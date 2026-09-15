# 凡人额度卡

一款面向 Windows 10/11 的 Codex 与 Antigravity 额度悬浮卡。应用保持在桌面最上层，提供双页额度展示、位置锁定、鼠标穿透、托盘控制和可选开机自启。

![凡人额度卡 Codex 页面](docs/images/mortal-quota-card-codex.png)

## 下载与安装

当前版本：**1.0.0**

直接下载仓库中的 [`凡人额度卡-Setup-1.0.0.exe`](artifacts/installer/凡人额度卡-Setup-1.0.0.exe)，双击后按提示安装。安装程序面向当前用户，无需管理员权限，并会创建桌面快捷方式、开始菜单项和卸载入口。

安装包 SHA-256：

```text
5C30ED3108ED07927846481E0695D19A692BD26094B72AB52969C682A9B2E11F
```

运行环境：Windows 10/11 x64，系统需具备 Microsoft Edge WebView2 Runtime。Windows 11 通常已预装。

## 使用方法

- 拖动卡片空白区域可调整位置。
- 点击右上角 **“引”** 在 Codex 与 Antigravity 两页之间切换。
- 点击锁形按钮后，卡片位置被锁定并启用鼠标穿透。
- 按 `Ctrl+Alt+L`，或从系统托盘选择“解锁”，即可恢复操作。
- 托盘菜单可显示或隐藏卡片、锁定或解锁、切换开机自启，以及退出应用。

应用会保存窗口位置和当前页面；每次启动保持解锁，避免窗口锁定后无法操作。高 DPI 屏幕会自动调整原生窗口尺寸，保证整张卡片完整显示。

更详细的操作说明与故障排查见 [使用指南](docs/USER_GUIDE.md)。

## 数据来源

### Codex

应用优先通过本机 `codex app-server` 的只读接口获取：

- 5 小时额度及重置时间；
- 7 天额度及重置时间；
- 账户余额；
- 可用重置卡数量及最近到期时间。

服务不可用时会回退到本地会话记录。回退状态下仍显示能够确认的额度和余额，重置卡信息会明确标记为“待同步”。应用不会消耗重置卡。

### Antigravity

应用每 60 秒只读检查已经打开的英文 `Settings - Models` 页面，读取 Available AI Credits、Gemini 与 Claude/GPT 的周额度和 5 小时额度。它不会主动打开设置、切换页面或抢占 Antigravity 焦点。

## 隐私与网络边界

- 本地服务仅监听随机的 `127.0.0.1` 端口。
- 不读取或保存 Cookie、令牌、邮箱、账号标识、聊天内容和网络流量。
- 不复制 Codex 登录凭据。
- 缓存和设置保存在 `%LOCALAPPDATA%\MortalQuotaCard`。
- 静态服务采用文件白名单，不会对外提供项目源码、配置、缓存或测试文件。

## 从源码运行

安装 Python 3.11 或更高版本后：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
.\.venv\Scripts\python.exe quota_card_app.py
```

若只需运行浏览器原型：

```powershell
python antigravity_quota.py --port 8765
```

随后打开 `http://127.0.0.1:8765/original-artifact-refined.html`。

## 测试

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
node tests/quota-card-runtime.test.js
node tests/quota-card-formal-v1.test.js
node tests/quota-card-app.test.js
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

当前正式构建已通过 37 项 Python 测试、3 组 JavaScript 页面测试和视觉规格检查，并在 150% Windows 缩放下验证完整显示、页面切换、锁定与解锁后拖动。

## 构建安装包

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

构建脚本会创建隔离环境，使用 PyInstaller 生成目录式应用，再调用 Inno Setup 6 输出当前用户安装包。正式视觉入口由 `scripts/build-formal-v1.py` 从两份已确认概念稿生成，请重新运行构建脚本，不要直接修改生成后的页面。

## 项目结构

```text
mortal_quota/                 Codex 数据读取与 Windows 桌面控制
quota_card_app.py             桌面应用入口
antigravity_quota.py          本地只读服务与 Antigravity 数据读取
scripts/build-formal-v1.py    正式双页卡片生成器
scripts/quota-card-app.js     实时数据绑定与桌面桥接
installer/                    Inno Setup 安装配置
tests/                        Python、JavaScript 与视觉检查
artifacts/installer/          可直接安装的 1.0.0 安装包
```

## 当前范围

1.0.0 不包含自动更新、云同步、重置卡消耗和代码签名。
