# 企业AI成熟度分析系统

## 🚀 在线演示

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/YOUR_USERNAME/pwc_ai_strategy/main/ai_maturity_dashboard.py)

> **提示**：点击上方链接直接体验完整的交互式看板，或按照下方说明在本地运行。

---

## 项目简介

这是一个专业的企业AI成熟度分析系统，帮助企业管理层和咨询顾问评估企业AI成熟度水平，制定数字化转型路线图。

## 功能特点

### 📊 Streamlit交互式看板
- **总体概览**：企业成熟度分布、行业对比、关键指标
- **企业详情**：单个企业六大维度雷达图、详细评分
- **行业对比**：行业间成熟度对比、维度分析
- **优先级矩阵**：基于Impact/Effort的举措优先级分析
- **路线图**：个性化三阶段转型路线图
- **数据筛选**：按行业、规模、成熟度等级筛选

### 📄 专业分析报告
- **执行摘要**：核心发现和关键洞察
- **数据概览**：统计分析、分布情况
- **关键发现**：差距分析、问题识别
- **模型结果**：成熟度模型、预测分析
- **建议措施**：具体行动方案、实施路径

### 🎯 数据模型
- **六大维度评估**：战略与愿景、数据基础、技术能力、人才与组织、治理与伦理、文化与创新
- **五级成熟度模型**：观望者(L1)、起步者(L2)、探索者(L3)、加速者(L4)、领先者(L5)
- **优先级算法**：基于影响力、投入度和差距的优先级评分
- **路线图规划**：三阶段实施策略（基础期、建设期、优化期）

## 安装和运行

### 1. 环境要求
- Python 3.8+
- 8GB+ 内存
- 依赖包：streamlit, pandas, numpy, plotly

### 2. 安装依赖
```bash
pip install streamlit pandas numpy plotly markdown
```

### 3. 一键运行
```bash
python run_analysis.py
```

这将自动：
- 检查依赖是否安装
- 执行数据处理和分析
- 生成HTML和Markdown报告
- 启动Streamlit看板（可选）

### 4. 单独运行

#### 仅生成报告
```bash
python report_generator.py
```

#### 启动Streamlit看板
```bash
streamlit run ai_maturity_dashboard.py
```

## 数据文件

### 输入数据
- `ai_initiatives.csv` - AI倡议列表（14项举措）
- `ai_maturity_benchmarks.csv` - 行业基准数据
- `ai_maturity_companies.csv` - 企业原始数据（49家企业）

### 输出文件
- `ai_maturity_scores.csv` - 企业维度得分
- `ai_maturity_gaps.csv` - 差距分析结果
- `ai_maturity_recommendations.csv` - 优先级推荐
- `roadmaps.json` - 个性化路线图
- `analysis_report.html` - HTML格式报告
- `analysis_report.md` - Markdown格式报告

## 使用指南

### 1. 浏览看板
1. 运行 `python run_analysis.py`
2. 选择"1"启动看板
3. 在浏览器中访问 http://localhost:8501
4. 使用侧边栏筛选器查看特定数据

### 2. 查看报告
生成的HTML报告可在浏览器中直接打开，或嵌入到企业演示文档中。

### 3. 导出数据
看板提供数据导出功能，可导出Excel格式的分析结果。

## 分析维度说明

### 战略与愿景 (20%)
- AI战略清晰度
- 高管支持度
- 业务对齐度

### 数据基础 (20%)
- 数据质量
- 数据治理
- 数据开放性

### 技术能力 (15%)
- 基础设施就绪度
- MLOps成熟度
- AI平台能力

### 人才与组织 (15%)
- AI人才密度
- 跨部门协作
- 培训体系

### 治理与伦理 (15%)
- AI治理框架
- 风险管控
- 伦理合规

### 文化与创新 (15%)
- 数据驱动文化
- 创新机制
- 容错与试错

## 成熟度等级

| 等级 | 分数区间 | 特征 |
|------|----------|------|
| L1 观望者 | 0-1.8 | 刚起步，缺乏明确规划 |
| L2 起步者 | 1.8-2.5 | 试点阶段，零星应用 |
| L3 探索者 | 2.5-3.2 | 有规划，小规模应用 |
| L4 加速者 | 3.2-4.0 | 规模化应用，成熟度高 |
| L5 领先者 | 4.0+ | 行业标杆，生态引领 |

## 路线图规划

### 基础期 (0-6个月)
- 建立AI战略
- 组建核心团队
- 制定数据标准

### 建设期 (6-12个月)
- 搭建技术平台
- 培养人才队伍
- 开发核心场景

### 优化期 (12-18个月)
- 全面推广应用
- 优化业务流程
- 形成创新文化

## 技术架构

```
数据层
├── ai_maturity_companies.csv (企业数据)
├── ai_maturity_benchmarks.csv (行业基准)
└── ai_initiatives.csv (AI倡议)

处理层
├── data_processing.py (数据计算引擎)
├── report_generator.py (报告生成器)
└── ai_maturity_dashboard.py (Streamlit应用)

应用层
├── Streamlit交互看板
└── HTML分析报告

输出层
├── analysis_report.html (专业报告)
├── analysis_report.md (Markdown文档)
└── 个性化路线图
```

## 许可证

本项目仅供内部使用，如需外部分享请获得授权。

## 版本历史

- v1.0 (2026-05-11) - 初始版本
  - 基础数据处理
  - Streamlit看板
  - HTML报告生成

## 联系方式

如有问题或建议，请联系项目团队。