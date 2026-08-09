# Mortal Seal Scroll Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the 480 × 270 quota card as a cinematic “墨海剑墟·法宝封印图卷” scene that keeps the confirmed quota interfaces while replacing the old HUD composition with an overflowing Great Geng sword formation, a Qingzhu main sword, and a curved Wind-Thunder Wings spirit meridian.

**Architecture:** Keep the deliverable framework-free and split the accumulated single-file prototype into semantic HTML, one focused stylesheet, and one state controller. The HTML owns scene structure, CSS owns composition/material/motion/responsive behavior, and JavaScript owns only quota normalization, text updates, sword illumination, marker position, controls, and accessible state.

**Tech Stack:** HTML5, CSS custom properties and keyframes, vanilla JavaScript, PowerShell contract tests, local PNG assets, local Python static preview.

## Global Constraints

- Keep the card canvas exactly `480px × 270px`; scale the entire card on narrow viewports instead of changing internal geometry.
- Keep `assets/hanli-nangong-background.png` and the three confirmed artifact references; do not add remote fonts, CDNs, frameworks, or network image dependencies.
- Preserve `--used`, `#percent`, `#used`, `setUsed(value)`, the 20%/55%/85% demo buttons, and the top-right unlock button behavior.
- Clamp finite `setUsed(value)` input to `0..1`; non-finite input falls back to `0`.
- Derive the seven-day remaining value as `100 - usedPercent` and illuminated swords as `Math.round((1 - used) * 12)`.
- The 20%, 55%, and 85% used states must show 80%, 45%, and 15% remaining with 10, 5, and 2 illuminated sword slots.
- Keep the five-hour quota fixed at 58% and visually subordinate to the seven-day quota.
- Do not modify `index.html`; do not connect a real quota API in this change.
- All continuous animation must stop under `prefers-reduced-motion: reduce` without changing values, sword count, or progress-marker position.
- The new implementation must replace the accumulated CSS rather than append another override block.

## File Map

- `original-artifact-refined.html`: semantic display page, 480 × 270 scene markup, three demo controls, and explanatory copy.
- `styles/mortal-seal-card.css`: page presentation, card tokens, background masks, formation geometry, sword/wing materials, entrance choreography, responsive scaling, and reduced-motion fallback.
- `scripts/quota-card.js`: `setUsed(value)`, state normalization, numeric labels, twelve sword states, wing position, unlock state, and demo-button events.
- `tests/visual-spec.ps1`: static contract across HTML, CSS, JavaScript, and required local assets.
- `artifacts/mortal-seal-scroll-wide.png`: final desktop-width visual proof.
- `artifacts/mortal-seal-scroll-narrow.png`: final 523 × 792 visual proof.

---

### Task 1: Lock the New Three-File Contract

**Files:**
- Modify: `tests/visual-spec.ps1`
- Test: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: existing local files under `assets/`.
- Produces: failing requirements for `styles/mortal-seal-card.css`, `scripts/quota-card.js`, `.seal-card`, `.seal-formation`, `.spirit-meridian`, `.wind-thunder-wings`, `.spirit-seal`, twelve `.formation-sword` nodes, and preserved IDs/functions.

- [ ] **Step 1: Replace the single-file assertions with a split-file contract**

Use three source reads and accumulate failures without stopping at the first assertion:

```powershell
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$cssPath = Join-Path $projectRoot 'styles/mortal-seal-card.css'
$jsPath = Join-Path $projectRoot 'scripts/quota-card.js'
$html = if (Test-Path $htmlPath) { Get-Content $htmlPath -Raw -Encoding UTF8 } else { '' }
$css = if (Test-Path $cssPath) { Get-Content $cssPath -Raw -Encoding UTF8 } else { '' }
$js = if (Test-Path $jsPath) { Get-Content $jsPath -Raw -Encoding UTF8 } else { '' }
```

Add exact assertions for:

```powershell
Assert-True ($html.Contains('href="styles/mortal-seal-card.css"')) 'HTML must load the focused card stylesheet'
Assert-True ($html.Contains('src="scripts/quota-card.js"')) 'HTML must load the quota controller'
Assert-True ($html.Contains('class="seal-card"')) 'Missing seal-card scene root'
Assert-True ($html.Contains('class="seal-formation"')) 'Missing overflow formation scene'
Assert-True ($html.Contains('class="spirit-meridian"')) 'Missing curved spirit meridian'
Assert-True ($html.Contains('class="spirit-seal"')) 'Missing subordinate five-hour seal'
Assert-True (($html | Select-String 'class="formation-sword"' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve fixed sword slots'
Assert-True ($css.Contains('--abyss-ink: #041416')) 'Missing abyss-ink token'
Assert-True ($css.Contains('@media (prefers-reduced-motion: reduce)')) 'Missing reduced-motion treatment'
Assert-True ($js.Contains('function setUsed(value)')) 'Missing reusable setUsed interface'
Assert-True ($js.Contains('Math.round(remaining * 12)')) 'Sword count must derive from remaining quota'
```

- [ ] **Step 2: Run the test and verify the new contract fails**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

Expected: FAIL messages for missing split stylesheet/script and new scene hooks while all five local asset checks still pass.

- [ ] **Step 3: Commit the red contract**

```powershell
git add tests/visual-spec.ps1
git commit -m "test: define mortal seal card contract"
```

---

### Task 2: Rebuild the Display Page and Semantic Card Scene

**Files:**
- Modify: `original-artifact-refined.html`
- Create: `styles/mortal-seal-card.css`
- Create: `scripts/quota-card.js`
- Test: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: contract hooks from Task 1.
- Produces: stable DOM for CSS and JavaScript: `#widget`, `#percent`, `#used`, `#unlockButton`, `.formation-sword[data-sword-index]`, `[data-used]` controls.

- [ ] **Step 1: Replace the accumulated inline page with semantic scene markup**

The HTML head must load only the focused stylesheet and the body must end with a deferred controller:

```html
<link rel="stylesheet" href="styles/mortal-seal-card.css">
...
<script src="scripts/quota-card.js" defer></script>
```

Use this scene hierarchy inside `#widget`:

```html
<article class="seal-card" id="widget" style="--used:.2" aria-label="Codex 用量法宝封印图卷">
  <div class="portrait-scene" aria-hidden="true"></div>
  <div class="scene-veil" aria-hidden="true"></div>
  <header class="card-mark">...</header>
  <div class="seal-formation" aria-hidden="true">...</div>
  <section class="quota-eye" aria-label="七日额度余量">
    <strong id="percent">80%</strong><span>七日额度余量</span>
  </section>
  <section class="spirit-meridian" aria-label="七日额度进度">...</section>
  <section class="spirit-seal" aria-label="五小时额度余量">...</section>
  <footer class="card-foot">...</footer>
</article>
```

Generate twelve explicit fixed sword nodes with `data-sword-index="0"` through `data-sword-index="11"`; do not generate them dynamically so the design remains inspectable without JavaScript.

- [ ] **Step 2: Add a minimal stylesheet and controller so sources load without errors**

Create `styles/mortal-seal-card.css` with tokens and base dimensions:

```css
:root {
  --abyss-ink: #041416;
  --nascent-cyan: #71e2dc;
  --bamboo-jade: #59d99d;
  --moon-white: #eaf8ee;
  --ward-gold: #d5b564;
  --mist-blue: #5ea8c9;
}
.seal-card { position: relative; width: 480px; height: 270px; overflow: hidden; }
```

Create `scripts/quota-card.js` with a temporary but valid exported global:

```javascript
function setUsed(value) {
  const numeric = Number.isFinite(Number(value)) ? Number(value) : 0;
  document.querySelector('#widget')?.style.setProperty('--used', String(Math.min(1, Math.max(0, numeric))));
}
window.setUsed = setUsed;
```

- [ ] **Step 3: Run the contract and inspect the remaining failures**

Run the PowerShell test. Expected: split-file, scene-root, and twelve-sword assertions pass; state-logic and complete styling assertions may still fail.

- [ ] **Step 4: Commit the semantic skeleton**

```powershell
git add original-artifact-refined.html styles/mortal-seal-card.css scripts/quota-card.js
git commit -m "refactor: rebuild seal card scene structure"
```

---

### Task 3: Compose the Portrait Scene and Top Seal Mark

**Files:**
- Modify: `styles/mortal-seal-card.css`
- Modify: `original-artifact-refined.html`
- Test: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `.portrait-scene`, `.scene-veil`, `.card-mark`, `#unlockButton`.
- Produces: face-centered background, asymmetric masks, quiet title mark, accessible lock focus state.

- [ ] **Step 1: Add a failing assertion for the confirmed background and non-panel composition**

```powershell
Assert-True ($css.Contains('url("../assets/hanli-nangong-background.png")')) 'Confirmed Han Li and Nangong Wan background must remain active'
Assert-True ($css.Contains('background-position: 51% 48%')) 'Portrait crop must preserve the face-to-face center'
Assert-True (-not $html.Contains('class="data"')) 'Legacy right-side data panel must be removed'
Assert-True (-not $html.Contains('class="core"')) 'Legacy left-side quota panel must be removed'
```

Run the test and expect at least the background-position assertion to fail.

- [ ] **Step 2: Implement the cinematic portrait layer**

Use `cover`, preserve natural skin warmth, and darken only the formation and bottom-reading zones:

```css
.portrait-scene {
  position: absolute;
  inset: 0;
  background: url("../assets/hanli-nangong-background.png") 51% 48% / cover no-repeat;
  filter: saturate(.82) contrast(1.08) brightness(.72);
  transform: scale(1.025);
}
.scene-veil {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 56% 43%, transparent 0 19%, rgba(4,20,22,.06) 34%, rgba(4,20,22,.28) 68%),
    linear-gradient(90deg, rgba(4,20,22,.88) 0%, rgba(4,20,22,.42) 31%, rgba(4,20,22,.08) 59%, rgba(4,20,22,.5) 100%),
    linear-gradient(0deg, rgba(4,20,22,.9) 0%, transparent 46%);
}
```

Style the top-left name as a seal-caption rather than a page heading. Give `#unlockButton` a thin gold sigil border, 28px hit target, and a visible `:focus-visible` outline.

- [ ] **Step 3: Run the contract and verify the portrait assertions pass**

Expected: no legacy panel hooks and confirmed local background crop.

- [ ] **Step 4: Commit the portrait composition**

```powershell
git add original-artifact-refined.html styles/mortal-seal-card.css tests/visual-spec.ps1
git commit -m "style: compose portrait seal scene"
```

---

### Task 4: Build the Overflowing Great Geng Formation and Qingzhu Sword

**Files:**
- Modify: `original-artifact-refined.html`
- Modify: `styles/mortal-seal-card.css`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `.seal-formation`, `.formation-ring--outer|middle|inner`, `.formation-sword`, `.qingzhu-sword`, `--sword-lit` class state.
- Produces: three perspective rings that move independently, twelve stationary sword slots, a jade main sword behind the readable quota number, and out-of-ring sword silhouettes.

- [ ] **Step 1: Add failing structural and movement assertions**

```powershell
Assert-True ($html.Contains('class="formation-ring formation-ring--outer"')) 'Missing outer perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--middle"')) 'Missing middle perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--inner"')) 'Missing inner perspective ring'
Assert-True ($html.Contains('class="qingzhu-sword"')) 'Missing Qingzhu main sword'
Assert-True ($html.Contains('class="stray-sword stray-sword--one"')) 'Missing out-of-ring sword accent'
Assert-True ($css.Contains('.formation-ring--outer {')) 'Outer ring must have its own material rule'
Assert-True (-not $css.Contains('.formation-swords { animation:')) 'Sword slots must remain fixed while rings move'
```

Run and expect failures for new ring and stray-sword hooks.

- [ ] **Step 2: Implement the tilted formation geometry**

Place the visual center near `(104px, 148px)` and intentionally crop the outer formation at the left/bottom card edge:

```css
.seal-formation { position: absolute; left: -22px; top: 54px; width: 246px; height: 198px; perspective: 520px; }
.formation-plane { position: absolute; left: 20px; top: 34px; width: 196px; height: 132px; transform: rotateX(62deg) rotateZ(-9deg); transform-style: preserve-3d; }
.formation-ring { position: absolute; inset: 0; border: 1px solid rgba(113,226,220,.42); border-radius: 50%; box-shadow: inset 0 0 18px rgba(89,217,157,.12), 0 0 15px rgba(113,226,220,.12); }
```

Build the rings from gradients, hairline borders, rune dots, and sparse gold nodes. Use `assets/dageng-sword-array-v2.png` only as a low-opacity material bloom, never as a pasted full vertical illustration.

- [ ] **Step 3: Implement fixed sword slots and the Qingzhu main sword**

Position each sword with `--angle` and `--radius`; use pseudo-elements for the blade so JavaScript only toggles `.is-lit`. The main sword may use a cropped `assets/qingzhu-fengyun-sword-v2.png` texture but must read as a 3D jade blade, remain behind `.quota-eye`, and avoid crossing the `80%` glyphs.

- [ ] **Step 4: Run the contract and verify formation requirements pass**

Expected: exactly three named rings, twelve fixed slots, main sword, and out-of-ring accents.

- [ ] **Step 5: Commit the formation**

```powershell
git add original-artifact-refined.html styles/mortal-seal-card.css tests/visual-spec.ps1
git commit -m "feat: build overflowing Great Geng formation"
```

---

### Task 5: Replace the Meter with a Curved Wind-Thunder Spirit Meridian

**Files:**
- Modify: `original-artifact-refined.html`
- Modify: `styles/mortal-seal-card.css`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `.spirit-meridian`, `.meridian-path`, `.meridian-progress`, `.wind-thunder-wings`, `--used`.
- Produces: a curved SVG progress path from the formation eye to the lower right and a centered horizontal wing marker whose position is derived from `--used`.

- [ ] **Step 1: Add failing spirit-meridian assertions**

```powershell
Assert-True ($html.Contains('class="meridian-path"')) 'Missing curved meridian SVG path'
Assert-True ($html.Contains('class="meridian-progress"')) 'Missing remaining-quota spirit stroke'
Assert-True ($html.Contains('class="wind-thunder-wings"')) 'Missing wing progress marker'
Assert-True ($css.Contains('offset-path: path(')) 'Wing center must follow the curved progress path'
Assert-True ($css.Contains('offset-distance: calc(var(--used) * 100%)')) 'Wing center must track the used quota boundary'
Assert-True ($css.Contains('width: 82px')) 'Wings must retain the confirmed compact horizontal scale'
```

Run and expect the new curved-path assertions to fail.

- [ ] **Step 2: Draw the meridian and place the wing marker**

Use a single shared cubic curve for the SVG stroke and CSS motion path:

```html
<svg class="meridian-lines" viewBox="0 0 300 70" aria-hidden="true">
  <path class="meridian-path" d="M8 22 C90 8 172 58 292 28" pathLength="100" />
  <path class="meridian-progress" d="M8 22 C90 8 172 58 292 28" pathLength="100" />
</svg>
```

```css
.wind-thunder-wings {
  width: 82px;
  height: 38px;
  offset-path: path("M 8 22 C 90 8 172 58 292 28");
  offset-distance: calc(var(--used) * 100%);
  offset-anchor: 50% 50%;
  offset-rotate: 0deg;
  opacity: .72;
}
```

Render `assets/wind-thunder-wings-v2.png` inside an SVG crop or image container with a cyan/silver blend and restrained gold lightning. The wing center—not its left edge—must sit on the used/remaining boundary.

- [ ] **Step 3: Place the used/reset labels away from the wings**

Keep `#used` below the curve’s left side and `8月4日 18:30 重置` below its right endpoint. Use 8–9px utility text with no panel background.

- [ ] **Step 4: Run the contract and verify spirit-meridian assertions pass**

Expected: curved path, marker path binding, compact size, and confirmed local wing texture.

- [ ] **Step 5: Commit the progress artifact**

```powershell
git add original-artifact-refined.html styles/mortal-seal-card.css tests/visual-spec.ps1
git commit -m "feat: turn Wind-Thunder Wings into spirit meridian"
```

---

### Task 6: Implement Quota State, Sword Illumination, and Unlock Behavior

**Files:**
- Modify: `scripts/quota-card.js`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `#widget`, `#percent`, `#used`, `#unlockButton`, `.formation-sword`, `[data-used]`.
- Produces: global `setUsed(value): void`, accessible current-state labels, `is-lit` sword classes, active demo-button state, and preserved unlock toggle.

- [ ] **Step 1: Add failing controller assertions**

```powershell
Assert-True ($js.Contains('Number.isFinite(Number(value))')) 'setUsed must guard non-finite input'
Assert-True ($js.Contains('Math.round(remaining * 12)')) 'Lit sword count must derive from remaining quota'
Assert-True ($js.Contains("sword.classList.toggle('is-lit', index < litSwordCount)")) 'Sword slots must update from the derived count'
Assert-True ($js.Contains('setUsed(Number(button.dataset.used))')) 'Demo controls must use the public updater'
Assert-True ($js.Contains("unlockButton.addEventListener('click'")) 'Unlock button behavior must remain interactive'
```

Run and expect controller assertions to fail against the temporary Task 2 implementation.

- [ ] **Step 2: Implement `setUsed(value)`**

```javascript
function setUsed(value) {
  const numeric = Number.isFinite(Number(value)) ? Number(value) : 0;
  const used = Math.min(1, Math.max(0, numeric));
  const remaining = 1 - used;
  const usedPercent = Math.round(used * 100);
  const remainingPercent = 100 - usedPercent;
  const litSwordCount = Math.round(remaining * 12);

  widget.style.setProperty('--used', used.toFixed(4));
  percent.textContent = `${remainingPercent}%`;
  usedLabel.textContent = `已用 ${usedPercent}%`;
  swords.forEach((sword, index) => sword.classList.toggle('is-lit', index < litSwordCount));
  widget.dataset.usedState = usedPercent >= 70 ? 'danger' : usedPercent >= 40 ? 'warning' : 'calm';
}
```

Expose it with `window.setUsed = setUsed`, initialize with `.2`, and keep a single click listener per demo button. Mark the active button with both `.active` and `aria-pressed="true"`.

- [ ] **Step 3: Preserve unlock-button behavior**

Toggle `aria-pressed`, `.is-unlocked`, and the label between `解锁悬浮窗` and `锁定悬浮窗`; do not open a settings panel.

- [ ] **Step 4: Run the contract and verify all controller assertions pass**

Expected: 20/55/85 inputs calculate 80/45/15 labels and 10/5/2 lit slots from the same function.

- [ ] **Step 5: Commit the state controller**

```powershell
git add scripts/quota-card.js tests/visual-spec.ps1
git commit -m "feat: connect quota state to seal artifacts"
```

---

### Task 7: Choreograph One Entrance Ritual and Restrained Ambient Motion

**Files:**
- Modify: `styles/mortal-seal-card.css`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: portrait, rings, sword slots, meridian, wings, quota eye, spirit seal.
- Produces: one entrance sequence under 1.8s, slow independent ring drift, infrequent wing breath, subtle fog, and static reduced-motion rendering.

- [ ] **Step 1: Add failing motion and accessibility assertions**

```powershell
Assert-True ($css.Contains('@keyframes sealAwaken')) 'Missing one-shot awakening sequence'
Assert-True ($css.Contains('animation: sealAwaken 1.75s')) 'Awakening sequence must stay under 1.8 seconds'
Assert-True ($css.Contains('@media (prefers-reduced-motion: reduce)')) 'Missing reduced-motion media query'
Assert-True ($css.Contains('animation: none !important')) 'Reduced-motion mode must stop continuous motion'
Assert-True ($css.Contains('transition-duration: .001ms !important')) 'Reduced-motion mode must suppress state-transition movement'
```

Run and expect the entrance assertions to fail.

- [ ] **Step 2: Implement the awakening sequence**

Use one root animation for scene reveal and delayed child animations for ring/sword/meridian opacity only. Total delay plus duration must not exceed 1.75s. Do not loop the entrance.

- [ ] **Step 3: Implement restrained ambient motion**

Use outer ring drift around 48s, middle ring reverse drift around 41s, core breath around 7s, fog drift around 28s, and one wing flex around every 5.5s. Do not animate all swords vertically; lit swords may receive only a static glow plus a rare specular sweep.

- [ ] **Step 4: Implement reduced-motion fallback**

Inside `@media (prefers-reduced-motion: reduce)`, set all card pseudo-elements and descendants to `animation: none !important` and `transition-duration: .001ms !important`; preserve the current `--used`-derived offset position.

- [ ] **Step 5: Run the full contract and verify it passes**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

Expected: `PASS: mortal seal scroll structure, state interfaces, and local assets satisfy the visual contract.`

- [ ] **Step 6: Commit the motion pass**

```powershell
git add styles/mortal-seal-card.css tests/visual-spec.ps1
git commit -m "style: choreograph formation awakening"
```

---

### Task 8: Verify Real Geometry, Responsive Display, and Browser Quality

**Files:**
- Modify: `styles/mortal-seal-card.css` only if verification exposes a defect.
- Modify: `scripts/quota-card.js` only if real state behavior is wrong.
- Create: `artifacts/mortal-seal-scroll-wide.png`
- Create: `artifacts/mortal-seal-scroll-narrow.png`
- Test: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: finished page at `http://127.0.0.1:55569/original-artifact-refined.html`.
- Produces: fresh test output, HTTP 200, clean console, state geometry evidence, two screenshots, and a reviewable browser tab left open on the final design.

- [ ] **Step 1: Run the full static contract from a clean status check**

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

Expected: only intended worktree changes and a passing contract.

- [ ] **Step 2: Verify the local preview is reachable**

Start the existing static server only if port 55569 is not already serving this checkout, then request:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:55569/original-artifact-refined.html | Select-Object StatusCode
```

Expected: `StatusCode 200`.

- [ ] **Step 3: Verify the three quota states in the browser**

For 20%, 55%, and 85% used, inspect:

- `#percent` text: `80%`, `45%`, `15%`.
- `.formation-sword.is-lit` count: `10`, `5`, `2`.
- `#used` text: `已用 20%`, `已用 55%`, `已用 85%`.
- Wing center and SVG meridian boundary center differ by no more than `1px` in both axes.
- The five-hour seal remains `58%` in every state.

- [ ] **Step 4: Verify visual hierarchy at 1089 × 792 and 523 × 792**

Confirm the first focal point is the quota eye, both faces remain readable, there is no legacy panel split, the formation visibly crosses its normal bounds, the page has no horizontal overflow, and the card is entirely visible in the display stage.

- [ ] **Step 5: Verify reduced motion and browser console**

Emulate `prefers-reduced-motion: reduce`, confirm ring, wing, fog, lightning, and entrance animations report `none`, and confirm the console has no errors.

- [ ] **Step 6: Save final screenshots**

Save the desktop and narrow viewport captures to:

```text
artifacts/mortal-seal-scroll-wide.png
artifacts/mortal-seal-scroll-narrow.png
```

- [ ] **Step 7: Commit the verified deliverable**

```powershell
git add original-artifact-refined.html styles/mortal-seal-card.css scripts/quota-card.js tests/visual-spec.ps1 artifacts/mortal-seal-scroll-wide.png artifacts/mortal-seal-scroll-narrow.png
git commit -m "feat: deliver mortal seal scroll quota card"
```

---

## Self-Review Record

- Spec coverage: every composition, palette, typography, motion, state, accessibility, responsive, and verification requirement is assigned to Tasks 1–8.
- Placeholder scan: every implementation step contains concrete markup, styles, script behavior, commands, and expected outcomes.
- Interface consistency: `setUsed(value)`, `#widget`, `#percent`, `#used`, `.formation-sword`, `.is-lit`, `[data-used]`, and `--used` retain identical spelling in tests, markup, styling, and controller steps.
- Scope control: no real API, installer, upload/settings panel, external dependency, or `index.html` change is included.
