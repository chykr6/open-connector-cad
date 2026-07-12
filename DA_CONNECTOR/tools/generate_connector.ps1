param(
    [Parameter(Mandatory = $true)]
    [string]$Series,

    [Parameter(Mandatory = $true)]
    [double]$Pitch,

    [Parameter(Mandatory = $true)]
    [string]$Poles,

    [string]$BodyColor,
    [string]$CoverColor,
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
    housing_colors = $HousingColors
    actuator_colors = $ActuatorColors
    terminal_pin_color = $TerminalPinColor
    variant = $Variant
    output_dir = $OutputDir
}

$env:CONNECTOR_REQUEST_JSON = $request | ConvertTo-Json -Compress
$env:CONNECTOR_AUTOCLOSE = '1'
try {
    & $freecad $generator
    # FreeCAD GUI 在部分 Windows 会话中正常关闭时不返回数值退出码；
    # 只有明确返回非零整数时才判定为失败，产物完整性由验证器负责确认。
    if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Connector generation failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:CONNECTOR_REQUEST_JSON -ErrorAction SilentlyContinue
    Remove-Item Env:CONNECTOR_AUTOCLOSE -ErrorAction SilentlyContinue
}
