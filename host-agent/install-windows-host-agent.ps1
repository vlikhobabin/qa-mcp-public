param(
    [int]$Port = 8001,
    # Safe default for native/local use. Model-B Docker Desktop deployments must opt in to 0.0.0.0 and keep the
    # firewall scoped with -RemoteAddress, for example 192.168.65.0/24 on Docker Desktop.
    [string]$BindAddress = "127.0.0.1",
    [string]$RemoteAddress = "192.168.65.0/24",
    [switch]$AllowUnsafeLan,
    [string]$Token = "",
    [string]$TokenFile = "",
    [string]$AllowedOrigins = "",
    [string]$InstallDir = "$env:LOCALAPPDATA\qa-mcp-host-agent",
    [string]$TaskName = "qa-mcp-host-agent",
    [string]$ExePath = "",
    [switch]$Uninstall,
    # Optional authenticated raw protocol relay. Use this when qa-mcp runs on
    # another LAN machine; the relay authenticates with the same token and
    # dials only the fixed loopback TestClient port.
    [string]$TestClientRelayAddress = "",
    [int]$TestClientPort = 15381,
    # Platform catalog used only to resolve the fixed TestClient lifecycle executable.
    [string]$PlatformCatalog = "C:\Program Files\1cv8"
)

$ErrorActionPreference = "Stop"

$TokenLoadedFromExistingFile = $false
if ([string]::IsNullOrWhiteSpace($TokenFile)) {
    $TokenFile = Join-Path $InstallDir "qa-mcp-host-agent.token"
}
if ([string]::IsNullOrWhiteSpace($Token)) {
    if (Test-Path $TokenFile) {
        $Token = (Get-Content -Raw -Path $TokenFile).Trim()
        $TokenLoadedFromExistingFile = $true
        Write-Host "Using existing QA_MCP host-agent token file."
    } else {
        $Token = [Guid]::NewGuid().ToString("N")
        Write-Host "Generated a new QA_MCP host-agent token and stored it in the token file."
    }
}
if ($Token -match "\s") {
    throw "Token must not contain whitespace."
}
function Set-TokenFileAcl([string]$Path) {
    if (-not (Test-Path $Path)) { return }
    $Item = Get-Item -LiteralPath $Path
    if ($Item.PSIsContainer) {
        $Acl = New-Object System.Security.AccessControl.DirectorySecurity
    } else {
        $Acl = New-Object System.Security.AccessControl.FileSecurity
    }
    $Acl.SetAccessRuleProtection($true, $false)
    $CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $AllowedPrincipals = @(
        [ordered]@{ Sid = $CurrentUser; Rights = [System.Security.AccessControl.FileSystemRights]::Modify },
        [ordered]@{ Sid = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-18"); Rights = [System.Security.AccessControl.FileSystemRights]::FullControl },
        [ordered]@{ Sid = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-32-544"); Rights = [System.Security.AccessControl.FileSystemRights]::FullControl }
    )
    foreach ($Principal in $AllowedPrincipals) {
        if ($Item.PSIsContainer) {
            $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $Principal.Sid,
                $Principal.Rights,
                ([System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit),
                [System.Security.AccessControl.PropagationFlags]::None,
                [System.Security.AccessControl.AccessControlType]::Allow
            )
        } else {
            $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $Principal.Sid,
                $Principal.Rights,
                [System.Security.AccessControl.AccessControlType]::Allow
            )
        }
        $Acl.AddAccessRule($Rule) | Out-Null
    }
    Set-Acl -LiteralPath $Path -AclObject $Acl
}
function Write-Utf8NoBom([string]$Path, [string]$Value) {
    if (Test-Path $Path) {
        Set-TokenFileAcl -Path $Path
    }
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Value, $Encoding)
}
function Get-SecretSafeSha256([string]$Value) {
    $Sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $Sha.Dispose()
    }
}
function Get-FileSha256OrEmpty([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return ""
    }
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}
function Normalize-CommandText([string]$Value) {
    return (($Value -replace "\s+", " ").Trim())
}
function Test-HostAgentCommandLineMatches([string]$CommandLine, [string]$ExecutablePath, [string]$Arguments) {
    $NormalizedCommand = Normalize-CommandText $CommandLine
    $NormalizedArguments = Normalize-CommandText $Arguments
    $QuotedCommand = Normalize-CommandText ("`"$ExecutablePath`" $Arguments")
    $UnquotedCommand = Normalize-CommandText ("$ExecutablePath $Arguments")
    return (
        $NormalizedCommand.Equals($QuotedCommand, [System.StringComparison]::OrdinalIgnoreCase) -or
        $NormalizedCommand.Equals($UnquotedCommand, [System.StringComparison]::OrdinalIgnoreCase) -or
        $NormalizedCommand.EndsWith(" " + $NormalizedArguments, [System.StringComparison]::OrdinalIgnoreCase)
    )
}
function Get-OwnedHostAgentProcessCommandLine([string]$ExecutablePath) {
    $Rows = @()
    $Expected = ""
    try {
        $Expected = [System.IO.Path]::GetFullPath($ExecutablePath)
    } catch {
        $Expected = $ExecutablePath
    }
    foreach ($Process in @(Get-CimInstance Win32_Process -Filter "Name = 'qa-mcp-host-agent.exe'" -ErrorAction SilentlyContinue)) {
        $Candidate = [string]$Process.ExecutablePath
        if ([string]::IsNullOrWhiteSpace($Candidate)) { continue }
        try {
            $Candidate = [System.IO.Path]::GetFullPath($Candidate)
        } catch {}
        if ($Candidate.Equals($Expected, [System.StringComparison]::OrdinalIgnoreCase)) {
            $Rows += [string]$Process.CommandLine
        }
    }
    return $Rows
}
function Copy-HostAgentArtifacts([bool]$CopyHostAgent) {
    if ($CopyHostAgent) {
        Copy-Item -Force $ExePath $TargetExe
    }
    # Files copied from an SSH/SCP staging directory can carry only the transient
    # logon SID. Rebind the staged executable to the persistent current-user ACL
    # before Task Scheduler starts it under a new InteractiveToken logon session.
    if (Test-Path -LiteralPath $TargetExe -PathType Leaf) {
        Set-TokenFileAcl -Path $TargetExe
    }
}
function Test-LoopbackBind([string]$Address) {
    $normalized = $Address.Trim().ToLowerInvariant()
    return $normalized -eq "127.0.0.1" -or $normalized -eq "localhost" -or $normalized -eq "::1"
}
function Get-InstalledTestClientRelayPort([string]$EnvFile, [string]$RequestedAddress) {
    $RelayAddress = $RequestedAddress
    if ([string]::IsNullOrWhiteSpace($RelayAddress) -and (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
        $RelayLine = @(Get-Content -LiteralPath $EnvFile -ErrorAction SilentlyContinue | Where-Object {
            $_ -match '^QA_MCP_TESTCLIENT_RELAY_ADDR='
        } | Select-Object -First 1)
        if ($RelayLine.Count -eq 1) {
            $RelayAddress = ([string]$RelayLine[0]).Substring('QA_MCP_TESTCLIENT_RELAY_ADDR='.Length)
        }
    }
    if ($RelayAddress -match ':(?<port>\d+)$') {
        return [int]$Matches.port
    }
    return 0
}
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptRoot
$TargetExe = Join-Path $InstallDir "qa-mcp-host-agent.exe"
$EnvFile = Join-Path $InstallDir "qa-mcp-host-agent.env"
if ($Uninstall) {
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        $OwnedAction = @(@($ExistingTask.Actions) | Where-Object {
            [string]::Equals([string]$_.Execute, $TargetExe, [System.StringComparison]::OrdinalIgnoreCase)
        })
        if ($OwnedAction.Count -ne 1) {
            throw "Refusing to uninstall task '$TaskName': its executable is not the owned bridge path."
        }
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { try { $_.Path -eq $TargetExe } catch { $false } } |
            Stop-Process -Force -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    Get-NetFirewallRule -DisplayName "qa-mcp host agent $Port" -ErrorAction SilentlyContinue |
        Remove-NetFirewallRule -ErrorAction SilentlyContinue
    $OwnedRelayPort = Get-InstalledTestClientRelayPort -EnvFile $EnvFile -RequestedAddress $TestClientRelayAddress
    if ($OwnedRelayPort -gt 0) {
        Get-NetFirewallRule -DisplayName "qa-mcp TestClient relay $OwnedRelayPort" -ErrorAction SilentlyContinue |
            Remove-NetFirewallRule -ErrorAction SilentlyContinue
    }
    foreach ($OwnedFile in @($TargetExe, $TokenFile, (Join-Path $InstallDir "qa-mcp-host-agent.env"), (Join-Path $InstallDir "qa-mcp-host-agent.log"))) {
        Remove-Item -LiteralPath $OwnedFile -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $InstallDir -Force -ErrorAction SilentlyContinue
    Write-Host "Uninstalled owned qa-mcp host bridge task and files."
    return
}
if (-not [string]::IsNullOrWhiteSpace($PlatformCatalog) -and -not (Test-Path $PlatformCatalog)) {
    Write-Warning "Platform catalog was not found: $PlatformCatalog. TestClient launch will fail closed until it is corrected."
}
if ([string]::IsNullOrWhiteSpace($ExePath)) {
    throw "ExePath is required. Use the verified executable from the signed release bootstrap or build a source-bound bundle on Linux with bin/ai-build-windows-host-agent."
}
if (-not (Test-Path $ExePath)) {
    throw "Host-agent executable not found: $ExePath. Use the signed release bootstrap or bin/ai-build-windows-host-agent; do not use an ignored checkout-adjacent executable."
}
if ($TestClientPort -lt 1 -or $TestClientPort -gt 65535) {
    throw "TestClientPort must be between 1 and 65535."
}
$TestClientRelayPort = 0
if (-not [string]::IsNullOrWhiteSpace($TestClientRelayAddress)) {
    if ($TestClientRelayAddress -notmatch '^(?<host>[^:]+):(?<port>\d+)$') {
        throw "TestClientRelayAddress must use host:port form, for example 0.0.0.0:15382."
    }
    $TestClientRelayPort = [int]$Matches.port
    if ($TestClientRelayPort -lt 1 -or $TestClientRelayPort -gt 65535) {
        throw "TestClientRelayAddress port must be between 1 and 65535."
    }
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$TokenParent = Split-Path -Parent $TokenFile
if (-not [string]::IsNullOrWhiteSpace($TokenParent)) {
    New-Item -ItemType Directory -Force -Path $TokenParent | Out-Null
}
$LogFile = Join-Path $InstallDir "qa-mcp-host-agent.log"
$InstalledHostAgentSha = Get-FileSha256OrEmpty -Path $TargetExe
$DesiredHostAgentSha = Get-FileSha256OrEmpty -Path $ExePath
$InstalledTokenSha = Get-FileSha256OrEmpty -Path $TokenFile
$DesiredTokenSha = Get-SecretSafeSha256 -Value $Token
try {
    Write-Utf8NoBom -Path $TokenFile -Value $Token
    Set-TokenFileAcl -Path $TokenFile
} catch {
    if ($TokenLoadedFromExistingFile -and (Test-Path $TokenFile)) {
        Write-Warning "Existing token file could not be rewritten; preserving it: $($_.Exception.Message)"
    } else {
        throw
    }
}
@(
    "QA_MCP_HOST_AGENT_ADDR=${BindAddress}:$Port",
    "QA_MCP_HOST_AGENT_TOKEN_FILE=$TokenFile",
    "QA_MCP_HOST_AGENT_ALLOWED_ORIGINS=$AllowedOrigins",
    "QA_MCP_PLATFORM_CATALOG=$PlatformCatalog",
    "QA_MCP_HOST_AGENT_LOG=$LogFile"
    "QA_MCP_TESTCLIENT_RELAY_ADDR=$TestClientRelayAddress"
    "QA_MCP_TESTCLIENT_RELAY_TARGET_PORT=$TestClientPort"
) | Set-Content -Encoding UTF8 -Path $EnvFile

# The agent is built windowless (`-ldflags -H windowsgui`) so the task does not pop a console window; -log keeps
# its output (it has no console to print to).
$ActionArgs = @("-addr", "${BindAddress}:$Port", "-token-file", "`"$TokenFile`"", "-log", "`"$LogFile`"")
if (-not [string]::IsNullOrWhiteSpace($TestClientRelayAddress)) {
    $ActionArgs += @(
        "-testclient-relay-addr", $TestClientRelayAddress,
        "-testclient-relay-target-port", [string]$TestClientPort
    )
}
if (-not [string]::IsNullOrWhiteSpace($AllowedOrigins)) {
    $ActionArgs += @("-allowed-origin", "`"$AllowedOrigins`"")
}
if (-not [string]::IsNullOrWhiteSpace($PlatformCatalog)) {
    $ActionArgs += @("-platform-catalog", "`"$PlatformCatalog`"")
}
$DesiredActionArguments = $ActionArgs -join " "
$Action = New-ScheduledTaskAction -Execute $TargetExe -Argument $DesiredActionArguments
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
$OwnedHostAgentCommandLines = @(Get-OwnedHostAgentProcessCommandLine -ExecutablePath $TargetExe)
$RestartReasons = @()
$CopyHostAgentArtifact = $InstalledHostAgentSha -ne $DesiredHostAgentSha
if ($CopyHostAgentArtifact) { $RestartReasons += "host-agent-artifact-drift" }
if ($InstalledTokenSha -ne $DesiredTokenSha) { $RestartReasons += "token-file-drift" }
if (-not $ExistingTask) {
    $RestartReasons += "task-missing"
} else {
    $ExistingActions = @($ExistingTask.Actions)
    if ($ExistingActions.Count -ne 1) {
        $RestartReasons += "task-action-drift"
    } else {
        $ExistingAction = $ExistingActions[0]
        if (
            -not ([string]$ExistingAction.Execute).Equals($TargetExe, [System.StringComparison]::OrdinalIgnoreCase) -or
            (Normalize-CommandText ([string]$ExistingAction.Arguments)) -ne (Normalize-CommandText $DesiredActionArguments)
        ) {
            $RestartReasons += "task-action-drift"
        }
    }
    if ($OwnedHostAgentCommandLines.Count -eq 0) {
        $RestartReasons += "process-not-running"
    } else {
        $RunningMatch = $false
        foreach ($CommandLine in $OwnedHostAgentCommandLines) {
            if (Test-HostAgentCommandLineMatches -CommandLine $CommandLine -ExecutablePath $TargetExe -Arguments $DesiredActionArguments) {
                $RunningMatch = $true
                break
            }
        }
        if (-not $RunningMatch) {
            $RestartReasons += "running-process-arguments-drift"
        }
    }
}
$DesiredProfilePayload = [ordered]@{
    task_name = $TaskName
    executable = $TargetExe
    arguments = $DesiredActionArguments
    host_agent_sha256 = $DesiredHostAgentSha
    token_file_sha256 = $DesiredTokenSha
}
$DesiredProfileFingerprint = Get-SecretSafeSha256 -Value ($DesiredProfilePayload | ConvertTo-Json -Compress -Depth 4)
$RestartReasons = @($RestartReasons | Select-Object -Unique)
$RestartRequired = $RestartReasons.Count -gt 0
if ($RestartRequired) {
    Write-Host "Host-agent restart required: $($RestartReasons -join ', '); desired profile $($DesiredProfileFingerprint.Substring(0, 12))"
    if ($ExistingTask) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { try { $_.Path -eq $TargetExe } catch { $false } } |
        Stop-Process -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "Host-agent restart skipped: running task already matches desired profile $($DesiredProfileFingerprint.Substring(0, 12))"
}
Copy-HostAgentArtifacts -CopyHostAgent $CopyHostAgentArtifact
if ($RestartRequired) {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null
}

$RuleName = "qa-mcp host agent $Port"
try {
    if (Test-LoopbackBind $BindAddress) {
        Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
    } else {
        if ($AllowUnsafeLan) {
            $FirewallRemoteAddress = "Any"
            Write-Warning "Creating an all-remote firewall rule for ${BindAddress}:$Port because -AllowUnsafeLan was supplied."
        } else {
            if ([string]::IsNullOrWhiteSpace($RemoteAddress)) {
                throw "RemoteAddress is required for non-loopback bind. Use a Docker Desktop subnet such as 192.168.65.0/24, or pass -AllowUnsafeLan explicitly."
            }
            $FirewallRemoteAddress = $RemoteAddress
        }
        Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName $RuleName -Direction Inbound -LocalPort $Port -Protocol TCP -Action Allow -RemoteAddress $FirewallRemoteAddress | Out-Null
    }
} catch {
    Write-Warning "Firewall rule was not created: $($_.Exception.Message)"
}
if ($TestClientRelayPort -gt 0) {
    $RelayRuleName = "qa-mcp TestClient relay $TestClientRelayPort"
    try {
        Get-NetFirewallRule -DisplayName $RelayRuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
        $RelayRemoteAddress = if ($AllowUnsafeLan) { "Any" } else { $RemoteAddress }
        if ([string]::IsNullOrWhiteSpace($RelayRemoteAddress)) {
            throw "RemoteAddress is required for the TestClient relay firewall rule."
        }
        New-NetFirewallRule -DisplayName $RelayRuleName -Direction Inbound -LocalPort $TestClientRelayPort `
            -Protocol TCP -Action Allow -RemoteAddress $RelayRemoteAddress | Out-Null
    } catch {
        Write-Warning "TestClient relay firewall rule was not created: $($_.Exception.Message)"
    }
}

if ($RestartRequired) {
    Start-ScheduledTask -TaskName $TaskName
}

Write-Host "Installed qa-mcp host agent:"
Write-Host "  exe: $TargetExe"
Write-Host "  task: $TaskName"
Write-Host "  bind: ${BindAddress}:$Port"
Write-Host "  platform catalog: $PlatformCatalog"
if (Test-LoopbackBind $BindAddress) {
    Write-Host "  agent: 127.0.0.1:$Port"
} else {
    Write-Host "  agent: host.docker.internal:$Port"
    Write-Host "  firewall remote address: $FirewallRemoteAddress"
}
Write-Host "  log: $LogFile"
Write-Host "  token file: $TokenFile"
if ($TestClientRelayPort -gt 0) {
    Write-Host "  authenticated TestClient relay: $TestClientRelayAddress -> 127.0.0.1:$TestClientPort"
}
Write-Host "Container env:"
Write-Host "  QA_MCP_HOST_AGENT=host.docker.internal:$Port"
Write-Host "  QA_MCP_HOST_AGENT_TOKEN=(read the token from $TokenFile)"
if ($TestClientRelayPort -gt 0) {
    Write-Host "  QA_MCP_CLIENT_HOST=host.docker.internal"
    Write-Host "  QA_MCP_CLIENT_PORT=$TestClientRelayPort"
    Write-Host "  QA_MCP_HOST_AGENT_CLIENT_PORT=$TestClientPort"
    Write-Host "  QA_MCP_TESTCLIENT_RELAY_ENDPOINT=host.docker.internal:$TestClientRelayPort"
    Write-Host "  QA_MCP_TESTCLIENT_RELAY_TOKEN=(same token from $TokenFile)"
}
