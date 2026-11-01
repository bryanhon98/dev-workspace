param(
    [Parameter(Mandatory=$true, Position=0)][string]$Source,
    [string]$Question = ''
)
$ErrorActionPreference = 'Stop'
$watchTools = Join-Path $env:USERPROFILE 'Documents/Codex/tools/watch'
$watchSkill = Join-Path $env:USERPROFILE '.codex/skills/watch'
$watchPython = Join-Path $watchTools 'python/Scripts/python.exe'
$savedPath = $env:PATH
try {
    $env:PATH = "$watchTools/bin;$watchTools/python/Scripts;$savedPath"
    $watchOptions = @((Join-Path $watchSkill 'scripts/watch.py'), $Source, '--engine', 'local', '--no-whisper', '--detail', 'balanced')
    if ($Question) { $watchOptions += @('--question', $Question) }
    & $watchPython @watchOptions
    $watchExitCode = $LASTEXITCODE
} finally {
    $env:PATH = $savedPath
}
exit $watchExitCode
