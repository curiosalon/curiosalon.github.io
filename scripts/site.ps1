param(
    [ValidateSet('Preview', 'Build')]
    [string]$Action = 'Preview',
    [ValidateRange(1024, 65535)]
    [int]$Port = 4000
)
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path $PSScriptRoot -Parent
$rubyCommand = Get-Command ruby.exe -ErrorAction SilentlyContinue
$rubyPath = if ($rubyCommand) { $rubyCommand.Source } else {
    Join-Path $env:LOCALAPPDATA 'Programs\Ruby34\bin\ruby.exe'
}
if (-not (Test-Path -LiteralPath $rubyPath)) {
    throw 'Ruby was not found. Install Ruby 3.4 with DevKit, then reopen PowerShell.'
}
$rubyBin = Split-Path $rubyPath -Parent
$previousPath = $env:Path
$previousEnvironment = $env:JEKYLL_ENV
Push-Location $siteRoot
try {
    $env:Path = "$rubyBin;$previousPath"
    $bundlePath = Join-Path $rubyBin 'bundle'
    & $rubyPath $bundlePath check
    if ($LASTEXITCODE -ne 0) {
        throw 'Dependencies are missing. In this folder, run bundle install using a Ruby command prompt.'
    }
    if ($Action -eq 'Build') {
        $env:JEKYLL_ENV = 'production'
        & $rubyPath $bundlePath exec jekyll build --trace
    } else {
        $env:JEKYLL_ENV = 'development'
        Write-Host "Preview: http://127.0.0.1:$Port (Ctrl+C to stop). This does not publish."
        & $rubyPath $bundlePath exec jekyll serve --host 127.0.0.1 --port $Port
    }
    if ($LASTEXITCODE -ne 0) { throw "Jekyll exited with code $LASTEXITCODE." }
} finally {
    $env:Path = $previousPath
    $env:JEKYLL_ENV = $previousEnvironment
    Pop-Location
}
