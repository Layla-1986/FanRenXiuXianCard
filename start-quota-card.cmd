@echo off
setlocal EnableExtensions
cd /d "%~dp0"
start "" /b python antigravity_quota.py --port 8765
for /L %%I in (1,1,30) do (
  powershell.exe -NoLogo -NoProfile -NonInteractive -Command "try { $response = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8765/api/antigravity-quota' -TimeoutSec 2; if ($response.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
  if not errorlevel 1 goto ready
  timeout /t 1 /nobreak >nul
)
echo Antigravity quota companion did not become ready within 30 seconds.
exit /b 1

:ready
start "" "http://127.0.0.1:8765/original-artifact-refined.html"
