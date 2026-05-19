"""
企业 AI 成熟度评估 - 模拟数据生成器
生成 50 家企业的 AI 成熟度评估数据，覆盖 6 大维度 18 个子维度。
同时生成行业基准数据和转型举措库。
"""
import numpy as np
import pandas as pd

np.random.seed(42)

# ============================================================
# 维度与子维度定义（PwC AI成熟度模型简化版）
# ============================================================
DIMENSIONS = {
    "战略与愿景": {
        "sub_dims": ["AI战略清晰度", "高管支持度", "业务对齐度"],
        "weight": 0.20,
    },
    "数据基础": {
        "sub_dims": ["数据质量", "数据治理", "数据开放性"],
        "weight": 0.20,
    },
    "技术能力": {
        "sub_dims": ["基础设施就绪度", "MLOps成熟度", "AI平台能力"],
        "weight": 0.15,
    },
    "人才与组织": {
        "sub_dims": ["AI人才密度", "跨部门协作", "培训体系"],
        "weight": 0.15,
    },
    "治理与伦理": {
        "sub_dims": ["AI治理框架", "风险管控", "伦理合规"],
        "weight": 0.15,
    },
    "文化与创新": {
        "sub_dims": ["数据驱动文化", "创新机制", "容错与试错"],
        "weight": 0.15,
    },
}

INDUSTRIES = ["金融", "制造", "零售", "医疗", "能源", "科技"]
COMPANY_SIZES = ["大型(>10000人)", "中型(1000-10000人)", "小型(<1000人)"]

# ============================================================
# 生成 50 家企业数据
# ============================================================
N_COMPANIES = 50

companies = []
for i in range(N_COMPANIES):
    company_id = f"ENT-{i:03d}"
    industry = np.random.choice(INDUSTRIES)
    size = np.random.choice(COMPANY_SIZES, p=[0.3, 0.5, 0.2])

    # 基础成熟度水平（1-5分）受行业和规模影响
    base = np.random.normal(2.5, 0.8)
    if industry == "金融":
        base += 0.5
    elif industry == "科技":
        base += 0.8
    elif industry in ["制造", "能源"]:
        base -= 0.3
    if size == "大型(>10000人)":
        base += 0.2

    row = {
        "company_id": company_id,
        "company_name": f"企业{chr(65 + i // 26)}{chr(65 + i % 26)}",
        "industry": industry,
        "size": size,
        "revenue_bn": round(np.random.lognormal(2, 1), 2),  # 营收(十亿)
    }

    # 每个维度的当前分数和目标分数
    for dim_name, dim_info in DIMENSIONS.items():
        dim_base = base + np.random.normal(0, 0.5)
        for sub_dim in dim_info["sub_dims"]:
            current = np.clip(round(dim_base + np.random.normal(0, 0.4), 1), 1.0, 5.0)
            target = np.clip(round(current + np.random.uniform(0.5, 2.0), 1), 1.0, 5.0)
            row[f"{sub_dim}_current"] = current
            row[f"{sub_dim}_target"] = target

    companies.append(row)

df_companies = pd.DataFrame(companies)

# ============================================================
# 生成行业基准数据
# ============================================================
benchmarks = []
for industry in INDUSTRIES:
    for dim_name, dim_info in DIMENSIONS.items():
        # 行业平均分
        if industry == "科技":
            avg = np.random.uniform(3.0, 4.0)
        elif industry == "金融":
            avg = np.random.uniform(2.8, 3.8)
        elif industry in ["制造", "能源"]:
            avg = np.random.uniform(2.0, 3.2)
        else:
            avg = np.random.uniform(2.5, 3.5)

        benchmarks.append({
            "industry": industry,
            "dimension": dim_name,
            "industry_avg_score": round(avg, 1),
            "industry_top_quartile": round(avg + 0.8, 1),
        })

df_benchmarks = pd.DataFrame(benchmarks)

# ============================================================
# 生成转型举措库
# ============================================================
initiatives = [
    {"initiative_id": "I01", "name": "制定AI战略白皮书", "dimension": "战略与愿景",
     "impact": 4, "effort": 2, "duration_months": 3, "phase": "基础期",
     "description": "明确AI愿景、目标和KPI，获得高管共识"},
    {"initiative_id": "I02", "name": "成立AI卓越中心(CoE)", "dimension": "战略与愿景",
     "impact": 5, "effort": 3, "duration_months": 4, "phase": "基础期",
     "description": "建立跨职能AI团队，统筹全公司AI推进"},
    {"initiative_id": "I03", "name": "数据质量治理项目", "dimension": "数据基础",
     "impact": 5, "effort": 4, "duration_months": 6, "phase": "基础期",
     "description": "建立数据质量标准和清洗流程"},
    {"initiative_id": "I04", "name": "搭建数据中台", "dimension": "数据基础",
     "impact": 4, "effort": 5, "duration_months": 9, "phase": "建设期",
     "description": "统一数据资产管理，打破数据孤岛"},
    {"initiative_id": "I05", "name": "部署MLOps平台", "dimension": "技术能力",
     "impact": 4, "effort": 4, "duration_months": 6, "phase": "建设期",
     "description": "实现模型开发、部署、监控的全流程自动化"},
    {"initiative_id": "I06", "name": "云基础设施升级", "dimension": "技术能力",
     "impact": 3, "effort": 5, "duration_months": 8, "phase": "基础期",
     "description": "提供AI所需的弹性计算和存储能力"},
    {"initiative_id": "I07", "name": "AI人才引进计划", "dimension": "人才与组织",
     "impact": 4, "effort": 3, "duration_months": 4, "phase": "基础期",
     "description": "招募数据科学家、ML工程师等核心人才"},
    {"initiative_id": "I08", "name": "全员AI素养培训", "dimension": "人才与组织",
     "impact": 3, "effort": 2, "duration_months": 3, "phase": "建设期",
     "description": "分层次开展AI认知、工具使用、场景创新培训"},
    {"initiative_id": "I09", "name": "建立AI治理框架", "dimension": "治理与伦理",
     "impact": 4, "effort": 3, "duration_months": 4, "phase": "建设期",
     "description": "制定AI使用规范、审核流程和责任机制"},
    {"initiative_id": "I10", "name": "AI风险评估体系", "dimension": "治理与伦理",
     "impact": 3, "effort": 3, "duration_months": 3, "phase": "优化期",
     "description": "建立AI模型风险的识别、评估和缓解机制"},
    {"initiative_id": "I11", "name": "数据驱动文化变革", "dimension": "文化与创新",
     "impact": 3, "effort": 4, "duration_months": 8, "phase": "建设期",
     "description": "推动决策从经验驱动转向数据驱动"},
    {"initiative_id": "I12", "name": "AI创新孵化器", "dimension": "文化与创新",
     "impact": 4, "effort": 3, "duration_months": 5, "phase": "优化期",
     "description": "设立内部创新基金和快速实验机制"},
    {"initiative_id": "I13", "name": "AI场景快速验证", "dimension": "战略与愿景",
     "impact": 4, "effort": 2, "duration_months": 2, "phase": "基础期",
     "description": "选择3-5个高价值场景进行POC验证"},
    {"initiative_id": "I14", "name": "数据开放与共享机制", "dimension": "数据基础",
     "impact": 3, "effort": 3, "duration_months": 4, "phase": "建设期",
     "description": "建立内部数据共享目录和API标准"},
    {"initiative_id": "I15", "name": "AI伦理审查委员会", "dimension": "治理与伦理",
     "impact": 3, "effort": 2, "duration_months": 3, "phase": "优化期",
     "description": "组建跨部门伦理审查团队，定期审核AI应用"},
]

df_initiatives = pd.DataFrame(initiatives)

# ============================================================
# 保存所有数据
# ============================================================
df_companies.to_csv("ai_maturity_companies.csv", index=False)
df_benchmarks.to_csv("ai_maturity_benchmarks.csv", index=False)
df_initiatives.to_csv("ai_initiatives.csv", index=False)

print(f"企业数据: ai_maturity_companies.csv ({len(df_companies)} 家企业)")
print(f"行业基准: ai_maturity_benchmarks.csv ({len(df_benchmarks)} 条)")
print(f"举措库: ai_initiatives.csv ({len(df_initiatives)} 项举措)")
print(f"\n行业分布:\n{df_companies['industry'].value_counts().to_string()}")
print(f"\n规模分布:\n{df_companies['size'].value_counts().to_string()}")
