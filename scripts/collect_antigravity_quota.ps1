param(
    # Test-only synthetic controls. Normal collection never writes UIA text to disk.
    [string] $FixturePath
)

# Reads the already-open Antigravity Settings > Models page through Windows UI Automation.
# It never starts, foregrounds, activates, or navigates an application. It emits only five
# numeric fields (or null), never raw UI text or any network/session/account information.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$MaxAiCredits = 1000000000

function New-EmptyQuotaResult {
    return [ordered]@{
        aiCredits = $null
        gemini = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null; weeklyReset = $null; fiveHourReset = $null }
        claudeGpt = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null; weeklyReset = $null; fiveHourReset = $null }
    }
}

function Get-AntigravityProcessIds {
    $ids = [System.Collections.Generic.HashSet[int]]::new()
    try { $processes = @(Get-CimInstance Win32_Process -ErrorAction Stop) }
    catch {
        # Some Windows sessions deny Win32_Process inspection. Fall back to the
        # process list, which still provides the executable IDs without command lines.
        try {
            foreach ($process in @(Get-Process -ErrorAction Stop)) {
                if ($process.ProcessName -match '(?i)^antigravity(?:\s+ide)?$') {
                    [void]$ids.Add([int]$process.Id)
                }
            }
        } catch { }
        return $ids
    }
    foreach ($process in $processes) {
        if ($process.Name -match '(?i)^antigravity(?:\s+ide)?(?:\.exe)?$') { [void]$ids.Add([int]$process.ProcessId) }
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
    if ([string]::IsNullOrWhiteSpace($text) -or $text.Length -gt 120) { return $null }
    # Do not guess from signed or decimal text: -5 and 12.5 are unsupported values.
    foreach ($match in [regex]::Matches($text, '(?<![-+\d.,])(?<value>\d{1,10}|\d{1,3}(?:,\d{3})*)(?![\d.,])')) {
        $number = [int64]($match.Groups['value'].Value -replace ',', '')
        if ($number -ge 0 -and $number -le $MaxAiCredits) { return [int]$number }
    }
    return $null
}

function Get-Percent([string] $text) {
    if ([string]::IsNullOrWhiteSpace($text) -or $text.Length -gt 120) { return $null }
    # A value must be a complete unsigned integer token, optionally followed by %.
    $match = [regex]::Match($text, '(?<![-+\d.,])(?<value>100|[1-9]?\d)(?![\d.,])\s*%')
    if (-not $match.Success) { $match = [regex]::Match($text, '^\s*(?<value>100|[1-9]?\d)\s*$') }
    if (-not $match.Success) { return $null }
    return [int]$match.Groups['value'].Value
}

function Get-NearbyPercent($controls, [int] $labelIndex, [int] $endIndex) {
    $label = $controls[$labelIndex]
    $lastIndex = [Math]::Min($labelIndex + 5, $endIndex - 1)
    for ($index = $labelIndex; $index -le $lastIndex; $index++) {
        $candidate = $controls[$index]
        # A value may be a sibling Text control. Do not spill into the next visual paragraph.
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

function Get-ResetForPeriod($controls, [int] $startIndex, [int] $endIndex, [string] $periodPattern) {
    for ($index = $startIndex; $index -lt $endIndex; $index++) {
        if ($controls[$index].Name -notmatch $periodPattern -or $controls[$index].Name -notmatch '(?i)(?:quota|limit|remaining)') { continue }
        $lastIndex = [Math]::Min($index + 8, $endIndex - 1)
        for ($near = $index; $near -le $lastIndex; $near++) {
            $match = [regex]::Match($controls[$near].Name, '(?i)(?:fully\s+)?refresh(?:es)?\s+in\s+(?<duration>\d+\s*(?:days?|hours?|minutes?)(?:\s*,?\s*\d+\s*(?:days?|hours?|minutes?))?)')
            if ($match.Success) { return $match.Groups['duration'].Value }
        }
    }
    return $null
}

function Get-QuotaFromControls($controls) {
    $result = New-EmptyQuotaResult
    $controls = @($controls | Sort-Object Top, Left, Order)
    if ($controls.Count -eq 0) { return $result }

    # Page anchors must exist in visual order before any value is interpreted.
    $modelQuotaIndex = -1; $geminiIndex = -1; $claudeGptIndex = -1
    for ($index = 0; $index -lt $controls.Count; $index++) {
        $name = $controls[$index].Name
        if ($modelQuotaIndex -lt 0 -and $name -match '(?i)^model\s+(?:quota|credits)$') { $modelQuotaIndex = $index }
        if ($geminiIndex -lt 0 -and $name -match '(?i)^gemini\s+models?$') { $geminiIndex = $index }
        if ($claudeGptIndex -lt 0 -and $name -match '(?i)^claude\s+(?:and|&)\s+gpt\s+models?$') { $claudeGptIndex = $index }
    }
    if ($modelQuotaIndex -lt 0 -or $geminiIndex -lt 0 -or $claudeGptIndex -lt 0) { return $result }
    if ($modelQuotaIndex -ge $geminiIndex -or $geminiIndex -ge $claudeGptIndex) { return $result }

    for ($index = $modelQuotaIndex + 1; $index -lt $geminiIndex; $index++) {
        $value = Get-Credits $controls[$index].Name
        if ($null -ne $value) { $result.aiCredits = $value; break }
    }
    $result.gemini.weeklyRemaining = Get-RemainingForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)weekly'
    $result.gemini.fiveHourRemaining = Get-RemainingForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    $result.gemini.weeklyReset = Get-ResetForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)weekly'
    $result.gemini.fiveHourReset = Get-ResetForPeriod $controls ($geminiIndex + 1) $claudeGptIndex '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    $result.claudeGpt.weeklyRemaining = Get-RemainingForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)weekly'
    $result.claudeGpt.fiveHourRemaining = Get-RemainingForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    $result.claudeGpt.weeklyReset = Get-ResetForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)weekly'
    $result.claudeGpt.fiveHourReset = Get-ResetForPeriod $controls ($claudeGptIndex + 1) $controls.Count '(?i)(?:5\s*-?\s*hour|five\s*-?\s*hour)'
    return $result
}

function Get-FixtureControls([string] $path) {
    try { $fixture = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop }
    catch { return @() }
    if ($fixture.modelsPage -ne $true -or $null -eq $fixture.controls) { return @() }
    $controls = @(); $order = 0
    foreach ($item in $fixture.controls) {
        if ($item.name -isnot [string] -or [string]::IsNullOrWhiteSpace($item.name) -or $item.name.Length -gt 120) { continue }
        $controls += [pscustomobject]@{ Name = $item.name; Top = [int]$item.top; Left = [int]$item.left; Order = $order }
        $order++
    }
    return $controls
}

function Get-SelectedModelsContainer($window) {
    # Phase 1: require the Models navigation item and exact page anchors before
    # reading any values. Current Electron builds expose Models as Text/Button
    # controls rather than a SelectionItem, so selection state is not available.
    $modelsTabCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Models'
    )
    $modelsTab = $window.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $modelsTabCondition)
    if ($null -eq $modelsTab) { return $null }
    try {
        $quotaHeading = $null
        foreach ($headingName in @('Model Quota', 'Model Credits')) {
            $quotaHeading = $window.FindFirst(
                [System.Windows.Automation.TreeScope]::Descendants,
                (New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::NameProperty,
                    $headingName
                ))
            )
            if ($null -ne $quotaHeading) { break }
        }
        if ($null -eq $quotaHeading) { return $null }
        foreach ($anchorName in @('Gemini Models', 'Claude and GPT models')) {
            $anchor = $window.FindFirst(
                [System.Windows.Automation.TreeScope]::Descendants,
                (New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::NameProperty,
                    $anchorName
                ))
            )
            if ($null -eq $anchor) { return $null }
        }
    } catch { return $null }
    return $window
}

function Get-VisibleQuotaControls($container) {
    # Phase 2: names are read only below the confirmed Models page. Chromium maps
    # ARIA headings to Heading controls, so add only the exact quota headings to
    # the ordinary Text controls used for labels and values.
    $textCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Text
    )
    $controls = @(); $order = 0
    foreach ($element in $container.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textCondition)) {
        try {
            if ($element.Current.IsOffscreen) { continue }
            $bounds = $element.Current.BoundingRectangle
            $name = $element.Current.Name
        } catch { continue }
        if ([string]::IsNullOrWhiteSpace($name) -or $name.Length -gt 120 -or $bounds.Width -le 0 -or $bounds.Height -le 0) { continue }
        $controls += [pscustomobject]@{ Name = $name; Top = [int]$bounds.Top; Left = [int]$bounds.Left; Order = $order }
        $order++
    }
    foreach ($anchorName in @('Model Quota', 'Model Credits', 'Gemini Models', 'Claude and GPT models')) {
        if (@($controls | Where-Object { $_.Name -eq $anchorName }).Count -gt 0) { continue }
        $anchor = $container.FindFirst(
            [System.Windows.Automation.TreeScope]::Descendants,
            (New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::NameProperty,
                $anchorName
            ))
        )
        if ($null -eq $anchor) { continue }
        try {
            if ($anchor.Current.IsOffscreen) { continue }
            $bounds = $anchor.Current.BoundingRectangle
        } catch { continue }
        if ($bounds.Width -le 0 -or $bounds.Height -le 0) { continue }
        $controls += [pscustomobject]@{ Name = $anchorName; Top = [int]$bounds.Top; Left = [int]$bounds.Left; Order = $order }
        $order++
    }
    return $controls
}

$result = New-EmptyQuotaResult
if ($FixturePath) {
    # Fixtures are test-only synthetic quota labels/values; production invokes no fixture path.
    $result = Get-QuotaFromControls (Get-FixtureControls $FixturePath)
} else {
    $topLevelWindows = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )
    $antigravityProcessIds = Get-AntigravityProcessIds
    foreach ($window in $topLevelWindows) {
        if ($window.Current.ControlType -ne [System.Windows.Automation.ControlType]::Window) { continue }
        $processMatch = $antigravityProcessIds.Contains([int]$window.Current.ProcessId)
        $titleMatch = $window.Current.Name -match '(?i)^Settings(?: - Models)?$'
        if (-not ($processMatch -or $titleMatch)) { continue }
        $modelsContainer = Get-SelectedModelsContainer $window
        if ($null -eq $modelsContainer) { continue }
        $result = Get-QuotaFromControls (Get-VisibleQuotaControls $modelsContainer)
        break
    }
}

# ConvertTo-Json serializes only the ordered whitelist above.
$result | ConvertTo-Json -Depth 3 -Compress
