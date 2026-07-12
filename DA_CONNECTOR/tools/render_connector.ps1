param(
    [Parameter(Mandatory = $true)]
    [string]$Model,

    [string]$Output,
    [int]$Width = 1200,
    [int]$Height = 900,
    [string]$FreeCADExe
)

$ErrorActionPreference = 'Stop'
$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$renderer = Join-Path $toolsDir 'connector_render.py'

$candidates = @(
    $FreeCADExe,
    $env:FREECAD_EXE,
    (Get-Command freecad.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source),
    (Join-Path $env:ProgramFiles 'FreeCAD 1.0\bin\FreeCAD.exe'),
    (Join-Path $env:ProgramFiles 'FreeCAD 0.21\bin\FreeCAD.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$freecad = $candidates | Select-Object -First 1
if (-not $freecad) {
    throw 'FreeCAD executable not found. Pass -FreeCADExe or set FREECAD_EXE.'
}

$request = @{
    model = $Model
    output = $Output
    width = $Width
    height = $Height
}

$env:CONNECTOR_RENDER_REQUEST_JSON = $request | ConvertTo-Json -Compress
$env:CONNECTOR_AUTOCLOSE = '1'
try {
    & $freecad $renderer
    if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Connector render failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:CONNECTOR_RENDER_REQUEST_JSON -ErrorAction SilentlyContinue
    Remove-Item Env:CONNECTOR_AUTOCLOSE -ErrorAction SilentlyContinue
}
