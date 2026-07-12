$ErrorActionPreference = 'Stop'

$connectorDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$helper = Join-Path $connectorDir 'tools\freecad_process.ps1'
. $helper

$tempDir = Join-Path ([IO.Path]::GetTempPath()) ('freecad-process-' + [Guid]::NewGuid())
New-Item -ItemType Directory -Path $tempDir | Out-Null
try {
    $derivedStem = Get-ConnectorOutputStem `
        -Series 'DA803' `
        -Pitch 3.5 `
        -Poles 2 `
        -ActuatorColors 'black,blue'
    if ($derivedStem -ne 'DA803-350-2P-black-blue') {
        throw "derived output stem mismatch: $derivedStem"
    }
    $plainStem = Get-ConnectorOutputStem `
        -Series 'DA803' `
        -Pitch 3.5 `
        -Poles 2 `
        -ActuatorColors 'black'
    if ($plainStem -ne 'DA803-350-2P') {
        throw "plain output stem mismatch: $plainStem"
    }

    $exitScript = Join-Path $tempDir 'exit-one.ps1'
    Set-Content -LiteralPath $exitScript -Value 'exit 1'
    $pwsh = (Get-Process -Id $PID).Path
    $isolatedExitCode = Invoke-FreeCADProcess `
        -Executable $pwsh `
        -Arguments @('-NoProfile', '-File', $exitScript)
    if ($isolatedExitCode -ne 1) {
        throw "isolated process exit code mismatch: $isolatedExitCode"
    }

    $startedAt = [DateTime]::UtcNow.AddSeconds(-1)
    $fresh = Join-Path $tempDir 'fresh.FCStd'
    Set-Content -LiteralPath $fresh -Value 'model'

    $global:LASTEXITCODE = 1
    Assert-FreeCADArtifacts `
        -ExitCode 1 `
        -ExpectedPaths @($fresh) `
        -StartedAt $startedAt `
        -Operation 'test render'
    if ($LASTEXITCODE -ne 0) {
        throw "verified artifacts must normalize LASTEXITCODE to 0, got $LASTEXITCODE"
    }

    $missing = Join-Path $tempDir 'missing.png'
    try {
        Assert-FreeCADArtifacts `
            -ExitCode 1 `
            -ExpectedPaths @($missing) `
            -StartedAt $startedAt `
            -Operation 'test render'
        throw 'missing artifact was incorrectly accepted'
    }
    catch {
        if ($_.Exception.Message -eq 'missing artifact was incorrectly accepted') {
            throw
        }
    }

    $stale = Join-Path $tempDir 'stale.step'
    Set-Content -LiteralPath $stale -Value 'old model'
    (Get-Item -LiteralPath $stale).LastWriteTimeUtc = $startedAt.AddMinutes(-1)
    try {
        Assert-FreeCADArtifacts `
            -ExitCode 1 `
            -ExpectedPaths @($stale) `
            -StartedAt $startedAt `
            -Operation 'test export'
        throw 'stale artifact was incorrectly accepted'
    }
    catch {
        if ($_.Exception.Message -eq 'stale artifact was incorrectly accepted') {
            throw
        }
    }

    $empty = Join-Path $tempDir 'empty.png'
    New-Item -ItemType File -Path $empty | Out-Null
    try {
        Assert-FreeCADArtifacts `
            -ExitCode 1 `
            -ExpectedPaths @($empty) `
            -StartedAt $startedAt `
            -Operation 'test render'
        throw 'empty artifact was incorrectly accepted'
    }
    catch {
        if ($_.Exception.Message -eq 'empty artifact was incorrectly accepted') {
            throw
        }
    }

    'FREECAD_PROCESS_TEST_OK'
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force
}
