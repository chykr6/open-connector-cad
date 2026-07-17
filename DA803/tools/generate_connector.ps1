param(
    [Parameter(Mandatory = $true)]
    [string]$Series,

    [Parameter(Mandatory = $true)]
    [double]$Pitch,

    [Parameter(Mandatory = $true)]
    [string]$Poles,

    [string]$BodyColor,
    [string]$CoverColor,
    [string]$SpacerColor,
    [string]$HousingColors,
    [string]$ActuatorColors,
    [string]$TerminalPinColor,
    [string]$Variant,
    [string]$OutputDir,
    [string]$FreeCADExe
)

$ErrorActionPreference = 'Stop'
$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$generator = Join-Path $toolsDir 'connector_generator.py'
. (Join-Path $toolsDir 'freecad_process.ps1')

# 优先使用显式参数，其次读取环境变量、PATH 和常见安装目录。
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
    series = $Series
    pitch = $Pitch
    poles = $Poles
    body_color = $BodyColor
    cover_color = $CoverColor
    spacer_color = $SpacerColor
    housing_colors = $HousingColors
    actuator_colors = $ActuatorColors
    terminal_pin_color = $TerminalPinColor
    variant = $Variant
    output_dir = $OutputDir
}

$env:CONNECTOR_REQUEST_JSON = $request | ConvertTo-Json -Compress
$env:CONNECTOR_AUTOCLOSE = '1'
try {
    $startedAt = [DateTime]::UtcNow
    $exitCode = Invoke-FreeCADProcess -Executable $freecad -Arguments @($generator)

    $pitchCode = ([int][math]::Round($Pitch * 100.0)).ToString('D3')
    $baseDir = if ($OutputDir) {
        [IO.Path]::GetFullPath($OutputDir)
    }
    else {
        Join-Path (Split-Path -Parent $toolsDir) "generated\$($Series.ToUpperInvariant())-$pitchCode"
    }
    $expected = foreach ($poleText in $Poles.Split(',')) {
        $poleCount = [int]$poleText.Trim()
        $stem = Get-ConnectorOutputStem -Series $Series -Pitch $Pitch -Poles $poleCount -Variant $Variant -ActuatorColors $ActuatorColors
        Join-Path $baseDir "$stem.FCStd"
        Join-Path $baseDir "$stem.step"
    }
    Assert-FreeCADArtifacts -ExitCode $exitCode -ExpectedPaths $expected -StartedAt $startedAt -Operation 'Connector generation'
}
finally {
    Remove-Item Env:CONNECTOR_REQUEST_JSON -ErrorAction SilentlyContinue
    Remove-Item Env:CONNECTOR_AUTOCLOSE -ErrorAction SilentlyContinue
}
