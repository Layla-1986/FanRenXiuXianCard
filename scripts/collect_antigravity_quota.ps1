# Reads the already-open Antigravity Settings - Models page through Windows UI Automation.
# It never starts, foregrounds, activates, or navigates an application. It emits only five
# numeric fields (or null), never raw UI text or any network/session/account information.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$scope = [System.Windows.Automation.TreeScope]::Children
$allWindows = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
    $scope,
    [System.Windows.Automation.Condition]::TrueCondition
)
$settingsWindow = $null
foreach ($window in $allWindows) {
    # Only the window title is inspected to locate the already-visible target page.
    if ($window.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and
        $window.Current.Name -match '(?i)settings\s*[-–]?\s*models') {
        $settingsWindow = $window
        break
    }
}
if ($null -eq $settingsWindow) { exit 0 }

function Get-Percent([string] $text, [string] $pattern) {
    if ($text.Length -gt 160 -or $text -notmatch $pattern) { return $null }
    $number = [int]$Matches['value']
    if ($number -ge 0 -and $number -le 100) { return $number }
    return $null
}

$result = [ordered]@{
    aiCredits = $null
    gemini = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null }
    claudeGpt = [ordered]@{ weeklyRemaining = $null; fiveHourRemaining = $null }
}
$texts = $settingsWindow.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Text
    ))
)
foreach ($element in $texts) {
    # Inspect only short text controls that explicitly name one of the quota categories.
    $text = $element.Current.Name
    if ($text -notmatch '(?i)(ai\s*credits|gemini|claude|gpt)' -or $text.Length -gt 160) { continue }
    if ($null -eq $result.aiCredits) {
        $result.aiCredits = Get-Percent $text '(?i)ai\s*credits\D*(?<value>100|[0-9]{1,2})'
    }
    if ($null -eq $result.gemini.weeklyRemaining) {
        $result.gemini.weeklyRemaining = Get-Percent $text '(?i)gemini.*weekly\D*(?<value>100|[0-9]{1,2})'
    }
    if ($null -eq $result.gemini.fiveHourRemaining) {
        $result.gemini.fiveHourRemaining = Get-Percent $text '(?i)gemini.*(?:5\s*-?\s*hour|five\s*-?\s*hour)\D*(?<value>100|[0-9]{1,2})'
    }
    if ($null -eq $result.claudeGpt.weeklyRemaining) {
        $result.claudeGpt.weeklyRemaining = Get-Percent $text '(?i)(?:claude|gpt).*weekly\D*(?<value>100|[0-9]{1,2})'
    }
    if ($null -eq $result.claudeGpt.fiveHourRemaining) {
        $result.claudeGpt.fiveHourRemaining = Get-Percent $text '(?i)(?:claude|gpt).*(?:5\s*-?\s*hour|five\s*-?\s*hour)\D*(?<value>100|[0-9]{1,2})'
    }
}

# ConvertTo-Json serializes only the ordered whitelist above.
$result | ConvertTo-Json -Depth 3 -Compress
