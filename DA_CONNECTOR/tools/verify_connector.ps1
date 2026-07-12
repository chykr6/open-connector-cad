param(
    [Parameter(Mandatory = $true)]
    [string]$Model,

    [string]$Step,
    [string]$FreeCADPython
)

$ErrorActionPreference = 'Stop'
$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$verifier = Join-Path $toolsDir 'connector_verify.py'

$fromFreeCADExe = $null
if ($env:FREECAD_EXE) {
    $fromFreeCADExe = Join-Path (Split-Path -Parent $env:FREECAD_EXE) 'python.exe'
}

$candidates = @(
    $FreeCADPython,
    $env:FREECAD_PYTHON,
    $fromFreeCADExe,
    (Join-Path $env:ProgramFiles 'FreeCAD 1.0\bin\python.exe'),
    (Join-Path $env:ProgramFiles 'FreeCAD 0.21\bin\python.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$python = $candidates | Select-Object -First 1
if (-not $python) {
    throw 'FreeCAD Python not found. Pass -FreeCADPython or set FREECAD_PYTHON.'
}

$arguments = @($verifier, $Model)
if ($Step) {
    $arguments += @('--step', $Step)
}

& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Connector verification failed with exit code $LASTEXITCODE"
}

