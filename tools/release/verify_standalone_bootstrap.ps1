param(
    [Parameter(Mandatory = $true)][string]$Path
)
$ErrorActionPreference = "Stop"
$ParseErrors = $null
$Tokens = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $Path,
    [ref]$Tokens,
    [ref]$ParseErrors
)
if ($ParseErrors.Count -ne 0) {
    $Messages = ($ParseErrors | ForEach-Object { $_.Message }) -join "; "
    throw "standalone bootstrap parse failed: $Messages"
}
$ParameterNames = @(
    $Ast.ParamBlock.Parameters |
        ForEach-Object { $_.Name.VariablePath.UserPath }
)
foreach ($Required in @(
    "PasswordFile"
)) {
    if ($ParameterNames -notcontains $Required) {
        throw "standalone bootstrap lacks protected parameter $Required"
    }
}
$RetiredDataKeyParameter = "Bundled" + "DataKey"
foreach ($Forbidden in @("Password", "LicenseKey", $RetiredDataKeyParameter, "${RetiredDataKeyParameter}File", "LicenseKeyFile")) {
    if ($ParameterNames -contains $Forbidden) {
        throw "standalone bootstrap exposes forbidden plain parameter $Forbidden"
    }
}
$Content = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path))
foreach ($RequiredText in @(
    "Read-ProtectedInputFile",
    "-e QA_MCP_BEARER_TOKEN=`$McpToken",
    "qa-mcp HTTP runtime"
)) {
    if (-not $Content.Contains($RequiredText)) {
        throw "standalone bootstrap lacks contract marker: $RequiredText"
    }
}
foreach ($ForbiddenText in @(
    "AI1C-QAMCP-ALPHA-C19884D77AEA7A6B",
    "Q4dfh5lyk8HIRJccxVeEW4vn+B11fMxCdAItw6VsGFE=",
    "QA_MCP_LICENSE_",
    "AI1C_LICENSE_",
    "AI1C_MCP_PROXY_HTTP_TOKEN",
    "ai-mcp-proxy",
    "ai1c-license",
    "Обычно предустановлен"
)) {
    if ($Content.Contains($ForbiddenText)) {
        throw "standalone bootstrap contains retired embedded-material marker"
    }
}
Write-Output "standalone bootstrap Windows-native contract OK"
