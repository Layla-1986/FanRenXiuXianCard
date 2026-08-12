$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$cssPath = Join-Path $projectRoot 'styles/mortal-seal-card.css'
$jsPath = Join-Path $projectRoot 'scripts/quota-card.js'
$html = if (Test-Path -LiteralPath $htmlPath) { Get-Content -LiteralPath $htmlPath -Raw -Encoding UTF8 } else { '' }
$css = if (Test-Path -LiteralPath $cssPath) { Get-Content -LiteralPath $cssPath -Raw -Encoding UTF8 } else { '' }
$js = if (Test-Path -LiteralPath $jsPath) { Get-Content -LiteralPath $jsPath -Raw -Encoding UTF8 } else { '' }
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $script:failures.Add($Message) }
}

$localAssets = @(
    'assets/hanli-nangong-background.png',
    'assets/nascent-soul-aura-reference.png',
    'assets/dageng-sword-array-v2.png',
    'assets/qingzhu-fengyun-sword-v2.png',
    'assets/wind-thunder-wings-v2.png'
)

foreach ($asset in $localAssets) {
    Assert-True (Test-Path -LiteralPath (Join-Path $projectRoot $asset)) "Missing local asset: $asset"
}

Assert-True (Test-Path -LiteralPath $cssPath) 'Missing focused card stylesheet'
Assert-True (Test-Path -LiteralPath $jsPath) 'Missing quota controller'
Assert-True ($html.Contains('href="styles/mortal-seal-card.css"')) 'HTML must load the focused card stylesheet'
Assert-True ($html.Contains('src="scripts/quota-card.js"')) 'HTML must load the quota controller'
Assert-True (-not $html.Contains('<style>')) 'Legacy inline stylesheet must be removed'
Assert-True (-not $html.Contains('class="data"')) 'Legacy right-side data panel must be removed'
Assert-True (-not $html.Contains('class="core"')) 'Legacy left-side quota panel must be removed'

Assert-True ($html.Contains('class="seal-card"')) 'Missing seal-card scene root'
Assert-True ($html.Contains('id="widget"')) 'Missing stable widget state root'
Assert-True ($html.Contains('class="portrait-scene"')) 'Missing portrait background layer'
Assert-True ($html.Contains('class="scene-veil"')) 'Missing scene readability veil'
Assert-True ($html.Contains('class="seal-formation"')) 'Missing overflow formation scene'
Assert-True ($html.Contains('class="formation-swords formation-swords--lower-arc"')) 'Formation swords must be gathered into the lower battle arc'
Assert-True ($html.Contains('class="quota-eye"')) 'Missing seven-day quota eye'
Assert-True ($html.Contains('id="percent"')) 'Missing seven-day quota value target'
Assert-True (-not $html.Contains('class="spirit-meridian"')) 'Curved progress meridian must be removed'
Assert-True (-not $html.Contains('meridian-')) 'All progress-line SVG layers must be removed'
Assert-True (-not $html.Contains('wind-thunder-wings')) 'Wind-Thunder Wings must be removed from the card'
$windThunderWingCopy = ([char]0x98CE) + ([char]0x96F7) + ([char]0x7FC5)
Assert-True (-not $html.Contains($windThunderWingCopy)) 'Obsolete Wind-Thunder Wings copy must be removed'
Assert-True ($html.Contains('class="quota-ledger"')) 'Missing right-side quota text ledger'
Assert-True ($html.Contains('class="ledger-item ledger-item--cycle"')) 'Missing seven-day cycle information group'
Assert-True ($html.Contains('class="ledger-item ledger-item--credits"')) 'Missing account credit balance information group'
Assert-True ($html.Contains('id="credits"')) 'Missing account credit balance value interface'
$accountCreditLabel = ([char]0x8D26) + ([char]0x6237) + ([char]0x70B9) + ([char]0x6570) + ([char]0x4F59) + ([char]0x989D)
$pointUnit = '0 ' + ([char]0x70B9)
$fiveHourCopy = ([char]0x4E94) + ([char]0x5C0F) + ([char]0x65F6) + ([char]0x4F59) + ([char]0x91CF)
Assert-True ($html.Contains($accountCreditLabel)) 'Account credit balance label must be visible'
Assert-True ($html.Contains($pointUnit)) 'Account credit balance must use a point unit'
Assert-True (-not $html.Contains($fiveHourCopy)) 'Obsolete five-hour quota copy must be removed'
Assert-True ($html.Contains('class="ledger-divider"')) 'Missing restrained ledger divider'
Assert-True ($html.Contains('id="used"')) 'Missing used quota label target'
Assert-True ($html.Contains('id="unlockButton"')) 'Missing unlock control'
Assert-True (($html | Select-String 'data-used=' -AllMatches).Matches.Count -eq 3) 'Exactly three quota demonstration states are required'

Assert-True (($html | Select-String 'class="formation-sword"' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve fixed sword slots'
Assert-True ($html.Contains('class="formation-ring formation-ring--outer"')) 'Missing outer perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--middle"')) 'Missing middle perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--inner"')) 'Missing inner perspective ring'
Assert-True ($html.Contains('class="qingzhu-sword"')) 'Missing Qingzhu main sword'
Assert-True ($html.Contains('class="stray-sword stray-sword--one"')) 'Missing out-of-ring sword accent'
Assert-True (-not $html.Contains('assets/wind-thunder-wings-v2.png')) 'Wind-Thunder Wings texture must no longer render'

Assert-True ($css.Contains('--abyss-ink: #041416')) 'Missing abyss-ink token'
Assert-True ($css.Contains('--nascent-cyan: #71e2dc')) 'Missing Nascent Soul cyan token'
Assert-True ($css.Contains('--bamboo-jade: #59d99d')) 'Missing bamboo jade token'
Assert-True ($css.Contains('--moon-white: #eaf8ee')) 'Missing moon-white token'
Assert-True ($css.Contains('--ward-gold: #d5b564')) 'Missing ward-gold token'
Assert-True ($css.Contains('--mist-blue: #5ea8c9')) 'Missing mist-blue token'
Assert-True ($css.Contains('width: 480px')) 'Card must retain the exact 480px width'
Assert-True ($css.Contains('height: 270px')) 'Card must retain the exact 270px height'
Assert-True ($css.Contains('url("../assets/hanli-nangong-background.png")')) 'Confirmed Han Li and Nangong Wan background must remain active'
Assert-True ($css.Contains('background-position: 51% 48%')) 'Portrait crop must preserve the face-to-face center'
Assert-True ($css.Contains('url("../assets/dageng-sword-array-v2.png")')) 'Great Geng texture must be fused into the formation material'
Assert-True ($css.Contains('url("../assets/qingzhu-fengyun-sword-v2.png")')) 'Qingzhu texture must be fused into the main sword material'
Assert-True ($css.Contains('.formation-ring--outer {')) 'Outer ring must have its own material rule'
Assert-True (-not $css.Contains('.formation-swords { animation:')) 'Sword slots must remain fixed while rings move'
Assert-True (-not $css.Contains('offset-path: path(')) 'Progress-marker motion path must be removed'
Assert-True (-not $css.Contains('.wind-thunder-wings')) 'Wind-Thunder Wings styling must be removed'
Assert-True (-not $css.Contains('.meridian-path')) 'Progress-line styling must be removed'
Assert-True ($css.Contains('.quota-ledger {')) 'Quota ledger must have a dedicated layout rule'
Assert-True ($css.Contains('right: 18px')) 'Quota ledger must align to the card right edge'
Assert-True ($css.Contains('width: 136px')) 'Quota ledger must preserve the portrait center with a compact width'
Assert-True ($css.Contains('clip-path: inset(42% 0 0')) 'Static upper formation texture must be removed'
Assert-True (-not $css.Contains('@keyframes windRun')) 'Obsolete wind-current animation must be removed'
Assert-True (-not $css.Contains('@keyframes thunderRun')) 'Obsolete thunder animation must be removed'
Assert-True ($css.Contains('@keyframes sealAwaken')) 'Missing one-shot awakening sequence'
Assert-True ($css.Contains('animation: sealAwaken 1.75s')) 'Awakening sequence must stay under 1.8 seconds'
Assert-True ($css.Contains('@media (prefers-reduced-motion: reduce)')) 'Missing reduced-motion treatment'
Assert-True ($css.Contains('animation: none !important')) 'Reduced-motion mode must stop continuous motion'
Assert-True ($css.Contains('transition-duration: .001ms !important')) 'Reduced-motion mode must suppress state-transition movement'

Assert-True ($js.Contains('function setUsed(value)')) 'Missing reusable setUsed interface'
Assert-True ($js.Contains('Number.isFinite(Number(value))')) 'setUsed must guard non-finite input'
Assert-True ($js.Contains('Math.round(remaining * 12)')) 'Lit sword count must derive from remaining quota'
Assert-True ($js.Contains("sword.classList.toggle('is-lit', index < litSwordCount)")) 'Sword slots must update from the derived count'
Assert-True ($js.Contains('setUsed(Number(button.dataset.used))')) 'Demo controls must use the public updater'
Assert-True ($js.Contains("unlockButton.addEventListener('click'")) 'Unlock button behavior must remain interactive'
Assert-True ($js.Contains('window.setUsed = setUsed')) 'setUsed must remain available to future integrations'

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Host "FAIL: $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PASS: mortal seal scroll structure, state interfaces, and local assets satisfy the visual contract.' -ForegroundColor Green
