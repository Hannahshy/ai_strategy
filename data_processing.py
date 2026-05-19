"""
企业 AI 成熟度分析脚本
流程：加载 → 维度评分计算 → 差距分析 → 优先级矩阵 → 个性化路线图生成
"""
import pandas as pd
import numpy as np
import json

DIMENSIONS = {
    "战略与愿景": {"sub_dims": ["AI战略清晰度", "高管支持度", "业务对齐度"], "weight": 0.20},
    "数据基础": {"sub_dims": ["数据质量", "数据治理", "数据开放性"], "weight": 0.20},
    "技术能力": {"sub_dims": ["基础设施就绪度", "MLOps成熟度", "AI平台能力"], "weight": 0.15},
    "人才与组织": {"sub_dims": ["AI人才密度", "跨部门协作", "培训体系"], "weight": 0.15},
    "治理与伦理": {"sub_dims": ["AI治理框架", "风险管控", "伦理合规"], "weight": 0.15},
    "文化与创新": {"sub_dims": ["数据驱动文化", "创新机制", "容错与试错"], "weight": 0.15},
}


# ============================================================
# 1. 数据加载
# ============================================================
def load_data():
    companies = pd.read_csv("ai_maturity_companies.csv")
    benchmarks = pd.read_csv("ai_maturity_benchmarks.csv")
    initiatives = pd.read_csv("ai_initiatives.csv")
    print(f"加载完成: {len(companies)} 家企业, {len(benchmarks)} 条基准, {len(initiatives)} 项举措")
    return companies, benchmarks, initiatives


# ============================================================
# 2. 维度评分计算
# ============================================================
def calculate_dimension_scores(companies):
    """将子维度分数聚合为6大维度分数，再计算加权总分"""
    dim_scores = []

    for _, row in companies.iterrows():
        record = {
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "industry": row["industry"],
            "size": row["size"],
        }

        weighted_total = 0
        for dim_name, dim_info in DIMENSIONS.items():
            subs = dim_info["sub_dims"]
            # 当前分 = 该维度下所有子维度当前分的均值
            current_vals = [row[f"{s}_current"] for s in subs]
            target_vals = [row[f"{s}_target"] for s in subs]
            dim_current = np.mean(current_vals)
            dim_target = np.mean(target_vals)
            weighted_total += dim_current * dim_info["weight"]

            record[f"{dim_name}_current"] = round(dim_current, 2)
            record[f"{dim_name}_target"] = round(dim_target, 2)
            record[f"{dim_name}_gap"] = round(dim_target - dim_current, 2)

        record["overall_score"] = round(weighted_total, 2)
        dim_scores.append(record)

    df = pd.DataFrame(dim_scores)
    print(f"\n总体评分分布:")
    print(f"  均值: {df['overall_score'].mean():.2f}")
    print(f"  中位数: {df['overall_score'].median():.2f}")
    print(f"  范围: {df['overall_score'].min():.2f} - {df['overall_score'].max():.2f}")
    return df


# ============================================================
# 3. 成熟度分级
# ============================================================
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


# ============================================================
# 4. 差距分析
# ============================================================
def gap_analysis(df_scores, benchmarks):
    """计算每家企业与行业基准的差距"""
    gap_records = []

    for _, row in df_scores.iterrows():
        industry = row["industry"]
        for dim_name in DIMENSIONS:
            current = row[f"{dim_name}_current"]
            target = row[f"{dim_name}_target"]
            # 行业基准
            bm_row = benchmarks[
                (benchmarks["industry"] == industry)
                & (benchmarks["dimension"] == dim_name)
            ]
            industry_avg = bm_row["industry_avg_score"].values[0]
            industry_top = bm_row["industry_top_quartile"].values[0]

            gap_records.append({
                "company_id": row["company_id"],
                "company_name": row["company_name"],
                "industry": industry,
                "dimension": dim_name,
                "current_score": current,
                "target_score": target,
                "industry_avg": industry_avg,
                "industry_top": industry_top,
                "gap_to_target": round(target - current, 2),
                "gap_to_industry_avg": round(current - industry_avg, 2),
                "gap_to_industry_top": round(current - industry_top, 2),
            })

    df_gaps = pd.DataFrame(gap_records)

    print(f"\n差距分析概要:")
    for dim_name in DIMENSIONS:
        dim_data = df_gaps[df_gaps["dimension"] == dim_name]
        avg_gap = dim_data["gap_to_industry_avg"].mean()
        print(f"  {dim_name}: 与行业均值差距 = {avg_gap:+.2f}")

    return df_gaps


# ============================================================
# 5. 优先级矩阵 — 确定先做什么
# ============================================================
def priority_matrix(df_scores, df_gaps, initiatives):
    """基于差距和举措的impact/effort，为企业推荐优先举措"""
    recommendations = []

    for _, company in df_scores.iterrows():
        company_gaps = df_gaps[df_gaps["company_id"] == company["company_id"]]
        # 找差距最大的3个维度
        top_gap_dims = company_gaps.nlargest(3, "gap_to_target")["dimension"].tolist()

        for dim in top_gap_dims:
            dim_initiatives = initiatives[initiatives["dimension"] == dim]
            for _, ini in dim_initiatives.iterrows():
                gap = company_gaps[company_gaps["dimension"] == dim]["gap_to_target"].values[0]
                recommendations.append({
                    "company_id": company["company_id"],
                    "company_name": company["company_name"],
                    "dimension": dim,
                    "dimension_gap": gap,
                    "initiative_id": ini["initiative_id"],
                    "initiative_name": ini["name"],
                    "impact": ini["impact"],
                    "effort": ini["effort"],
                    "duration_months": ini["duration_months"],
                    "phase": ini["phase"],
                    "priority_score": round(ini["impact"] / ini["effort"] * gap, 2),
                    "description": ini["description"],
                })

    df_recs = pd.DataFrame(recommendations)
    df_recs = df_recs.sort_values("priority_score", ascending=False)

    print(f"\n优先级矩阵: 共 {len(df_recs)} 条推荐")
    print(f"  高优先级(前25%): {len(df_recs[df_recs['priority_score'] >= df_recs['priority_score'].quantile(0.75)])} 条")
    return df_recs


# ============================================================
# 6. 生成转型路线图
# ============================================================
def generate_roadmap(df_recs):
    """按企业分组，生成三阶段路线图"""
    roadmaps = {}

    for company_id in df_recs["company_id"].unique():
        company_recs = df_recs[df_recs["company_id"] == company_id]
        company_name = company_recs.iloc[0]["company_name"]

        phases = {"基础期(0-6月)": [], "建设期(6-12月)": [], "优化期(12-18月)": []}
        for _, rec in company_recs.iterrows():
            phase = rec["phase"]
            if phase == "基础期":
                phases["基础期(0-6月)"].append({
                    "initiative": rec["initiative_name"],
                    "dimension": rec["dimension"],
                    "duration": f"{rec['duration_months']}个月",
                    "priority_score": rec["priority_score"],
                })
            elif phase == "建设期":
                phases["建设期(6-12月)"].append({
                    "initiative": rec["initiative_name"],
                    "dimension": rec["dimension"],
                    "duration": f"{rec['duration_months']}个月",
                    "priority_score": rec["priority_score"],
                })
            else:
                phases["优化期(12-18月)"].append({
                    "initiative": rec["initiative_name"],
                    "dimension": rec["dimension"],
                    "duration": f"{rec['duration_months']}个月",
                    "priority_score": rec["priority_score"],
                })

        # 每个阶段按优先级排序，取前5个
        for phase in phases:
            phases[phase] = sorted(phases[phase], key=lambda x: x["priority_score"], reverse=True)[:5]

        roadmaps[company_id] = {
            "company_name": company_name,
            "phases": phases,
        }

    # 保存为JSON
    with open("roadmaps.json", "w", encoding="utf-8") as f:
        json.dump(roadmaps, f, ensure_ascii=False, indent=2)

    print(f"\n路线图生成完成: {len(roadmaps)} 家企业 → roadmaps.json")
    return roadmaps


# ============================================================
# 7. 行业对比分析
# ============================================================
def industry_analysis(df_scores, benchmarks):
    print(f"\n行业AI成熟度对比:")
    industry_stats = df_scores.groupby("industry")["overall_score"].agg(["mean", "median", "std"])
    industry_stats.columns = ["均值", "中位数", "标准差"]
    industry_stats = industry_stats.sort_values("均值", ascending=False)
    print(industry_stats.to_string())

    print(f"\n各维度行业差距:")
    for dim_name in DIMENSIONS:
        col = f"{dim_name}_current"
        dim_stats = df_scores.groupby("industry")[col].mean().sort_values(ascending=False)
        print(f"  {dim_name}: {dim_stats.to_dict()}")


# ============================================================
# 主流程
# ============================================================
if __name__ == "__main__":
    companies, benchmarks, initiatives = load_data()
    df_scores = calculate_dimension_scores(companies)

    # 成熟度分级
    df_scores["maturity_level"] = df_scores["overall_score"].apply(classify_maturity)
    print(f"\n成熟度分布:\n{df_scores['maturity_level'].value_counts().to_string()}")

    # 差距分析
    df_gaps = gap_analysis(df_scores, benchmarks)

    # 优先级矩阵
    df_recs = priority_matrix(df_scores, df_gaps, initiatives)

    # 路线图
    roadmaps = generate_roadmap(df_recs)

    # 行业对比
    industry_analysis(df_scores, benchmarks)

    # 保存
    df_scores.to_csv("ai_maturity_scores.csv", index=False)
    df_gaps.to_csv("ai_maturity_gaps.csv", index=False)
    df_recs.to_csv("ai_maturity_recommendations.csv", index=False)
    print("\n所有分析结果已保存")
