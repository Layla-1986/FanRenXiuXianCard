# 剑阵账簿对齐与玩梗题跋 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让左侧大庚剑阵阵眼与右侧额度账簿共享水平视觉中轴，并加入「念头通达」「炖煮红尘」双题跋。

**Architecture:** 继续使用现有静态 HTML、集中式 CSS 和 `setUsed(value)` 控制器。对齐由 `.seal-card` 上的共享 CSS 变量驱动，文案仅替换现有辅助文本，不新增组件或脚本接口。

**Tech Stack:** HTML5、CSS 自定义属性、PowerShell 视觉契约测试

## Global Constraints

- 保持卡片精确尺寸 480 × 270px。
- 保持 `setUsed(value)`、三个状态按钮、账户余额和解锁按钮接口不变。
- 玩梗文案必须使用「炖煮红尘」，不替换为「遁出红尘」。
- 本轮不增加持续动画。

---

### Task 1: 建立剑阵与账簿共享中轴

**Files:**
- Modify: `tests/visual-spec.ps1`
- Modify: `styles/mortal-seal-card.css`

**Interfaces:**
- Consumes: `.seal-card`、`.quota-eye`、`.quota-ledger`
- Produces: `--content-axis-y` 共享中轴变量

- [ ] **Step 1: Write the failing test**

在视觉契约中断言 CSS 包含 `--content-axis-y: 168px`，并且 `.quota-ledger` 的中心位置通过 `top: var(--content-axis-y)` 与 `transform: translateY(-50%)` 派生。

- [ ] **Step 2: Run test to verify it fails**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: FAIL，提示缺少共享信息中轴或账簿未从中轴派生。

- [ ] **Step 3: Write minimal implementation**

在 `.seal-card` 中加入 `--content-axis-y: 168px`；让 `--formation-eye-y` 引用该变量；让 `.quota-ledger` 使用同一变量定位并垂直居中，同时保留 `right: 18px` 与 `width: 136px`。

- [ ] **Step 4: Run test to verify it passes**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: PASS。

### Task 2: 加入双题跋并精简页首文案

**Files:**
- Modify: `tests/visual-spec.ps1`
- Modify: `original-artifact-refined.html`
- Modify: `styles/mortal-seal-card.css`

**Interfaces:**
- Consumes: `.card-foot` 现有底部区域
- Produces: `.mortal-motto` 两个题跋文本节点

- [ ] **Step 1: Write the failing test**

断言 HTML 中存在且仅存在「念头通达」与「炖煮红尘」两条 `.mortal-motto`，并断言 CSS 为题跋提供低亮度青玉色、楷体和疏朗字距。

- [ ] **Step 2: Run test to verify it fails**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: FAIL，提示缺少玩梗题跋。

- [ ] **Step 3: Write minimal implementation**

将 `.card-foot` 两个现有文本替换为 `<span class="mortal-motto">念头通达</span>` 与 `<span class="mortal-motto">炖煮红尘</span>`；调整底部左右边界，使其与阵眼和账簿区域呼应；精简页首说明但不改变卡片主数据。

- [ ] **Step 4: Run test to verify it passes**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: PASS。

### Task 3: 完整回归验证

**Files:**
- Verify: `original-artifact-refined.html`
- Verify: `styles/mortal-seal-card.css`
- Verify: `scripts/quota-card.js`

**Interfaces:**
- Consumes: 本计划所有改动
- Produces: 可交付的静态设计稿

- [ ] **Step 1: Run complete visual contract**

Run: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: `PASS: mortal seal scroll structure, state interfaces, and local assets satisfy the visual contract.`

- [ ] **Step 2: Check patch integrity**

Run: `git diff --check`

Expected: 无输出且退出码为 0。

- [ ] **Step 3: Commit implementation**

提交测试、HTML 与 CSS 修改，提交信息为 `对齐剑阵账簿并加入凡人题跋`。
