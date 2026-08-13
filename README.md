# 凡人法宝额度卡

480 × 270 的本地桌面额度卡，包含两页：

- Codex：七日额度、大庚剑阵、账户美元余额。
- Antigravity：Available AI Credits、Gemini 与 Claude/GPT 的周额度和五小时额度。

## 启动

在项目目录运行：

```powershell
python antigravity_quota.py --port 8765
```

然后打开：

```text
http://127.0.0.1:8765/original-artifact-refined.html
```

右上角“引”字反重力印用于切换页面；旁边仍是原有解锁按钮。页面每 60 秒读取一次本地接口。

## Antigravity 同步条件

1. Antigravity IDE 已经运行。
2. 英文版 `Settings - Models` 页面已经由用户打开。
3. 伴随服务只做 Windows UI Automation 只读检查；不会主动打开设置、切换页面、激活或聚焦 Antigravity。

页面没有打开时保留最近一次成功值并显示“待同步”；10 分钟未更新显示“同步已滞后”；24 小时未更新隐藏百分比并提示重新打开 Models 页同步。

## 隐私边界

- 服务只监听 `127.0.0.1`。
- 不读取 Cookie、令牌、邮箱、账号标识、聊天内容或网络流量。
- 不保存完整辅助功能树或窗口文字。
- 缓存与 API 只包含五项额度、同步时间、来源和状态。

接口：

```text
GET /api/antigravity-quota
```

本地缓存 `.antigravity-quota-cache.json` 已排除在 Git 之外。

## 测试

```powershell
python -m unittest tests.test_antigravity_quota -v
node tests/quota-card-runtime.test.js
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```
