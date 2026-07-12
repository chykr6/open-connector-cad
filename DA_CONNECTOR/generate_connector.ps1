param(
    [Parameter(Mandatory = $true)]
    [string]$Series,

    [Parameter(Mandatory = $true)]
    [double]$Pitch,

    [Parameter(Mandatory = $true)]
    [string]$Poles,

    [string]$BodyColor,
    [string]$ActuatorColors,
    [string]$TerminalPinColor,
    [string]$Variant,
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'
$connectorDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$generator = Join-Path $connectorDir 'connector_generator.py'
$freecad = 'D:\destool\FreeCAD\bin\freecad.exe'

if (-not (Test-Path -LiteralPath $freecad)) {
    throw "FreeCAD executable not found: $freecad"
}

$request = @{
    series = $Series
    pitch = $Pitch
    poles = $Poles
    body_color = $BodyColor
    actuator_colors = $ActuatorColors
    terminal_pin_color = $TerminalPinColor
    variant = $Variant
    output_dir = $OutputDir
}

$env:CONNECTOR_REQUEST_JSON = $request | ConvertTo-Json -Compress
$env:CONNECTOR_AUTOCLOSE = '1'
try {
    & $freecad $generator
    if ($LASTEXITCODE -ne 0) {
        throw "Connector generation failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:CONNECTOR_REQUEST_JSON -ErrorAction SilentlyContinue
    Remove-Item Env:CONNECTOR_AUTOCLOSE -ErrorAction SilentlyContinue
}

