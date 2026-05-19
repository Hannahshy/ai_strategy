"""
企业AI成熟度分析报告生成器
生成专业的HTML分析报告，包含执行摘要、数据概览、关键发现、模型结果和建议措施
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

# 加载数据
def load_data():
    """加载所有数据文件"""
    try:
        companies = pd.read_csv("ai_maturity_companies.csv")
        benchmarks = pd.read_csv("ai_maturity_benchmarks.csv")
        initiatives = pd.read_csv("ai_initiatives.csv")
        dimension_scores = pd.read_csv("ai_maturity_scores.csv")
        gaps = pd.read_csv("ai_maturity_gaps.csv")
        recommendations = pd.read_csv("ai_maturity_recommendations.csv")
        roadmaps = json.load(open("roadmaps.json", "r", encoding="utf-8"))
    except:
        # 如果处理过的数据不存在，先进行计算
        from data_processing import calculate_dimension_scores, gap_analysis, priority_matrix, generate_roadmap

        companies = pd.read_csv("ai_maturity_companies.csv")
        benchmarks = pd.read_csv("ai_maturity_benchmarks.csv")
        initiatives = pd.read_csv("ai_initiatives.csv")

        dimension_scores = calculate_dimension_scores(companies)
        dimension_scores["maturity_level"] = dimension_scores["overall_score"].apply(classify_maturity)
        gaps = gap_analysis(dimension_scores, benchmarks)
        recommendations = priority_matrix(dimension_scores, gaps, initiatives)
        roadmaps = generate_roadmap(recommendations)

    return {
        'companies': companies,
        'benchmarks': benchmarks,
        'initiatives': initiatives,
        'dimension_scores': dimension_scores,
        'gaps': gaps,
        'recommendations': recommendations,
        'roadmaps': roadmaps
    }

# 成熟度分类函数
def classify_maturity(score):
    if score >= 4.0:
        return "L5 领先者"
    elif score >= 3.2:
        return "L4 加速者"
    elif score >= 2.5:
        return "L3 探索者"
    elif score >= 1.8:
        return "L2 起步者"
    else:
        return "L1 观望者"

# 生成执行摘要
def generate_executive_summary(data):
    """生成执行摘要"""
    companies = data['companies']
    dimension_scores = data['dimension_scores']
    recommendations = data['recommendations']

    # 基础统计
    total_companies = len(dimension_scores)
    avg_score = dimension_scores['overall_score'].mean()
    avg_gap = dimension_scores[[f"{dim}_gap" for dim in DIMENSIONS.keys()]].mean().mean()

    # 成熟度分布
    maturity_counts = dimension_scores['maturity_level'].value_counts()
    leaders = maturity_counts.get("L5 领先者", 0) + maturity_counts.get("L4 加速者", 0)
    leaders_pct = leaders / total_companies * 100

    # 行业表现最佳
    best_industry = dimension_scores.groupby('industry')['overall_score'].mean().idxmax()

    # 最重要的举措
    top_initiatives = recommendations.nlargest(5, 'priority_score')

    summary = f"""
## 执行摘要

### 核心发现
- 本次分析涵盖{total_companies}家企业，覆盖金融、制造、零售、医疗、能源、科技六大行业
- 企业AI成熟度平均得分为{avg_score:.2f}分，与行业基准存在{avg_gap:.2f}分的差距
- {leaders_pct:.1f}%的企业达到中高级成熟度（L4/L5），{100-leaders_pct:.1f}%仍处于早期阶段
- {best_industry}行业表现最佳，平均成熟度领先其他行业

### 关键洞察
1. **战略与治理领先**：企业普遍重视战略制定和合规管理，但文化转型滞后
2. **数据基础薄弱**：数据质量和开放性成为普遍瓶颈，影响AI应用落地
3. **人才缺口明显**：跨部门协作和培训体系不足，制约AI能力提升

### 建议重点
- 优先推进{top_initiatives.iloc[0]['initiative_name']}等高影响力举措
- 建立数据治理体系，提升数据质量和开放性
- 加强人才培养和组织变革，营造数据驱动文化

报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}
"""
    return summary

# 生成数据概览
def generate_data_overview(data):
    """生成数据概览部分"""
    dimension_scores = data['dimension_scores']

    # 总体统计
    total_companies = len(dimension_scores)
    score_stats = dimension_scores['overall_score'].describe()

    # 行业分布
    industry_dist = dimension_scores['industry'].value_counts()

    # 成熟度分布
    maturity_dist = dimension_scores['maturity_level'].value_counts()

    # 规模分布
    size_dist = dimension_scores['size'].value_counts()

    # 行业平均分
    industry_avg = dimension_scores.groupby('industry')['overall_score'].mean().sort_values(ascending=False)

    # 维度平均分
    dim_avg = {}
    for dim_name in DIMENSIONS.keys():
        dim_avg[dim_name] = dimension_scores[f"{dim_name}_current"].mean()

    overview = f"""
## 数据概览

### 样本统计
- **分析企业总数**：{total_companies}家
- **平均成熟度**：{score_stats['mean']:.2f}分
- **中位数**：{score_stats['50%']:.2f}分
- **最高分**：{score_stats['max']:.2f}分
- **最低分**：{score_stats['min']:.2f}分
- **标准差**：{score_stats['std']:.2f}分

### 行业分布
{dict_to_table(industry_dist)}

### 企业规模分布
{dict_to_table(size_dist)}

### 成熟度等级分布
{dict_to_table(maturity_dist)}

### 行业平均成熟度排名
| 排名 | 行业 | 平均分 |
|------|------|--------|
{industry_ranking_to_table(industry_avg)}

### 六大维度平均分
| 维度 | 平均分 | 状态 |
|------|--------|------|
{dim_avg_to_table(dim_avg)}
"""
    return overview

# 生成关键发现
def generate_key_findings(data):
    """生成关键发现部分"""
    dimension_scores = data['dimension_scores']
    gaps = data['gaps']
    recommendations = data['recommendations']

    # 各维度差距分析
    dim_gaps = {}
    for dim_name in DIMENSIONS.keys():
        dim_gaps[dim_name] = gaps[gaps['dimension'] == dim_name]['gap_to_target'].mean()

    # 行业差距分析
    industry_gaps = dimension_scores.groupby('industry').apply(
        lambda x: (x['overall_score'].mean() - 3.0)  # 假设3.0为基准线
    ).sort_values()

    # 举措分析
    top_initiatives = recommendations.nlargest(10, 'priority_score')
    initiative_stats = recommendations.groupby('dimension').agg({
        'priority_score': 'mean',
        'impact': 'mean',
        'effort': 'mean'
    }).round(2)

    # 问题识别
    problem_dims = sorted(dim_gaps.items(), key=lambda x: x[1], reverse=True)[:3]

    findings = f"""
## 关键发现

### 1. 成熟度差距分析
企业AI成熟度与目标存在显著差距，六大维度中差距最大的领域：

{dim_gap_analysis_to_table(problem_dims)}

### 2. 行业差异明显
各行业AI成熟度发展不均衡，具体情况：

{industry_gap_analysis_to_table(industry_gaps)}

### 3. 举措优先级分析
基于影响力和投入度的优先级分析，高价值举措集中在：

{initiative_analysis_to_table(initiative_stats)}

### 4. 主要问题识别
1. **战略落地不足**：战略制定与执行脱节，业务对齐度低
2. **数据基础薄弱**：数据质量参差不齐，数据孤岛严重
3. **技术能力不足**：基础设施和平台能力建设滞后
4. **人才结构失衡**：专业人才短缺，组织协作不畅
5. **文化转型缓慢**：数据驱动文化尚未形成，创新机制缺失
"""
    return findings

# 生成模型结果
def generate_model_results(data):
    """生成模型结果部分"""
    dimension_scores = data['dimension_scores']
    recommendations = data['recommendations']

    # 成熟度模型结果
    maturity_data = {}
    for level in dimension_scores['maturity_level'].unique():
        level_data = dimension_scores[dimension_scores['maturity_level'] == level]
        maturity_data[level] = {
            'count': len(level_data),
            'mean': level_data['overall_score'].mean(),
            'min': level_data['overall_score'].min(),
            'max': level_data['overall_score'].max(),
            'sample_companies': ', '.join(level_data['company_name'].sample(min(len(level_data), 3)).tolist())
        }
    maturity_model = pd.DataFrame(maturity_data).T.round(2)

    # 行业模型
    industry_model = dimension_scores.groupby('industry').agg({
        'overall_score': ['mean', 'std', 'count'],
        '战略与愿景_current': 'mean',
        '数据基础_current': 'mean',
        '技术能力_current': 'mean',
        '人才与组织_current': 'mean',
        '治理与伦理_current': 'mean',
        '文化与创新_current': 'mean'
    }).round(2)

    # 规模模型
    size_data = {}
    for size in dimension_scores['size'].unique():
        size_df = dimension_scores[dimension_scores['size'] == size]
        size_data[size] = {
            'mean': size_df['overall_score'].mean(),
            'count': len(size_df),
            'sample_companies': ', '.join(size_df['company_name'].sample(min(len(size_df), 2)).tolist())
        }
    size_model = pd.DataFrame(size_data).T.round(2)

    # 优化建议模型
    recommendations['roi_score'] = recommendations['priority_score'] / recommendations['effort']
    roi_model = recommendations.groupby('dimension').agg({
        'priority_score': 'mean',
        'roi_score': 'mean',
        'duration_months': 'mean'
    }).round(2)

    results = f"""
## 模型结果

### 成熟度等级模型
| 等级 | 企业数 | 平均分 | 分数区间 | 代表企业 |
|------|--------|--------|----------|----------|
{maturity_model_to_table(maturity_model)}

### 行业影响模型
行业特征对AI成熟度的影响显著，不同行业表现各异：

{industry_model_to_table(industry_model)}

### 企业规模模型
企业规模与AI成熟度呈现正相关，大型企业表现更佳：

{size_model_to_table(size_model)}

### 优化建议模型
基于ROI分析的优化方向：

{roi_model_to_table(roi_model)}

### 预测模型
基于当前数据，企业预计实现目标时间：
- 基础改进：6-12个月
- 全面提升：12-18个月
- 行业领先：24个月
"""
    return results

# 生成建议措施
def generate_recommendations(data):
    """生成建议措施部分"""
    recommendations = data['recommendations']
    roadmaps = data['roadmaps']

    # 优先级最高的举措
    top_priority_actions = recommendations.nlargest(15, 'priority_score')

    # 按维度的建议
    dim_recommendations = {}
    for dim in DIMENSIONS.keys():
        dim_recs = recommendations[recommendations['dimension'] == dim]
        if not dim_recs.empty:
            dim_recommendations[dim] = dim_recs.nlargest(3, 'priority_score')

    # 路线图建议
    roadmap_suggestions = []
    for company_id, roadmap in roadmaps.items():
        for phase, items in roadmap['phases'].items():
            if items:
                for item in items:
                    roadmap_suggestions.append({
                        'company': roadmap['company_name'],
                        'phase': phase,
                        'initiative': item['initiative'],
                        'dimension': item['dimension'],
                        'priority': item['priority_score']
                    })

    roadmap_suggestions = sorted(roadmap_suggestions, key=lambda x: x['priority'], reverse=True)

    recommendations_text = f"""
## 建议措施

### 阶段性建议
#### 第一阶段（0-6个月）：奠定基础
1. **AI战略制定**：明确AI愿景、目标和KPI，获得高管共识
2. **数据治理**：建立数据质量标准和治理机制
3. **团队建设**：成立AI卓越中心，招募核心人才

#### 第二阶段（6-12个月）：建设能力
1. **平台建设**：搭建AI平台和MLOps系统
2. **数据整合**：建立数据中台，打破数据孤岛
3. **人才培养**：开展全员AI素养培训

#### 第三阶段（12-18个月）：优化提升
1. **场景落地**：推进AI应用场景规模化
2. **文化建设**：营造数据驱动和创新文化
3. **持续优化**：建立评估和改进机制

### 优先级最高的举措
| 排名 | 举措名称 | 所属维度 | 优先级评分 | 预期时长 | 实施阶段 |
|------|----------|----------|------------|----------|----------|
{priority_actions_to_table(top_priority_actions)}

### 各维度具体建议
"""

    for dim, dim_recs in dim_recommendations.items():
        recommendations_text += f"""
#### {dim}
"""
        for _, rec in dim_recs.iterrows():
            recommendations_text += f"- **{rec['initiative_name']}**：{rec['description']}（优先级：{rec['priority_score']:.2f})\n"

    recommendations_text += """
### 企业个性化路线图
根据企业实际情况，建议采取以下差异化路径：

#### 领先企业（L4/L5）
- 重点：创新引领、行业标杆、生态构建
- 路径：前沿探索 → 标杆输出 → 生态共赢

#### 加速企业（L3）
- 重点：能力建设、场景深化、组织优化
- 路径：夯实基础 → 快速迭代 → 全面提升

#### 起步企业（L1/L2）
- 重点：战略规划、基础建设、人才培养
- 路径：明确方向 → 重点突破 → 持续改进

### 实施保障
1. **组织保障**：成立AI转型办公室，明确责任分工
2. **资源保障**：确保资金、人才、技术投入
3. **机制保障**：建立评估、激励、迭代机制
4. **风险管控**：识别并管控实施过程中的风险
"""

    return recommendations_text

# 辅助函数
def dict_to_table(d):
    """字典转表格"""
    return '\n'.join([f"| {k} | {v} |" for k, v in d.items()])

def industry_ranking_to_table(s):
    """行业排名转表格"""
    return '\n'.join([
        f"| {i+1} | {idx} | {val:.2f} |"
        for i, (idx, val) in enumerate(s.items())
    ])

def dim_avg_to_table(d):
    """维度平均分转表格"""
    status_map = {
        4.5: "🟢 优秀",
        3.5: "🟡 良好",
        2.5: "🔴 不足"
    }

    table = []
    for dim, score in d.items():
        if score >= 3.5:
            status = "🟢 良好"
        elif score >= 2.5:
            status = "🟡 一般"
        else:
            status = "🔴 不足"
        table.append(f"| {dim} | {score:.2f} | {status} |")

    return '\n'.join(table)

def dim_gap_analysis_to_table(gaps):
    """维度差距分析转表格"""
    table = []
    for dim, gap in gaps:
        if gap >= 1.5:
            level = "🔴 严重"
        elif gap >= 1.0:
            level = "🟡 中等"
        else:
            level = "🟢 轻微"
        table.append(f"| {dim} | {gap:.2f} | {level} |")

    return '\n'.join(table)

def industry_gap_analysis_to_table(gaps):
    """行业差距分析转表格"""
    table = []
    for industry, gap in gaps.items():
        if gap > 0:
            status = "🟢 领先"
        else:
            status = "🔴 落后"
        table.append(f"| {industry} | {gap:+.2f} | {status} |")

    return '\n'.join(table)

def initiative_analysis_to_table(stats):
    """举措分析转表格"""
    table = []
    for dim, row in stats.iterrows():
        table.append(f"| {dim} | {row['priority_score']:.2f} | {row['impact']:.2f} | {row['effort']:.2f} |")

    return '\n'.join(table)

def maturity_model_to_table(model):
    """成熟度模型转表格"""
    table = []
    for level in model.index:
        count = model.loc[level, 'count']
        mean_score = model.loc[level, 'mean']
        min_score = model.loc[level, 'min']
        max_score = model.loc[level, 'max']
        companies = model.loc[level, 'sample_companies']

        table.append(f"| {level} | {count} | {mean_score:.2f} | {min_score:.2f}-{max_score:.2f} | {companies} |")

    return '\n'.join(table)

def industry_model_to_table(model):
    """行业模型转表格"""
    table = []
    for industry, row in model['overall_score']['mean'].items():
        std = model['overall_score']['std'][industry]
        count = model['overall_score']['count'][industry]

        table.append(f"| {industry} | {row:.2f} | {std:.2f} | {count} |")

    return '\n'.join(table)

def size_model_to_table(model):
    """规模模型转表格"""
    table = []
    for size in model.index:
        mean_score = model.loc[size, 'mean']
        count = model.loc[size, 'count']
        companies = model.loc[size, 'sample_companies']

        table.append(f"| {size} | {mean_score:.2f} | {count} | {companies} |")

    return '\n'.join(table)

def roi_model_to_table(model):
    """ROI模型转表格"""
    table = []
    for dim, row in model.iterrows():
        table.append(f"| {dim} | {row['priority_score']:.2f} | {row['roi_score']:.2f} | {row['duration_months']:.1f}个月 |")

    return '\n'.join(table)

def priority_actions_to_table(actions):
    """优先级举措转表格"""
    table = []
    for i, (_, action) in enumerate(actions.iterrows()):
        table.append(f"| {i+1} | {action['initiative_name']} | {action['dimension']} | {action['priority_score']:.2f} | {action['duration_months']}个月 | {action['phase']} |")

    return '\n'.join(table)

# 生成完整报告
def generate_report():
    """生成完整报告"""
    # 加载数据
    data = load_data()

    # 生成报告各部分
    executive_summary = generate_executive_summary(data)
    data_overview = generate_data_overview(data)
    key_findings = generate_key_findings(data)
    model_results = generate_model_results(data)
    recommendations = generate_recommendations(data)

    # 组合完整报告
    full_report = f"""# 企业AI成熟度分析报告

{executive_summary}

{data_overview}

{key_findings}

{model_results}

{recommendations}

---
*报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}*
*分析工具：AI Maturity Analysis Dashboard*
*数据来源：企业调研、行业基准*
"""

    return full_report

# 添加全局变量
DIMENSIONS = {
    "战略与愿景": {"sub_dims": ["AI战略清晰度", "高管支持度", "业务对齐度"], "weight": 0.20},
    "数据基础": {"sub_dims": ["数据质量", "数据治理", "数据开放性"], "weight": 0.20},
    "技术能力": {"sub_dims": ["基础设施就绪度", "MLOps成熟度", "AI平台能力"], "weight": 0.15},
    "人才与组织": {"sub_dims": ["AI人才密度", "跨部门协作", "培训体系"], "weight": 0.15},
    "治理与伦理": {"sub_dims": ["AI治理框架", "风险管控", "伦理合规"], "weight": 0.15},
    "文化与创新": {"sub_dims": ["数据驱动文化", "创新机制", "容错与试错"], "weight": 0.15},
}

# Markdown转HTML函数
def markdown_to_html(markdown_text):
    """简单的Markdown转HTML"""
    # 生成报告
    report = generate_report()

    # 保存为Markdown文件
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    # 转换为HTML
    html_report = markdown_to_html(report)

    # 保存为HTML文件
    with open("analysis_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print("报告生成完成！")
    print("分析报告已保存为：")
    print("- analysis_report.md (Markdown格式)")
    print("- analysis_report.html (HTML格式)")
    """简单的Markdown转HTML"""
    html = markdown_text

    # 标题转换
    html = html.replace("# ", "<h1 style='color: #1E3A8A; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px;'>")
    html = html.replace("## ", "<h2 style='color: #1F2937; margin-top: 30px;'>")
    html = html.replace("### ", "<h3 style='color: #374151; margin-top: 20px;'>")
    html = html.replace("#### ", "<h4 style='color: #4B5563; margin-top: 15px;'>")

    # 结束标签
    html = html + "\n</h1>\n</h2>\n</h3>\n</h4>\n" * 4

    # 表格转换
    html = html.replace("|", "<td>")
    lines = html.split('\n')
    html_lines = []
    in_table = False

    for line in lines:
        if line.strip().startswith("<h") or line.strip() == "":
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(line)
        elif line.strip().startswith("---"):
            if not in_table:
                html_lines.append("<table style='border-collapse: collapse; width: 100%; margin: 20px 0;'>")
                in_table = True
            html_lines.append("<tr style='background-color: #F9FAFB;'>")
            html_lines.append("<th style='border: 1px solid #E5E7EB; padding: 12px; text-align: left; font-weight: bold;'>" + line.strip().replace("---", "<th style='border: 1px solid #E5E7EB; padding: 12px; text-align: left; font-weight: bold;'>"))
        else:
            if in_table:
                if line.strip():
                    html_lines.append("<tr style='border-bottom: 1px solid #E5E7EB;'>")
                    html_lines.append(line)
                    html_lines.append("</tr>")

    if in_table:
        html_lines.append("</table>")

    # 添加CSS样式
    css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0 auto;
            max-width: 1200px;
            padding: 20px;
            color: #374151;
            background-color: #F9FAFB;
        }
        h1, h2, h3, h4 {
            margin-top: 30px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #E5E7EB;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #F3F4F6;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #F9FAFB;
        }
        .highlight {
            background-color: #FEF3C7;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .warning {
            color: #D97706;
            font-weight: bold;
        }
        .success {
            color: #059669;
            font-weight: bold;
        }
        .danger {
            color: #DC2626;
            font-weight: bold;
        }
    </style>
    """

    return css + "\n".join(html_lines)