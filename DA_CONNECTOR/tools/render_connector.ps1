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
. (Join-Path $toolsDir 'freecad_process.ps1')

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
    $startedAt = [DateTime]::UtcNow
    $exitCode = Invoke-FreeCADProcess -Executable $freecad -Arguments @($renderer)
    $modelPath = [IO.Path]::GetFullPath($Model)
    $outputPath = if ($Output) {
        [IO.Path]::GetFullPath($Output)
    }
    else {
        [IO.Path]::ChangeExtension($modelPath, '.png')
    }
    Assert-FreeCADArtifacts -ExitCode $exitCode -ExpectedPaths @($outputPath) -StartedAt $startedAt -Operation 'Connector render'
}
finally {
    Remove-Item Env:CONNECTOR_RENDER_REQUEST_JSON -ErrorAction SilentlyContinue
    Remove-Item Env:CONNECTOR_AUTOCLOSE -ErrorAction SilentlyContinue
}
