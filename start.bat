@echo off
chcp 65001 >nul
echo ==========================================
echo   智检通 - 工程质量检测分析智能体系统
echo   启动中...
echo ==========================================
echo.

:: 获取本机IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4" ^| findstr /v "127.0.0.1"') do (
    set "IP=%%a"
    goto :found_ip
)
:found_ip
set IP=%IP: =%

echo [1/2] 启动Streamlit服务...
echo.
echo   本机访问:  http://localhost:8501
echo   局域网访问: http://%IP%:8501
echo.
echo   其他电脑在浏览器输入: http://%IP%:8501
echo.
echo ==========================================
echo   按 Ctrl+C 停止服务
echo ==========================================
echo.

cd /d "%~dp0"
python -m streamlit run app/main.py
pause
