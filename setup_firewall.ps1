# 智检通 - 防火墙配置脚本
# 以管理员身份运行此脚本，允许其他电脑访问

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  配置防火墙规则 - 允许局域网访问" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否以管理员身份运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "请以管理员身份运行此脚本!" -ForegroundColor Red
    Write-Host "右键点击 PowerShell -> 以管理员身份运行" -ForegroundColor Yellow
    pause
    exit
}

# 删除旧规则（如果存在）
netsh advfirewall firewall delete rule name="QualityAgent-Streamlit" 2>$null

# 添加入站规则
netsh advfirewall firewall add rule name="QualityAgent-Streamlit" ^
    dir=in action=allow protocol=TCP localport=8501

Write-Host ""
Write-Host "防火墙规则已添加!" -ForegroundColor Green
Write-Host "端口 8501 已开放，其他电脑可以通过局域网访问。" -ForegroundColor Green
Write-Host ""

# 显示本机IP
Write-Host "本机IP地址:" -ForegroundColor Yellow
ipconfig | Select-String "IPv4"
Write-Host ""
Write-Host "其他电脑在浏览器输入: http://<本机IP>:8501" -ForegroundColor Cyan
Write-Host ""
pause
