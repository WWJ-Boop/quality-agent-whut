# 智检通 — 面向工程质量检测的多智能体分析系统

> 第二届武汉理工大学中国研究生智能建造创新大赛参赛作品
> 赛道：工程大模型 Agent 智能应用系统设计

## 项目简介

"智检通"是一个面向工程质量检测领域的AI智能体系统，结合大模型微调、RAG知识库和多智能体编排技术，实现工程质量检测全流程的智能化辅助。

### 核心功能

- **智能报告分析**：自动解析检测报告PDF/Excel，提取关键指标，判断合格性
- **标准知识问答**：基于RAG的工程质量标准智能检索与问答
- **质量趋势分析**：基于历史检测数据分析趋势并预警
- **报告自动生成**：根据检测数据自动生成规范报告

### 技术亮点

1. **领域模型微调**：基于Qwen2.5-7B进行QLoRA微调，适配工程质量检测领域
2. **RAG知识库**：集成30+份国家标准/行业规范，支持精准检索
3. **多Agent协同**：4个专项Agent + 协调路由，展现Agent编排能力
4. **端到端覆盖**：从数据→模型→知识库→Agent→应用的完整链路

## 快速开始

### 环境要求

- Python 3.10+
- CUDA 11.8+ (GPU显存 >= 16GB，推荐24GB+)
- 内存 >= 32GB

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd quality-inspection-agent

# 创建虚拟环境
conda create -n quality-agent python=3.10
conda activate quality-agent

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env
# 编辑 .env 填写必要配置
```

### 运行

```bash
# 1. 下载模型
python scripts/download_model.py

# 2. 初始化知识库 (首次运行)
python scripts/init_db.py

# 3. 启动应用
streamlit run app/main.py
```

访问 http://localhost:8501 即可使用。

## Streamlit Cloud 部署

本项目支持部署到 [Streamlit Cloud](https://streamlit.io/cloud) 进行在线演示。

### 部署步骤

1. **Fork 或 Push 项目到 GitHub**
   ```bash
   git remote add origin https://github.com/<your-username>/quality-inspection-agent.git
   git push -u origin master
   ```

2. **登录 Streamlit Cloud**
   访问 https://share.streamlit.io 并使用 GitHub 账号登录

3. **部署应用**
   - Repository: 选择你的仓库
   - Branch: `master`
   - Main file path: `app/main.py`
   - 点击 "Deploy!"

### 云端运行说明

Streamlit Cloud 版本为**演示模式**，与本地部署的区别：

| 功能 | 本地部署 | Streamlit Cloud |
|------|---------|----------------|
| 报告分析 (PDF解析) | 完整功能 | 完整功能 |
| 趋势分析 (图表) | 完整功能 | 完整功能 |
| 报告生成 | 完整功能 | 完整功能 |
| 标准问答 (RAG) | 需要 Milvus + Embedding 模型 | 基于规则的演示回复 |
| LLM 推理 | 本地模型 / API | 无需 API 的演示回复 |

- 无 GPU 和模型权重时，系统自动切换到**演示模式**，使用内置规则引擎生成回复
- 如需完整 LLM 能力，可在 Streamlit Cloud 的 Secrets 中配置 `OPENAI_API_KEY`

### 环境变量配置（可选）

在 Streamlit Cloud 的 "Secrets" 中添加：

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

## 项目结构

```
quality-inspection-agent/
├── config/          # 配置文件
├── data/            # 数据目录
│   ├── standards/   # 工程质量标准文档
│   ├── reports/     # 示例检测报告
│   └── training/    # 微调训练数据
├── model/           # 模型相关
│   ├── finetune/    # 微调脚本
│   └── inference/   # 推理服务
├── knowledge/       # RAG知识库模块
├── agents/          # 智能体模块
│   └── tools/       # Agent工具集
├── app/             # Streamlit前端
│   ├── pages/       # 功能页面
│   └── components/  # UI组件
└── scripts/         # 工具脚本
```

## 模型微调

### 训练数据格式

```json
{"instruction": "混凝土试块28天抗压强度检测值为28.5MPa，设计强度等级C30，是否合格？", "output": "根据GB/T 50107-2010..."}
```

### 执行微调

```bash
# 准备训练数据
python model/finetune/prepare_data.py

# 执行QLoRA微调
python model/finetune/finetune_qlora.py

# 合并LoRA权重
python model/finetune/merge_model.py

# 评估模型
python model/finetune/evaluate.py
```

## 知识库构建

支持的标准文档：
- GB/T 50081 混凝土力学性能试验方法标准
- GB/T 228.1 金属材料拉伸试验
- GB/T 50107 混凝土强度检验评定标准
- GB 50204 混凝土结构工程施工质量验收规范
- JGJ/T 23 回弹法检测混凝土抗压强度技术规程
- 以及更多...

```bash
# 初始化知识库
python scripts/init_db.py

# 添加新文档
python scripts/init_db.py --add-doc path/to/document.pdf
```

## Agent架构

系统采用多Agent协同架构：

- **协调Agent**：接收用户输入，识别意图，路由到对应专项Agent
- **报告分析Agent**：解析检测报告，提取指标，判定合格性
- **标准问答Agent**：检索知识库，回答标准相关问题
- **趋势分析Agent**：分析历史数据，生成图表，预测趋势

## 作者

- 参赛单位：武汉理工大学
- 指导教师：[待填写]
- 团队成员：[待填写]

## 许可证

本项目仅供学术交流使用。
