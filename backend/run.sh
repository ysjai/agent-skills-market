#!/bin/bash
set -e

cd "$(dirname "$0")"

# 检查 .env 是否存在
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在"
    echo "请先运行: cp .env.example .env"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python -m venv .venv
fi

# 激活虚拟环境并启动
source .venv/bin/activate

echo "启动 Agent Skills Manager 后端服务..."
echo "API: http://localhost:8000"
echo "文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo ""

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
