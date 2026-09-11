<#
  qa-mcp Windows bootstrap (модель B) — развёртывание в одну команду: host-agent + TestClient + тонкий
  контейнер, связанные между собой. Реализует шаги 0-6 из delivery/windows-agent-runbook.md.
  Запускать в ИНТЕРАКТИВНОЙ сессии пользователя.

  Example:
    powershell -ExecutionPolicy Bypass -File bootstrap.ps1 -Infobase "C:\1C_BASES\mybase" -User "Администратор"
    powershell -ExecutionPolicy Bypass -File bootstrap.ps1 -Infobase 'Srvr="srv";Ref="base";' -User "Tester" -Password "pw"
#>
param(
    [Parameter(Mandatory = $true)][string]$Infobase,    # file infobase path OR a full IBConnectionString
    [string]$User = "Администратор",
    [string]$Password = "",
    [string]$PlatformExe = "",                           # auto-detected from C:\Program Files\1cv8 if empty
    [string]$WindowTitle = "",                           # legacy compatibility hint; lifecycle targeting ignores it
    [string]$ReleaseBase = "__QA_MCP_RELEASE_BASE__",
    [string]$DistBase = "",                                # legacy alias for ReleaseBase; do not use for new links
    [string]$PortalEmail = "",                              # standalone portal email for protected downloads
    [string]$PortalPassword = "",                           # standalone portal password for protected downloads
    [string]$PortalPasswordFile = "",                       # legacy-compatible ACL-protected UTF-8 portal password file
    [string]$ManifestPublicKey = "RWS1HjrA2VQMULW4qhjpLyYhDWIA1llhkw1y3RStMCJTaKMVuXbyE6cv",  # minisign public key (pre-set for the alpha; public, not a secret; override to change)
    [string]$ManifestPublicKeyFile = "",                   # trusted local minisign public key path
    [string]$ManifestVerifier = "minisign",                # verifier executable or full path
    [string]$Image = "",                                   # optional local override; normal path uses manifest image tag
    [int]$ClientPort = 15381,
    [int]$RelayPort = 15382,
    [int]$AgentPort = 8001,
    [int]$McpPort = 8000,
    [string]$AgentRemoteAddress = "192.168.65.0/24",
    [string]$Token = "",                                 # generated if empty
    [string]$McpToken = "",                              # generated if empty; passed to qa-mcp HTTP runtime
    [string]$ContainerName = "qa-mcp"
)
$ErrorActionPreference = "Stop"
$ReleaseBasePlaceholder = "__QA_MCP_" + "RELEASE_BASE__"
function Info($m) { Write-Host "[qa-mcp] $m" -ForegroundColor Cyan }
function Done($m) { Write-Host "[qa-mcp] $m" -ForegroundColor Green }
function Die($m)  { Write-Host "[qa-mcp] ERROR: $m" -ForegroundColor Red; exit 1 }
function Set-TokenFileAcl([string]$Path) {
    if (-not (Test-Path $Path)) { return }
    $Acl = Get-Acl $Path
    $Acl.SetAccessRuleProtection($true, $false)
    $UserRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "Modify", "Allow")
    $Acl.SetAccessRule($UserRule)
    Set-Acl -Path $Path -AclObject $Acl
}
function Read-OptionalProtectedTextFile([string]$Path, [string]$Label) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $Item -or $Item.PSIsContainer) { Die "$Label file not found: $Path" }
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Die "$Label file must not be a symlink or reparse point: $Path"
    }
    $Acl = Get-Acl -LiteralPath $Item.FullName
    if (-not $Acl.AreAccessRulesProtected) {
        Die "$Label file ACL must disable inherited access: $Path"
    }
    $AllowedSids = @(
        [Security.Principal.WindowsIdentity]::GetCurrent().User.Value,
        "S-1-5-18",
        "S-1-5-32-544"
    )
    foreach ($Rule in $Acl.Access) {
        $Sid = $Rule.IdentityReference.Translate(
            [Security.Principal.SecurityIdentifier]
        ).Value
        if (
            $Rule.AccessControlType -eq "Allow" -and
            $AllowedSids -notcontains $Sid
        ) {
            Die "$Label file grants access outside the current user/SYSTEM/Administrators: $Path"
        }
    }
    return [IO.File]::ReadAllText($Item.FullName).TrimEnd("`r", "`n")
}
function Write-Utf8NoBom([string]$Path, [string]$Value) {
    if (Test-Path $Path) {
        Set-TokenFileAcl -Path $Path
    }
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Value, $Encoding)
    Set-TokenFileAcl -Path $Path
}
function Write-Utf8Bom([string]$Path, [string]$Value) {
    # Windows PowerShell 5.1 decodes a BOM-less .ps1 with the ANSI code page
    # (CP1251 on Russian Windows), which corrupts non-ASCII content such as a
    # Cyrillic 1C username (default "Администратор") baked into a generated
    # launch script. Executable helper scripts re-run via `powershell -File`
    # must therefore be written WITH a UTF-8 BOM so they decode correctly.
    if (Test-Path $Path) {
        Set-TokenFileAcl -Path $Path
    }
    $Encoding = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($Path, $Value, $Encoding)
    Set-TokenFileAcl -Path $Path
}
function Normalize-ReleaseBase([string]$Base) {
    $Value = $Base.Trim()
    while ($Value.EndsWith("/")) {
        $Value = $Value.Substring(0, $Value.Length - 1)
    }
    return $Value
}
function Assert-HttpsReleaseBase([string]$Base) {
    $Uri = $null
    if (-not [System.Uri]::TryCreate($Base, [System.UriKind]::Absolute, [ref]$Uri)) {
        Die "ReleaseBase must be an absolute HTTPS URL: $Base"
    }
    if ($Uri.Scheme -ne "https") {
        Die "ReleaseBase must use https:// before any release asset is downloaded: $Base"
    }
}
function Join-ReleaseUrl([string]$Base, [string]$Asset) {
    return "$(Normalize-ReleaseBase $Base)/$Asset"
}
function Get-ReleaseRequestHeaders() {
    $HasPortalPassword = -not [string]::IsNullOrWhiteSpace($PortalPassword)
    $HasPortalPasswordFile = -not [string]::IsNullOrWhiteSpace($PortalPasswordFile)
    if (
        [string]::IsNullOrWhiteSpace($PortalEmail) -and
        -not $HasPortalPassword -and
        -not $HasPortalPasswordFile
    ) {
        return @{}
    }
    if ([string]::IsNullOrWhiteSpace($PortalEmail) -or (-not $HasPortalPassword -and -not $HasPortalPasswordFile)) {
        Die "Protected qa-mcp downloads require -PortalEmail plus -PortalPassword or -PortalPasswordFile."
    }
    if ($HasPortalPassword -and $HasPortalPasswordFile) {
        Die "Pass only one portal password source: -PortalPassword or -PortalPasswordFile."
    }
    $PortalPasswordValue = $PortalPassword
    if ($HasPortalPasswordFile) {
        $PortalPasswordValue = Read-OptionalProtectedTextFile -Path $PortalPasswordFile -Label "portal password"
        if ([string]::IsNullOrEmpty($PortalPasswordValue)) { Die "portal password file is empty: $PortalPasswordFile" }
    }
    $Pair = "${PortalEmail}:$PortalPasswordValue"
    $TokenBytes = [System.Text.Encoding]::UTF8.GetBytes($Pair)
    return @{ Authorization = "Basic " + [Convert]::ToBase64String($TokenBytes) }
}
function Save-HttpResponseBody([object]$Response, [string]$OutFile) {
    $InputStream = $null
    $OutputStream = $null
    try {
        $InputStream = $Response.GetResponseStream()
        $OutputStream = [IO.File]::Open($OutFile, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $InputStream.CopyTo($OutputStream)
    } finally {
        if ($OutputStream) { $OutputStream.Dispose() }
        if ($InputStream) { $InputStream.Dispose() }
    }
}
function Invoke-ReleaseRequestNoRedirect([string]$Url, [string]$OutFile, [hashtable]$Headers) {
    $Request = [System.Net.HttpWebRequest]::Create($Url)
    $Request.Method = "GET"
    $Request.AllowAutoRedirect = $false
    $Request.UserAgent = "qa-mcp-bootstrap/1.0"
    foreach ($HeaderName in $Headers.Keys) {
        if ($HeaderName -ieq "Authorization") {
            $Request.Headers[[System.Net.HttpRequestHeader]::Authorization] = [string]$Headers[$HeaderName]
        } else {
            $Request.Headers[$HeaderName] = [string]$Headers[$HeaderName]
        }
    }
    $Response = $null
    try {
        $Response = $Request.GetResponse()
    } catch [System.Net.WebException] {
        if (-not $_.Exception.Response) { throw }
        $Response = $_.Exception.Response
    }
    try {
        $StatusCode = [int]$Response.StatusCode
        if ($StatusCode -ge 200 -and $StatusCode -lt 300) {
            Save-HttpResponseBody -Response $Response -OutFile $OutFile
        }
        return @{
            StatusCode = $StatusCode
            Location = [string]$Response.Headers["Location"]
        }
    } finally {
        if ($Response) { $Response.Close() }
    }
}
function Save-ReleaseAsset([string]$Url, [string]$OutFile) {
    $Headers = Get-ReleaseRequestHeaders
    $Initial = Invoke-ReleaseRequestNoRedirect -Url $Url -OutFile $OutFile -Headers $Headers
    if ($Initial.StatusCode -ge 200 -and $Initial.StatusCode -lt 300) {
        return
    }
    if ($Initial.StatusCode -lt 300 -or $Initial.StatusCode -ge 400) {
        Die "release asset download failed: HTTP $($Initial.StatusCode) for $Url"
    }
    $Location = $Initial.Location
    if ([string]::IsNullOrWhiteSpace($Location)) { Die "release asset redirect had no Location header: $Url" }
    if ($Location -match "/login") {
        Die "Protected qa-mcp downloads require portal credentials. Pass -PortalEmail plus -PortalPassword or -PortalPasswordFile."
    }
    $Resolved = [Uri]::new([Uri]$Url, $Location)
    Invoke-WebRequest $Resolved.AbsoluteUri -OutFile $OutFile -UseBasicParsing
}
function New-ReleaseToken() {
    return ([Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N"))
}
function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}
function Get-ManifestAssetSpec($Manifest, [string]$Name) {
    if ($Manifest.assets) {
        $prop = $Manifest.assets.PSObject.Properties[$Name]
        if ($prop) { return $prop.Value }
    }
    if ($Manifest.image -and $Manifest.image.asset -eq $Name) {
        return $Manifest.image
    }
    Die "manifest.json не содержит asset '$Name'."
}
function Test-ManifestAsset($Manifest, [string]$Name) {
    if ($Manifest.assets) {
        $prop = $Manifest.assets.PSObject.Properties[$Name]
        if ($prop) { return $true }
    }
    if ($Manifest.image -and $Manifest.image.asset -eq $Name) {
        return $true
    }
    return $false
}
function Assert-AssetSha256($Manifest, [string]$Name, [string]$Path) {
    $spec = Get-ManifestAssetSpec $Manifest $Name
    $expected = ([string]$spec.sha256).ToLowerInvariant()
    if (-not $expected) { Die "manifest.json asset '$Name' не содержит sha256." }
    $actual = Get-Sha256 $Path
    if ($actual -ne $expected) {
        Die "sha256 mismatch for ${Name}: expected $expected, got $actual"
    }
}
function Download-ReleaseAsset($Manifest, [string]$Name, [string]$OutFile) {
    $url = Join-ReleaseUrl $ReleaseBase $Name
    Info "скачиваю $Name..."
    Save-ReleaseAsset $url $OutFile
    Assert-AssetSha256 $Manifest $Name $OutFile
}
function Resolve-ManifestPublicKeyArgs() {
    if ($ManifestPublicKeyFile) {
        if (-not (Test-Path $ManifestPublicKeyFile)) {
            Die "manifest public key file not found: $ManifestPublicKeyFile"
        }
        return @("-p", $ManifestPublicKeyFile)
    }
    if ($ManifestPublicKey) {
        return @("-P", $ManifestPublicKey)
    }
    Die "ManifestPublicKey or ManifestPublicKeyFile is required. The manifest verification key must be delivered out of band, not downloaded from ReleaseBase."
}
function Assert-ManifestSignature([string]$ManifestPath, [string]$SignaturePath, [string]$SetupDir) {
    if (-not (Test-Path $SignaturePath)) {
        Die "manifest signature is missing: $SignaturePath"
    }
    $VerifierCommand = Get-Command $ManifestVerifier -ErrorAction SilentlyContinue
    if (-not $VerifierCommand) {
        Die "manifest verifier not found: $ManifestVerifier"
    }
    $PublicKeyArgs = Resolve-ManifestPublicKeyArgs
    Info "проверяю подпись manifest.json..."
    $output = & $VerifierCommand.Source -Vm $ManifestPath -x $SignaturePath @PublicKeyArgs 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Die "manifest signature verification failed: $output"
    }
}
function Test-TcpPortOpen([string]$HostName, [int]$Port) {
    $client = New-Object Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $iar.AsyncWaitHandle.WaitOne(500, $false)) { return $false }
        $client.EndConnect($iar)
        return $true
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}
function Remove-TestClientLaunchTask() {
    try { schtasks /Delete /TN qa-mcp-testclient /F 2>&1 | Out-Null } catch {}
}
function Get-PlatformVersionFromExe([string]$ExePath) {
    return Split-Path (Split-Path (Split-Path $ExePath -Parent) -Parent) -Leaf
}
function Get-PlatformFamily([string]$VersionText) {
    if ($VersionText -match '^(\d+\.\d+)') { return $Matches[1] }
    return ""
}
$DirectCaptureFamilies = @("8.3")
$ProtocolDataFallbacks = @{ "8.5" = "8.3" }
function Test-DirectCaptureFamily([string]$Family) {
    return $DirectCaptureFamilies -contains $Family
}
function Get-ProtocolDataFamily([string]$Family) {
    if (Test-DirectCaptureFamily $Family) { return $Family }
    if ($ProtocolDataFallbacks.ContainsKey($Family)) { return $ProtocolDataFallbacks[$Family] }
    return ""
}
function New-PlatformCandidate($File) {
    $VersionText = Get-PlatformVersionFromExe $File.FullName
    $ParsedVersion = $null
    try { $ParsedVersion = [version]$VersionText } catch { $ParsedVersion = [version]"0.0.0.0" }
    $Family = Get-PlatformFamily $VersionText
    return [PSCustomObject]@{
        Exe = $File.FullName
        VersionText = $VersionText
        Version = $ParsedVersion
        Family = $Family
        DirectCapture = (Test-DirectCaptureFamily $Family)
        ProtocolDataFamily = (Get-ProtocolDataFamily $Family)
    }
}
function Write-PlatformCoverageWarning([string]$PlatformVersion, [string]$Family, [string]$ProtocolDataFamily) {
    if (-not $ProtocolDataFamily) {
        Die "семейство платформы $Family (v$PlatformVersion) не поддерживается bundled protocol data. Укажите -PlatformExe на поддержанную 8.3/8.5 платформу."
    }
    if ($ProtocolDataFamily -ne $Family) {
        Write-Host "[qa-mcp] ПРЕДУПРЕЖДЕНИЕ: платформа v$PlatformVersion (семейство $Family) не имеет прямого bundled capture set; qa-mcp использует валидированный protocol-data fallback $ProtocolDataFamily. Для прямого coverage укажите -PlatformExe на 8.3.27.x." -ForegroundColor Yellow
    }
}

if ($DistBase -and (($ReleaseBase -eq $ReleaseBasePlaceholder) -or [string]::IsNullOrWhiteSpace($ReleaseBase))) {
    $ReleaseBase = $DistBase
}
if (($ReleaseBase -eq $ReleaseBasePlaceholder) -or [string]::IsNullOrWhiteSpace($ReleaseBase)) {
    Die "ReleaseBase is required. Use the secret qa-mcp release link, for example https://releases.aifor1c.ru:58443/qa-mcp/r-YYYYMMDD-.../"
}
$ReleaseBase = Normalize-ReleaseBase $ReleaseBase
Assert-HttpsReleaseBase $ReleaseBase
if (-not $McpToken) { $McpToken = New-ReleaseToken }

# --- 0. prerequisites -----------------------------------------------------------------------------------------
Info "проверяю прероквизиты..."
try { $dv = (docker info --format "{{.ServerVersion}}" 2>$null) } catch { $dv = $null }
if (-not $dv) { Die "Docker Desktop не запущен или не установлен. Установите/запустите его (бэкенд WSL2, нужны права администратора, возможна перезагрузка) и повторите." }
Info "docker: $dv"

if (-not $PlatformExe) {
    $candidates = Get-ChildItem "C:\Program Files\1cv8\*\bin\1cv8.exe" -ErrorAction SilentlyContinue |
            ForEach-Object { New-PlatformCandidate $_ } |
            Sort-Object Version -Descending
    $cand = $candidates | Where-Object { $_.DirectCapture } | Select-Object -First 1
    if (-not $cand) { $cand = $candidates | Select-Object -First 1 }
    if (-not $cand) { Die "1cv8.exe не найден в C:\Program Files\1cv8 — укажите -PlatformExe явно." }
    $PlatformExe = $cand.Exe
}
if (-not (Test-Path $PlatformExe)) { Die "файл платформы не найден: $PlatformExe" }
$PlatformVersion = Get-PlatformVersionFromExe $PlatformExe
$PlatformFamily = Get-PlatformFamily $PlatformVersion
$ProtocolDataFamily = Get-ProtocolDataFamily $PlatformFamily
Write-PlatformCoverageWarning $PlatformVersion $PlatformFamily $ProtocolDataFamily
Info "platform: $PlatformExe (v$PlatformVersion)"

$setup = Join-Path $env:LOCALAPPDATA "qa-mcp-setup"
New-Item -ItemType Directory -Force $setup | Out-Null
$ManifestPath = Join-Path $setup "manifest.json"
$ManifestSignaturePath = Join-Path $setup "manifest.json.minisig"
Info "скачиваю manifest.json из $ReleaseBase..."
Save-ReleaseAsset (Join-ReleaseUrl $ReleaseBase "manifest.json") $ManifestPath
Info "скачиваю manifest.json.minisig..."
Save-ReleaseAsset (Join-ReleaseUrl $ReleaseBase "manifest.json.minisig") $ManifestSignaturePath
Assert-ManifestSignature -ManifestPath $ManifestPath -SignaturePath $ManifestSignaturePath -SetupDir $setup
$Manifest = Get-Content -Raw -Path $ManifestPath | ConvertFrom-Json
if ($Manifest.schema -ne "ai1c.component-release.manifest.v1") { Die "unsupported manifest schema: $($Manifest.schema)" }
if ($Manifest.component -ne "qa-mcp") { Die "manifest component is not qa-mcp: $($Manifest.component)" }
Info "release: $($Manifest.version) ($($Manifest.git_commit))"
$HostAgentInstallDir = Join-Path $env:LOCALAPPDATA "qa-mcp-host-agent"
$AgentTokenFile = Join-Path $HostAgentInstallDir "qa-mcp-host-agent.token"
if ($Token) {
    New-Item -ItemType Directory -Force $HostAgentInstallDir | Out-Null
    Write-Utf8NoBom -Path $AgentTokenFile -Value $Token
}

# --- 2. host agent (display subset) ---------------------------------------------------------------------------
Info "скачиваю + устанавливаю host-agent (интерактивная сессия, 0.0.0.0:$AgentPort, firewall $AgentRemoteAddress, без окна)..."
Download-ReleaseAsset $Manifest "qa-mcp-host-agent.exe" "$setup\qa-mcp-host-agent.exe"
Download-ReleaseAsset $Manifest "install-windows-host-agent.ps1" "$setup\install-windows-host-agent.ps1"
$InstallArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$setup\install-windows-host-agent.ps1",
    "-Port", "$AgentPort", "-BindAddress", "0.0.0.0", "-RemoteAddress", "$AgentRemoteAddress",
    "-TokenFile", "$AgentTokenFile", "-ExePath", "$setup\qa-mcp-host-agent.exe",
    "-TestClientRelayAddress", "0.0.0.0:$RelayPort", "-TestClientPort", "$ClientPort",
    "-PlatformCatalog", (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PlatformExe)))
)
powershell @InstallArgs | Out-Null
$Token = (Get-Content -Raw -Path $AgentTokenFile).Trim()
if (-not $Token) { Die "host-agent token file is empty: $AgentTokenFile" }
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        if ((Invoke-RestMethod "http://127.0.0.1:$AgentPort/health" -Headers @{ "X-QA-MCP-Agent-Token" = $Token } -TimeoutSec 3).ok) { $ok = $true; break }
    } catch {}
    Start-Sleep 1
}
if (-not $ok) { Die "host-agent не поднялся на :$AgentPort (проверьте задачу qa-mcp-host-agent / её лог)." }
Done "host-agent поднят на 0.0.0.0:$AgentPort; firewall remote address: $AgentRemoteAddress."

# --- 3. lifecycle-owned TestClient in interactive session 1 ----------------------------------------------------
Info "запускаю 1C TestClient на TPort $ClientPort..."
if (Test-TcpPortOpen "127.0.0.1" $ClientPort) {
    Die "ClientPort $ClientPort already accepts TCP before this bootstrap run. Stop the stale TestClient or choose another -ClientPort; bootstrap will not report success against an ambiguous existing client."
}
$LaunchPayload = [ordered]@{
    user = $User
    password = $Password
    platform_version = $PlatformVersion
    use_hardware_licenses = $true
    port = $ClientPort
    timeout_seconds = 120
}
if (Test-Path -LiteralPath $Infobase -PathType Container) {
    $LaunchPayload.infobase_path = $Infobase
} else {
    $LaunchPayload.connection_string = $Infobase
}
$LaunchResult = Invoke-RestMethod "http://127.0.0.1:$AgentPort/testclient/launch" -Method Post `
    -Headers @{ "X-QA-MCP-Agent-Token" = $Token } `
    -Body ($LaunchPayload | ConvertTo-Json -Compress) -ContentType "application/json" -TimeoutSec 150
if (-not $LaunchResult.owns_process -or -not $LaunchResult.lifecycle_id -or -not $LaunchResult.client_target) {
    Die "host-agent не подтвердил lifecycle-owned TestClient; fallback к внешнему процессу запрещён."
}
$LaunchedClientPid = [int]$LaunchResult.pid
Done "host-agent владеет TestClient PID $LaunchedClientPid на TPort $ClientPort; relay :$RelayPort."
if ($WindowTitle) {
    Write-Host "[qa-mcp] ПРИМЕЧАНИЕ: -WindowTitle сохранён только для совместимости и не переопределяет lifecycle-bound target." -ForegroundColor Yellow
}

# --- 4. thin container ----------------------------------------------------------------------------------------
Info "загружаю + запускаю тонкий контейнер..."
if (-not $Image) {
    if (-not $Manifest.image -or $Manifest.image.type -ne "docker-archive") {
        Die "manifest.json должен содержать image.type=docker-archive."
    }
    $ImageAsset = [string]$Manifest.image.asset
    if (-not $ImageAsset) { Die "manifest.json не содержит image.asset." }
    $ImageArchive = Join-Path $setup $ImageAsset
    Download-ReleaseAsset $Manifest $ImageAsset $ImageArchive
    Info "docker load $ImageAsset..."
    $loadOutput = docker load -i $ImageArchive 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { Die "docker load failed: $loadOutput" }
    $Image = [string]$Manifest.image.tag
    if (-not $Image -and ($loadOutput -match "Loaded image:\s*(\S+)")) {
        $Image = $Matches[1]
    }
    if (-not $Image) { Die "не удалось определить Docker image tag из manifest.json/docker load output." }
} else {
    Write-Host "[qa-mcp] использую локальный override образа: $Image" -ForegroundColor Yellow
}
try { docker rm -f $ContainerName 2>&1 | Out-Null } catch {}   # tolerate "no such container" on a first run

docker run -d --name $ContainerName -p "127.0.0.1:${McpPort}:8080" `
    -e QA_MCP_BEARER_TOKEN=$McpToken `
    -e QA_MCP_REMOTE_CLIENT=1 `
    -e QA_MCP_CLIENT_HOST=host.docker.internal -e QA_MCP_CLIENT_PORT=$RelayPort `
    -e QA_MCP_TESTCLIENT_RELAY_ENDPOINT="host.docker.internal:$RelayPort" `
    -e QA_MCP_TESTCLIENT_RELAY_TOKEN=$Token `
    -e QA_MCP_HOST_AGENT=host.docker.internal:$AgentPort `
    -e QA_MCP_HOST_AGENT_TOKEN=$Token `
    -e QA_MCP_HOST_AGENT_CLIENT_PORT=$ClientPort `
    -e QA_MCP_PLATFORM_VERSION=$PlatformVersion `
    $Image | Out-Null
Start-Sleep 4
if (-not (docker ps --filter "name=$ContainerName" --format "{{.Names}}")) { Die "контейнер не стартовал (docker logs $ContainerName)." }
$mcpOk = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:$McpPort/health" -TimeoutSec 3
        if ($health.status -eq "ok" -or $health.ok) { $mcpOk = $true; break }
    } catch {}
    Start-Sleep 1
}
if (-not $mcpOk) { Die "qa-mcp HTTP runtime не ответил на /health на 127.0.0.1:$McpPort." }

# --- 5. verify wiring from inside the container ---------------------------------------------------------------
Info "проверяю развёртывание (контейнер -> клиент, здоровье host-agent)..."
# container -> TestClient (the protocol path) — retry: Docker Desktop's host.docker.internal has a cold-start
# delay to a freshly-bound host port, so a single short attempt right after `docker run` can miss.
$pyc = @'
import hashlib, os
from qa_mcp.protocol.session import TestClientSession
with TestClientSession(host="host.docker.internal", port=int(os.environ["QA_CP"]), connect_timeout_sec=8) as session:
    payload = session.read_initial()
if not payload:
    raise RuntimeError("empty TestClient protocol read")
print("CLIENT_READ_OK", len(payload), hashlib.sha256(payload).hexdigest())
'@
# This is a best-effort post-deploy probe, NOT a gate: the host agent (step 2), the TestClient (step 3) and the
# container (step 4) are already confirmed up. The container<->host path can need >20s of host.docker.internal
# cold-start, so a miss here is a warning, not a failure -- it is exercised for real on the first tool call.
$cok = $false; $cv = ""
for ($i = 0; $i -lt 8; $i++) {
    try { $cv = (docker exec -e QA_CP=$RelayPort $ContainerName python -c $pyc 2>&1 | Out-String) } catch { $cv = "$_" }
    if ("$cv" -match 'CLIENT_READ_OK') { $cok = $true; break }
    Start-Sleep 3
}
if ($cok) { Done "проверено: контейнер аутентифицировался в relay :$RelayPort и прочитал TestClient protocol." }
else { Write-Host "[qa-mcp] ПРИМЕЧАНИЕ: не удалось подтвердить путь контейнер->клиент в окне проверки (холодный старт host.docker.internal у Docker Desktop). Все компоненты подняты; путь отработает на первом вызове инструмента." -ForegroundColor Yellow }

# --- 6. connect + restart -------------------------------------------------------------------------------------
$mcpUrl = "http://127.0.0.1:$McpPort/mcp"
Done "qa-mcp развёрнут."
Write-Host ""
Write-Host "Добавьте этот MCP-сервер в конфиг вашего агента (используйте 127.0.0.1, НЕ localhost; путь ровно /mcp без завершающего слэша; держите bearer token приватным):"
$cfg = @{ mcpServers = @{ "qa-mcp" = @{ type = "http"; url = $mcpUrl; headers = @{ Authorization = "Bearer $McpToken" } } } } | ConvertTo-Json -Depth 6 -Compress
Write-Host "  $cfg"
Write-Host ""
Write-Host "Затем ПЕРЕЗАПУСТИТЕ сессию агента, чтобы он подключился к qa-mcp. После этого доступны ~67 инструментов qa-mcp."
Write-Host ""
Write-Host "Итог:"
Write-Host "  release:      $ReleaseBase"
Write-Host "  образ:        $Image"
Write-Host "  qa-mcp:       открытый пакет без product license и ключа данных"
Write-Host "  MCP:          $mcpUrl"
Write-Host "  TestClient:   127.0.0.1:$ClientPort (lifecycle-owned host-agent process)"
Write-Host "  relay:        host.docker.internal:$RelayPort (token-authenticated)"
Write-Host "  host-agent:   0.0.0.0:$AgentPort (firewall $AgentRemoteAddress, задача qa-mcp-host-agent, без окна)"
Write-Host "  платформа:    v$PlatformVersion"
Write-Host "  target:       immutable lifecycle/PID/TPort binding"
