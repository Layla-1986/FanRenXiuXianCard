$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$cssPath = Join-Path $projectRoot 'styles/mortal-seal-card.css'
$jsPath = Join-Path $projectRoot 'scripts/quota-card.js'
$collectorPath = Join-Path $projectRoot 'scripts/collect_antigravity_quota.ps1'
$html = Get-Content -LiteralPath $htmlPath -Raw -Encoding UTF8
$css = Get-Content -LiteralPath $cssPath -Raw -Encoding UTF8
$js = Get-Content -LiteralPath $jsPath -Raw -Encoding UTF8
$collector = Get-Content -LiteralPath $collectorPath -Raw -Encoding UTF8
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $script:failures.Add($Message) }
}

foreach ($asset in @('assets/hanli-nangong-background.png', 'assets/antigravity-nangong-background.jpg')) {
    Assert-True (Test-Path -LiteralPath (Join-Path $projectRoot $asset)) "Missing local asset: $asset"
}

Assert-True ($html.Contains('href="styles/mortal-seal-card.css"')) 'HTML must load the focused card stylesheet'
Assert-True ($html.Contains('src="scripts/quota-card.js"')) 'HTML must load the quota controller'
Assert-True (-not $html.Contains('<style>')) 'Card styles must remain in the focused stylesheet'
Assert-True ($html.Contains('class="seal-card"')) 'Missing stable 480 by 270 card root'
Assert-True ($html.Contains('id="widget"')) 'Missing stable widget state root'

# Codex co-branded first page: this is the visual contract from sword-array-qingzhu-model-v6.html.
Assert-True ($html.Contains('class="portrait-base"')) 'Codex page must use the co-branded portrait layer'
Assert-True ($html.Contains('class="moon-field"')) 'Codex page must preserve the quota-reactive moon layer'
Assert-True ($html.Contains('id="moon-luminance-mask"')) 'Moon must be isolated with the reference luminance mask'
Assert-True ($html.Contains('class="veil"')) 'Codex page must retain the portrait readability veil'
Assert-True ($html.Contains('class="formation-foundation"')) 'Missing five-layer Dageng formation foundation'
Assert-True ($html.Contains('class="formation-radiance"')) 'Missing counter-rotating formation radiance'
Assert-True (($html | Select-String 'class="seal-track' -AllMatches).Matches.Count -eq 2) 'Dageng formation must expose two seal tracks'
Assert-True ($html.Contains('class="golden-arc-track"')) 'Missing jade-gold formation arc'
Assert-True ($html.Contains('class="broken-orbit"')) 'Missing broken outer orbit'
Assert-True ($html.Contains('class="satellite-system"')) 'Missing four animated satellite eyes'
Assert-True (($html | Select-String 'class="satellite-eye' -AllMatches).Matches.Count -eq 4) 'Formation must contain exactly four satellite eyes'
Assert-True ($html.Contains('class="formation-particles"')) 'Missing restrained formation particles'
Assert-True ($html.Contains('class="core-dot"')) 'Missing shared formation eye core'
Assert-True (-not $html.Contains('class="formation-sword"')) 'Old fixed half-ring sword slots must not remain on the co-branded page'
Assert-True ($html.Contains('id="percent"')) 'Missing seven-day quota value target'
Assert-True ($html.Contains('id="used"')) 'Missing used quota target'
Assert-True ($html.Contains('id="resetAt"')) 'Missing Codex reset-time target'
Assert-True ($html.Contains('id="balance"')) 'Missing converted dollar balance target'
Assert-True ($html.Contains('id="syncStatus"')) 'Missing Codex live-read status target'
$accountMotto = -join (0x9047,0x4E8B,0x4E0D,0x51B3,0x20,0xB7,0x20,0x53EF,0x95EE,0x6625,0x98CE | ForEach-Object { [char]$_ })
$footerMotto = -join (0x5FF5,0x5934,0x901A,0x8FBE,0x20,0xB7,0x20,0x7096,0x716E,0x7EA2,0x5C18 | ForEach-Object { [char]$_ })
Assert-True ($html.Contains($accountMotto)) 'Co-branded account motto must match the source work file'
Assert-True ($html.Contains($footerMotto)) 'Co-branded footer motto must match the source work file'

# The Antigravity page remains a separate manual page.
Assert-True ($html.Contains('id="antigravityToggle"')) 'Missing manual Antigravity page control'
Assert-True ($html.Contains('id="unlockButton"')) 'Missing unlock control'
Assert-True ($html.Contains('class="antigravity-page"')) 'Missing independent Antigravity card page'
foreach ($id in @('agGeminiWeekly','agGeminiWeeklyReset','agGeminiFiveHour','agGeminiFiveHourReset','agClaudeWeekly','agClaudeWeeklyReset','agClaudeFiveHour','agClaudeFiveHourReset','agSyncStatus','agSyncedAt')) {
    Assert-True ($html.Contains("id=`"$id`"")) "Missing Antigravity target: $id"
}
Assert-True ([regex]::IsMatch($html, '(?s)id="agGeminiWeekly".*?</div>\s*<small class="quota-reset" id="agGeminiWeeklyReset"')) 'Gemini weekly reset must remain a separate column'
Assert-True ([regex]::IsMatch($html, '(?s)id="agClaudeFiveHour".*?</div>\s*<small class="quota-reset" id="agClaudeFiveHourReset"')) 'Claude five-hour reset must remain a separate column'

Assert-True ($css.Contains('width: 480px')) 'Card must retain the exact 480px width'
Assert-True ($css.Contains('height: 270px')) 'Card must retain the exact 270px height'
Assert-True ($css.Contains('url("../assets/hanli-nangong-background.png")')) 'Codex page must use the confirmed Han Li and Nangong Wan background'
Assert-True ($css.Contains('brightness(.9)')) 'Portrait exposure must match the approved co-branded page'
Assert-True ($css.Contains('--moon-energy:')) 'Moon exposure must remain independently quota-reactive'
Assert-True ($css.Contains('@keyframes foundationTurn')) 'Formation foundation must rotate slowly'
Assert-True ($css.Contains('@keyframes radianceCounterTurn')) 'Formation radiance must counter-rotate'
Assert-True ($css.Contains('@keyframes satelliteOrbit')) 'Satellite formation eyes must orbit'
Assert-True ($css.Contains('@keyframes jadeNumeralBreathe')) 'Jade-gold quota numeral must breathe subtly'
Assert-True ($css.Contains('url("../assets/antigravity-nangong-background.jpg")')) 'Antigravity page must retain its independent portrait background'
Assert-True ($css.Contains('backdrop-filter: blur(10px)')) 'Antigravity ledgers must retain the jelly-glass treatment'
Assert-True ($css.Contains('@keyframes scrollPageIn')) 'Manual page switch must retain the short scroll reveal'
Assert-True (-not $css.Contains('rotateY(')) 'Page switch must not flip the card'
Assert-True ($css.Contains('@media (prefers-reduced-motion: reduce)')) 'Missing reduced-motion treatment'

Assert-True ($js.Contains('function setUsed(value)')) 'Missing reusable Codex quota interface'
Assert-True ($js.Contains('function visualStateFor(remain)')) 'Missing source work file color interpolation'
Assert-True ($js.Contains("fetch('/api/codex-quota'")) 'Codex page must poll the local read-only API'
Assert-True ($js.Contains('setInterval(fetchCodexQuota, 15000)')) 'Codex quota must refresh every 15 seconds'
Assert-True ($js.Contains('formatPointBalance(payload.creditBalance)')) 'Codex points must convert to US dollars'
Assert-True ($js.Contains("fetch('/api/antigravity-quota'")) 'Antigravity page must keep its local read-only API'
Assert-True ($js.Contains("sessionStorage.setItem('quota-card-page'")) 'Manual page choice must remain session-scoped'
Assert-True ($js.Contains('widget.dataset.page = page')) 'Page switch must use the stable card state root'
Assert-True ($collector.Contains('(?:\s+ide)?')) 'Collector must continue recognizing the Antigravity IDE process'

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Host "FAIL: $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PASS: co-branded Codex first page and independent Antigravity second page satisfy the visual contract.' -ForegroundColor Green
