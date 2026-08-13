# Reads an already-open Antigravity Settings > Models page through Windows UI Automation.
# It never starts, foregrounds, activates, or navigates an application. It emits only five
# numeric fields (or null), never raw UI text or any network/session/account information.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$MaxAiCredits = 1000000000

function Get-AntigravityProcessIds {
    $ids = [System.Collections.Generic.HashSet[int]]::new()
    try { $processes = @(Get-CimInstance Win32_Process -ErrorAction Stop) }
    catch { return $ids }
    foreach ($process in $processes) {
        if ($process.Name -match '(?i)^antigravity(?:\.exe)?$') { [void]$ids.Add([int]$process.ProcessId) }
    }
    do {
        $added = $false
        foreach ($process in $processes) {
            if ($ids.Contains([int]$process.ParentProcessId) -and $ids.Add([int]$process.ProcessId)) { $added = $true }
        }
    } while ($added)
    Write-Output -NoEnumerate $ids
}

function Get-Credits([string] $text) {
    if ($text.Length -gt 120) { return $null }
    foreach ($match in [regex]::Matches($text, '(?<![\d,])(?<value>\d{1,3}(?:,\d{3})*|\d{1,10})(?![\d,])')) {
        $number = [int64]($match.Groups['value'].Value -replace ',', '')
        if ($number -ge 0 -and $number -le $MaxAiCredits) { return [int]$number }
    }
    return $null
}

function Get-Percent([string] $text) {
    if ($text.Length -gt 120) { return $null }
    # Percent signs avoid treating a label such as "5-hour" as a 5% value; a plain
    # numeric text control is allowed because UIA often separates the value from its label.
    $match = [regex]::Match($text, '(?<!\d)(?<value>100|[1-9]?\d)(?!\d)\s*%')
    if (-not $match.Success) { $match = [regex]::Match($text, '^\s*(?<value>100|[1-9]?\d)\s*$') }
    if (-not $match.Success) { return $null }
    $number = [int]$match.Groups['value'].Value
    if ($number -ge 0 -and $number -le 100) { return $number }
    return $null
}

function Get-NearbyPercent($controls, [int] $labelIndex, [int] $endIndex) {
    $label = $controls[$labelIndex]
    $lastIndex = [Math]::Min($labelIndex + 5, $endIndex - 1)
    for ($index = $labelIndex; $index -le $lastIndex; $index++) {
        $candidate = $controls[$index]
        # A value may be a sibling text control. Keep the search in the same visual paragraph.
        if ($index -gt $labelIndex -and $candidate.Top -gt ($label.Top + 48)) { break }
        $value = Get-Percent $candidate.Name
        if ($null -ne $value) { return $value }
    }
    return $null
}

function Get-RemainingForPeriod($controls, [int] $startIndex, [int] $endIndex, [string] $periodPattern) {
    for ($index = $startIndex; $index -lt $endIndex; $index++) {
        if ($controls[$index].Name -match $periodPattern) {
            $value = Get-NearbyPercent $controls $index $endIndex
            if ($null -ne $value) { return $value }
        }
    }
    return $null
}

$result = [ordered]@{
    aiCredits = $null
    gemini = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null }
    claudeGpt = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null }
}

$topLevelWindows = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition
)
$antigravityProcessIds = Get-AntigravityProcessIds

foreach ($window in $topLevelWindows) {
    if ($window.Current.ControlType -ne [System.Windows.Automation.ControlType]::Window) { continue }
    # Settings - Models is often an internal page, not a top-level window. Restrict discovery
    # to windows owned by the Antigravity process, without inspecting titles or activating it.
    if (-not $antigravityProcessIds.Contains([int]$window.Current.ProcessId)) { continue }

    $controls = @()
    $order = 0
    foreach ($element in $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        try {
            $name = $element.Current.Name
            $bounds = $element.Current.BoundingRectangle
        } catch { continue }
        if ([string]::IsNullOrWhiteSpace($name) -or $name.Length -gt 120 -or $bounds.Width -le 0 -or $bounds.Height -le 0) { continue }
        $controls += [pscustomobject]@{ Name = $name; Left = [int]$bounds.Left; Top = [int]$bounds.Top; Order = $order }
        $order++
    }
    $controls = @($controls | Sort-Object Top, Left, Order)
    if ($controls.Count -eq 0) { continue }

    # Require all three model-page anchors in visual order before inspecting nearby quota controls.
    $modelQuotaIndex = -1; $geminiIndex = -1; $claudeGptIndex = -1
    for ($index = 0; $index -lt $controls.Count; $index++) {
        $name = $controls[$index].Name
        if ($modelQuotaIndex -lt 0 -and $name -match '(?i)model\s+quota') { $modelQuotaIndex = $index }
        if ($geminiIndex -lt 0 -and $name -match '(?i)gemini\s+models?') { $geminiIndex = $index }
        if ($claudeGptIndex -lt 0 -and $name -match '(?i)claude\s+(?:and|&)\s+gpt\s+models?') { $claudeGptIndex = $index }
    }
    if ($modelQuotaIndex -lt 0 -or $geminiIndex -lt 0 -or $claudeGptIndex -lt 0) { continue }
    if ($modelQuotaIndex -ge $geminiIndex -or $geminiIndex -ge $claudeGptIndex) { continue }

    $creditEnd = $geminiIndex
    for ($index = $modelQuotaIndex + 1; $index -lt $creditEnd; $index++) {
        $value = Get-Credits $controls[$index].Name
        if ($null -ne $value) { $result.aiCredits = $value; break }
    }
    $result.gemini.weeklyRemaining = Get-RemainingForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)weekly'
    $result.gemini.fiveHourRemaining = Get-RemainingForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    $result.claudeGpt.weeklyRemaining = Get-RemainingForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)weekly'
    $result.claudeGpt.fiveHourRemaining = Get-RemainingForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    break
}

# ConvertTo-Json serializes only the ordered whitelist above.
$result | ConvertTo-Json -Depth 3 -Compress
