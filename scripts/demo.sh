#!/bin/bash

# 智检通 - 演示脚本
# 用于快速启动系统进行演示

echo "=========================================="
echo "  智检通 - 工程质量检测分析智能体系统"
echo "  演示启动脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.10+"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt -q

# 创建必要目录
mkdir -p data/standards
mkdir -p model/finetuned
mkdir -p logs

# 启动应用
echo ""
echo "启动Streamlit应用..."
echo "访问地址: http://localhost:8501"
echo ""

streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
