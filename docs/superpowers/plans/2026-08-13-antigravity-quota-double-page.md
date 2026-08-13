# Antigravity 账户额度双页展示

## Task 1: 本地只读采集器与伴随服务

- 新增 Windows UI Automation 一次性采集器，只读取已经打开的 Antigravity `Settings - Models` 页面，不打开页面、不聚焦窗口、不读取网络、Cookie、令牌、邮箱、聊天内容或保留完整窗口文本。
- 新增仅监听 `127.0.0.1` 的本地伴随服务，提供静态卡片与 `GET /api/antigravity-quota`。
- 每 60 秒采集；页面不存在时保留旧值并返回 `pending`；10 分钟后 `stale`；24 小时后 `expired`。
- 接口只返回 `source`、`syncedAt`、`status`、`aiCredits`、`gemini.weeklyRemaining`、`gemini.fiveHourRemaining`、`claudeGpt.weeklyRemaining`、`claudeGpt.fiveHourRemaining`。
- 用自动化测试覆盖 0、100、缺失值、非法值、状态衰减、缓存保留与敏感字段过滤。

## Task 2: 卡片双页界面

- 保持现有 Codex 页、剑阵、`setUsed(value)`、三档演示按钮与解锁按钮行为不变。
- 在右上角解锁按钮旁增加“反重力印”，以短暂卷轴淡入切换 Antigravity 页，不翻转卡片。
- 新页展示 AI Credits、Gemini 周额度与五小时额度、Claude and GPT 周额度与五小时额度、同步时间和 fresh/pending/stale/expired 状态。
- 两组模型额度使用上下两层法阵账簿；480×270 内不得遮挡或溢出。
- 新鲜数据正常展示；超过 24 小时隐藏百分比并提示打开 Models 页同步；请求失败不显示 NaN。
- 页面会话内记住上次查看页；全新浏览器会话默认 Codex。

## Task 3: 集成、文档与回归

- 更新 README，说明启动方式、隐私边界与同步条件。
- 执行 Python 单元测试、PowerShell 视觉契约、JavaScript 语法检查、HTTP 接口检查与 Git diff 检查。
- 在本地服务中验证 Codex 与 Antigravity 双页切换，并保留 80%/45%/15% 剑阵回归。
