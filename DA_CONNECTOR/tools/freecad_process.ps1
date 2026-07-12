function Get-ConnectorOutputStem {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Series,

        [Parameter(Mandatory = $true)]
        [double]$Pitch,

        [Parameter(Mandatory = $true)]
        [int]$Poles,

        [string]$Variant,
        [string]$ActuatorColors
    )

    $pitchCode = ([int][math]::Round($Pitch * 100.0)).ToString('D3')
    $suffix = if ($Variant) {
        ([regex]::Replace($Variant.Trim(), '[^a-zA-Z0-9_-]+', '-')).Trim('-').ToLowerInvariant()
    }
    elseif ($ActuatorColors) {
        $values = @($ActuatorColors.Split(',') | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_ })
        if (@($values | Select-Object -Unique).Count -gt 1) {
            ($values | ForEach-Object { [regex]::Replace($_.TrimStart('#'), '[^a-z0-9]+', '') }) -join '-'
        }
    }

    $stem = "$($Series.ToUpperInvariant())-$pitchCode-$($Poles)P"
    if ($suffix) {
        $stem += "-$suffix"
    }
    return $stem
}

function Invoke-FreeCADProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $process = Start-Process `
        -FilePath $Executable `
        -ArgumentList $Arguments `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    return $process.ExitCode
}

function Assert-FreeCADArtifacts {
    param(
        [AllowNull()]
        [Nullable[int]]$ExitCode,

        [Parameter(Mandatory = $true)]
        [string[]]$ExpectedPaths,

        [Parameter(Mandatory = $true)]
        [DateTime]$StartedAt,

        [Parameter(Mandatory = $true)]
        [string]$Operation
    )

    $problems = foreach ($path in $ExpectedPaths) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            "missing: $path"
            continue
        }
        $file = Get-Item -LiteralPath $path
        if ($file.Length -le 0) {
            "empty: $path"
        }
        elseif ($file.LastWriteTimeUtc -lt $StartedAt.ToUniversalTime()) {
            "not updated by this run: $path"
        }
    }

    if ($problems) {
        $exitText = if ($null -eq $ExitCode) { 'none' } else { [string]$ExitCode }
        throw "$Operation failed (FreeCAD exit code $exitText): $($problems -join '; ')"
    }

    if ($null -ne $ExitCode -and $ExitCode -ne 0) {
        Write-Warning "$Operation completed with FreeCAD exit code $ExitCode; fresh output artifacts were verified."
    }
    $global:LASTEXITCODE = 0
}
