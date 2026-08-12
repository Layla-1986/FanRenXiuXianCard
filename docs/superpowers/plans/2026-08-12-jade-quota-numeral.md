# 青玉灵数融合 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将七日余量数字做成与大庚剑阵同源的青玉灵力材质，并让数字、阵眼聚光和点亮剑身随三档额度同步变色。

**Architecture:** 保持现有 HTML、`setUsed(value)` 和阵眼坐标不变，仅在 `.seal-card` 上定义一组状态颜色变量。`data-used-state` 负责切换变量，数字渐变、阵眼光晕和点亮剑身统一消费这些变量；减少动态效果媒体查询关闭新增呼吸动画。

**Tech Stack:** HTML5、CSS 自定义属性与渐变、原生 JavaScript、PowerShell 视觉契约测试。

## Global Constraints

- 不改变 480 × 270 卡片尺寸、阵眼位置、38px 数字尺寸、人物背景和右侧账本布局。
- 保留 `setUsed()`、三个演示按钮、右上角解锁按钮和 `US$39.36` 余额显示。
- 不新增网络字体或外部依赖，使用本机衬线字体回退。
- 人物面部区域不得新增光效覆盖。
- `prefers-reduced-motion: reduce` 下停止新增的材质呼吸动画。

---

### Task 1: 青玉灵力共享色彩系统

**Files:**
- Modify: `tests/visual-spec.ps1:93-112`
- Modify: `styles/mortal-seal-card.css:173-183, 502-528, 615-635, 714-721`

**Interfaces:**
- Consumes: `.seal-card[data-used-state="calm|warning|danger"]`，由现有 `setUsed(value)` 设置。
- Produces: `--spirit-highlight`、`--spirit-jade`、`--spirit-gold`、`--spirit-shadow`、`--spirit-glow` 五个卡片级 CSS 变量。

- [ ] **Step 1: 写共享色彩变量的失败测试**

在 `tests/visual-spec.ps1` 增加以下断言：

```powershell
Assert-True ($css.Contains('--spirit-highlight:')) 'Card must expose a shared spirit highlight color'
Assert-True ($css.Contains('--spirit-jade:')) 'Card must expose a shared jade body color'
Assert-True ($css.Contains('--spirit-gold:')) 'Card must expose a shared gold reflection color'
Assert-True ($css.Contains('--spirit-shadow:')) 'Card must expose a shared dark outline color'
Assert-True ($css.Contains('--spirit-glow:')) 'Card must expose a shared spirit glow color'
Assert-True ($css.Contains('.seal-card[data-used-state="warning"] {')) 'Warning state must override shared spirit colors'
Assert-True ($css.Contains('.seal-card[data-used-state="danger"] {')) 'Danger state must override shared spirit colors'
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tests\visual-spec.ps1'`

Expected: FAIL，提示缺少共享灵力颜色和 warning/danger 覆盖。

- [ ] **Step 3: 定义三档灵力色变量**

在 `.seal-card` 中加入 calm 默认变量，并用两个状态选择器覆盖：

```css
.seal-card {
  --spirit-highlight: #edf9ed;
  --spirit-jade: #75d9b6;
  --spirit-gold: #d7bd70;
  --spirit-shadow: #123f39;
  --spirit-glow: rgba(94, 221, 181, .38);
}

.seal-card[data-used-state="warning"] {
  --spirit-highlight: #e8efcf;
  --spirit-jade: #79bf8c;
  --spirit-gold: #d3ad59;
  --spirit-shadow: #3d4b31;
  --spirit-glow: rgba(190, 177, 89, .34);
}

.seal-card[data-used-state="danger"] {
  --spirit-highlight: #dbc889;
  --spirit-jade: #778d62;
  --spirit-gold: #b88842;
  --spirit-shadow: #493820;
  --spirit-glow: rgba(177, 128, 57, .28);
}
```

- [ ] **Step 4: 让点亮剑身消费共享变量**

将 `.formation-sword::before` 的高光材质和 `.formation-sword.is-lit` 的滤镜改为使用 `--spirit-highlight`、`--spirit-jade` 与 `--spirit-glow`；未点亮剑的 `.formation-sword` 透明度保持 `.05`。

- [ ] **Step 5: 运行测试并确认通过**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tests\visual-spec.ps1'`

Expected: PASS。

- [ ] **Step 6: 提交共享色彩系统**

```powershell
git add -- 'styles/mortal-seal-card.css' 'tests/visual-spec.ps1'
git commit -m '建立青玉灵力共享色彩系统'
```

### Task 2: 青玉数字材质与阵眼聚光

**Files:**
- Modify: `tests/visual-spec.ps1:93-120`
- Modify: `styles/mortal-seal-card.css:615-635, 780-840, 930-950`

**Interfaces:**
- Consumes: Task 1 的五个 `--spirit-*` CSS 变量。
- Produces: `.quota-eye strong` 青玉渐变文字、`.quota-aura` 阵眼聚光、`@keyframes jadeNumeralBreathe`。

- [ ] **Step 1: 写数字材质的失败测试**

在 `tests/visual-spec.ps1` 增加：

```powershell
Assert-True ($css.Contains('font-family: Baskerville, "Times New Roman", Georgia, serif')) 'Quota numeral must use the restrained classical serif stack'
Assert-True ($css.Contains('background-clip: text')) 'Quota numeral must render its jade material inside the glyphs'
Assert-True ($css.Contains('-webkit-text-fill-color: transparent')) 'Quota numeral must expose the jade gradient instead of flat white'
Assert-True ($css.Contains('paint-order: stroke fill')) 'Quota numeral must keep a fine dark jade outline'
Assert-True ($css.Contains('stroke: var(--spirit-shadow)')) 'Quota numeral outline must share the spirit shadow color'
Assert-True ($css.Contains('@keyframes jadeNumeralBreathe')) 'Quota numeral must have a restrained material breathing animation'
Assert-True ($css.Contains('animation: jadeNumeralBreathe')) 'Quota numeral must use the material breathing animation'
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tests\visual-spec.ps1'`

Expected: FAIL，提示渐变文字、描边与呼吸动画尚未实现。

- [ ] **Step 3: 实现青玉数字材质**

保持 `font-size: 38px` 和当前定位不变，将 `.quota-eye strong` 的字体与材质改为：

```css
.quota-eye strong {
  color: var(--spirit-highlight);
  font-family: Baskerville, "Times New Roman", Georgia, serif;
  background: linear-gradient(180deg,
    var(--spirit-highlight) 0 24%,
    var(--spirit-jade) 52% 76%,
    var(--spirit-gold) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  -webkit-text-stroke: .45px var(--spirit-shadow);
  paint-order: stroke fill;
  stroke: var(--spirit-shadow);
  text-shadow: 0 2px 7px rgba(0, 0, 0, .72), 0 0 9px var(--spirit-glow);
  animation: jadeNumeralBreathe 6.8s ease-in-out infinite;
}
```

- [ ] **Step 4: 将阵眼光晕改为共享色聚光**

调整 `.quota-aura`：中心使用 `--spirit-glow`，外围仍回落到深墨色；保持 112 × 82px，不扩大到人物面部区域。

- [ ] **Step 5: 添加克制的材质呼吸**

```css
@keyframes jadeNumeralBreathe {
  0%, 100% { filter: saturate(.92) brightness(.98); }
  50% { filter: saturate(1.06) brightness(1.06); }
}
```

在现有 `@media (prefers-reduced-motion: reduce)` 规则中依靠 `.seal-card * { animation: none !important; }` 关闭动画，并保留渐变与描边。

- [ ] **Step 6: 运行测试并确认通过**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tests\visual-spec.ps1'`

Expected: PASS。

- [ ] **Step 7: 提交数字材质**

```powershell
git add -- 'styles/mortal-seal-card.css' 'tests/visual-spec.ps1'
git commit -m '融合青玉灵数与大庚剑阵材质'
```

### Task 3: 三档状态视觉回归验证

**Files:**
- Modify: `tests/visual-spec.ps1:110-130`（仅在发现契约缺口时）
- Verify: `original-artifact-refined.html`
- Verify: `scripts/quota-card.js`
- Verify: `styles/mortal-seal-card.css`

**Interfaces:**
- Consumes: `window.setUsed(value)`、`data-used-state`、共享灵力变量。
- Produces: 无新接口；交付三档状态一致的视觉效果。

- [ ] **Step 1: 运行完整视觉契约测试**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tests\visual-spec.ps1'`

Expected: PASS，且无接口或结构回归。

- [ ] **Step 2: 检查改动边界与格式**

Run: `git diff --check`

Expected: exit 0；允许 Git 提示未来将 LF 转为 CRLF，但不得有空白错误。

- [ ] **Step 3: 检查三档状态映射仍然存在**

Run: `rg -n "data-used-state|usedPercent >= 70|usedPercent >= 40|Math.round\(remaining \* 12\)" scripts\quota-card.js styles\mortal-seal-card.css`

Expected: JavaScript 仍以 40% 和 70% 已用量划分 calm、warning、danger，并继续由余量计算十二柄剑的点亮数量。

- [ ] **Step 4: 在页面依次检查三个演示状态**

在现有设计稿中依次选择已用 20%、55%、85%，确认：

- 80% 为月白青玉，剑身清亮青绿；
- 45% 为青玉夹金，剑身同步转暖；
- 15% 为暗金青铜并保留微弱青光；
- 三种数字位置与字号不变，人物面部无新增光效遮挡。

- [ ] **Step 5: 最终提交（仅在 Task 3 产生额外修正时）**

```powershell
git add -- 'styles/mortal-seal-card.css' 'tests/visual-spec.ps1'
git commit -m '校准青玉灵数三档状态'
```
