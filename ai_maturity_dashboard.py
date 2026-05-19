"""
企业AI成熟度分析Dashboard
使用Streamlit + Plotly构建交互式数据看板
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import datetime

# 六大维度定义
DIMENSIONS = {
    '战略与愿景': 'Strategy',
    '数据基础': 'Data',
    '技术能力': 'Technology',
    '人才与组织': 'Talent',
    '治理与伦理': 'Governance',
    '文化与创新': 'Culture'
}

# 页面配置
st.set_page_config(
    page_title="企业AI成熟度分析",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
    .info {
        color: #2563EB;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 加载数据函数
@st.cache_data
def load_data():
    """加载所有数据文件"""
    companies = pd.read_csv("ai_maturity_companies.csv")
    benchmarks = pd.read_csv("ai_maturity_benchmarks.csv")
    initiatives = pd.read_csv("ai_initiatives.csv")
    # 计算后的分数数据
    try:
        dimension_scores = pd.read_csv("ai_maturity_scores.csv")
        gaps = pd.read_csv("ai_maturity_gaps.csv")
        recommendations = pd.read_csv("ai_maturity_recommendations.csv")
        roadmaps = json.load(open("roadmaps.json", "r", encoding="utf-8"))
    except:
        # 如果处理过的数据不存在，进行计算
        dimension_scores, gaps, recommendations, roadmaps = process_raw_data(companies, benchmarks, initiatives)

    return {
        'companies': companies,
        'benchmarks': benchmarks,
        'initiatives': initiatives,
        'dimension_scores': dimension_scores,
        'gaps': gaps,
        'recommendations': recommendations,
        'roadmaps': roadmaps
    }

# 数据处理函数
def process_raw_data(companies, benchmarks, initiatives):
    """处理原始数据并计算各项指标"""
    from data_processing import calculate_dimension_scores, gap_analysis, priority_matrix, generate_roadmap

    # 计算维度分数
    df_scores = calculate_dimension_scores(companies)
    df_scores["maturity_level"] = df_scores["overall_score"].apply(classify_maturity)

    # 差距分析
    df_gaps = gap_analysis(df_scores, benchmarks)

    # 优先级矩阵
    df_recs = priority_matrix(df_scores, df_gaps, initiatives)

    # 路线图
    roadmaps = generate_roadmap(df_recs)

    # 保存结果
    df_scores.to_csv("ai_maturity_scores.csv", index=False)
    df_gaps.to_csv("ai_maturity_gaps.csv", index=False)
    df_recs.to_csv("ai_maturity_recommendations.csv", index=False)

    return df_scores, df_gaps, df_recs, roadmaps

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

# 获取成熟度颜色
def get_maturity_color(level):
    colors = {
        "L1 观望者": "#EF4444",
        "L2 起步者": "#F59E0B",
        "L3 探索者": "#3B82F6",
        "L4 加速者": "#8B5CF6",
        "L5 领先者": "#10B981"
    }
    return colors.get(level, "#6B7280")

# 侧边栏 - 筛选条件
def render_sidebar(data):
    """渲染侧边栏筛选器"""
    st.sidebar.title("📊 筛选条件")

    # 行业筛选
    industries = sorted(data['dimension_scores']['industry'].unique())
    selected_industries = st.sidebar.multiselect(
        "选择行业",
        industries,
        default=industries,
        key="industries"
    )

    # 企业规模筛选
    sizes = sorted(data['dimension_scores']['size'].unique())
    selected_sizes = st.sidebar.multiselect(
        "选择企业规模",
        sizes,
        default=sizes,
        key="sizes"
    )

    # 成熟度筛选
    selected_maturity = st.sidebar.multiselect(
        "选择成熟度等级",
        ["L1 观望者", "L2 起步者", "L3 探索者", "L4 加速者", "L5 领先者"],
        default=["L1 观望者", "L2 起步者", "L3 探索者", "L4 加速者", "L5 领先者"],
        key="maturity"
    )

    # 分数范围筛选
    all_scores = data['dimension_scores']['overall_score']
    score_range = st.sidebar.slider(
        "总体评分范围",
        float(all_scores.min()),
        float(all_scores.max()),
        (float(all_scores.min()), float(all_scores.max())),
        key="score_range"
    )

    return {
        'industries': selected_industries,
        'sizes': selected_sizes,
        'maturity': selected_maturity,
        'score_range': score_range
    }

# 筛选数据函数
def filter_data(data, filters):
    """根据筛选条件过滤数据"""
    filtered = data['dimension_scores'].copy()

    # 应用行业筛选
    if filters['industries']:
        filtered = filtered[filtered['industry'].isin(filters['industries'])]

    # 应用规模筛选
    if filters['sizes']:
        filtered = filtered[filtered['size'].isin(filters['sizes'])]

    # 应用成熟度筛选
    if filters['maturity']:
        filtered = filtered[filtered['maturity_level'].isin(filters['maturity'])]

    # 应用分数范围筛选
    filtered = filtered[
        (filtered['overall_score'] >= filters['score_range'][0]) &
        (filtered['overall_score'] <= filters['score_range'][1])
    ]

    return filtered

# 主要可视化组件
def render_overview_section(data):
    """渲染总体概览部分"""
    st.markdown("<h1 class='main-header'>企业AI成熟度分析Dashboard</h1>", unsafe_allow_html=True)

    # KPI卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "企业总数",
            len(data['companies']),
            "覆盖全行业"
        )

    with col2:
        avg_score = data['dimension_scores']['overall_score'].mean()
        st.metric(
            "平均成熟度",
            f"{avg_score:.2f}",
            "行业基准: 3.0"
        )

    with col3:
        top_companies = len(data['dimension_scores'][data['dimension_scores']['maturity_level'].isin(['L4 加速者', 'L5 领先者'])])
        st.metric(
            "领先企业",
            top_companies,
            f"{top_companies/len(data['dimension_scores'])*100:.1f}%"
        )

    with col4:
        total_gaps = data['gaps']['gap_to_target'].sum()
        st.metric(
            "总体差距",
            f"{total_gaps:.1f}",
            "需重点改进"
        )

    # 成熟度分布饼图
    st.subheader("📈 成熟度分布")
    col1, col2 = st.columns(2)

    with col1:
        maturity_counts = data['dimension_scores']['maturity_level'].value_counts()
        fig_pie = px.pie(
            values=maturity_counts.values,
            names=maturity_counts.index,
            color=maturity_counts.index,
            color_discrete_map={
                "L1 观望者": "#EF4444",
                "L2 起步者": "#F59E0B",
                "L3 探索者": "#3B82F6",
                "L4 加速者": "#8B5CF6",
                "L5 领先者": "#10B981"
            },
            title="成熟度等级分布"
        )
        fig_pie.update_layout(
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 行业分布
        industry_counts = data['dimension_scores']['industry'].value_counts()
        fig_bar = px.bar(
            x=industry_counts.index,
            y=industry_counts.values,
            title="行业分布",
            labels={'x': '行业', 'y': '企业数量'},
            color=industry_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(
            xaxis_tickangle=45,
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)

def render_company_detail_section(data):
    """渲染企业详情部分"""
    st.subheader("🏢 企业详情分析")

    # 选择企业
    selected_company = st.selectbox(
        "选择企业",
        options=data['dimension_scores']['company_name'].tolist(),
        key="company_select"
    )

    # 获取企业数据
    company_data = data['dimension_scores'][data['dimension_scores']['company_name'] == selected_company].iloc[0]
    company_id = company_data['company_id']

    # 企业基本信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("行业", company_data['industry'])
    with col2:
        st.metric("规模", company_data['size'])
    with col3:
        st.metric("成熟度等级", company_data['maturity_level'])

    # 雷达图 - 六大维度
    st.write(f"**{selected_company} - 六大维度雷达图**")
    dimensions = list(DIMENSIONS.keys())
    current_scores = [company_data[f"{dim}_current"] for dim in dimensions]
    target_scores = [company_data[f"{dim}_target"] for dim in dimensions]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=current_scores,
        theta=dimensions,
        fill='toself',
        name='当前分数',
        line_color='blue'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=target_scores,
        theta=dimensions,
        fill='toself',
        name='目标分数',
        line_color='red'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title='六大维度成熟度对比'
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # 企业详情表格
    st.write(f"**{selected_company} - 维度详细评分**")
    details_df = pd.DataFrame({
        '维度': dimensions,
        '当前分数': current_scores,
        '目标分数': target_scores,
        '差距': [target_scores[i] - current_scores[i] for i in range(len(dimensions))]
    })

    # 高亮显示差距最大的维度
    details_df['状态'] = details_df['差距'].apply(lambda x: '⚠️ 需改进' if x > 1 else '✅ 正常')

    st.dataframe(
        details_df.style
        .highlight_between(subset=['差距'], left=1.0, right=5.0, color='lightcoral')
        .map(lambda x: 'font-weight: bold' if isinstance(x, str) and x.startswith('⚠️') else '', subset=['状态']),
        use_container_width=True
    )

def render_industry_comparison_section(data):
    """渲染行业对比部分"""
    st.subheader("📊 行业对比分析")

    # 行业平均分对比
    industry_avg = data['dimension_scores'].groupby('industry')['overall_score'].mean().sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(
            x=industry_avg.values,
            y=industry_avg.index,
            orientation='h',
            title="各行业平均成熟度",
            labels={'x': '平均分数', 'y': '行业'},
            color=industry_avg.values,
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(
            xaxis_range=[0, 5],
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # 行业维度对比
        st.write("**行业维度对比热力图**")
        industry_dim_avg = data['dimension_scores'].groupby('industry').agg({
            '战略与愿景_current': 'mean',
            '数据基础_current': 'mean',
            '技术能力_current': 'mean',
            '人才与组织_current': 'mean',
            '治理与伦理_current': 'mean',
            '文化与创新_current': 'mean'
        }).round(2)

        fig_heatmap = px.imshow(
            industry_dim_avg.T,
            x=industry_dim_avg.index,
            y=industry_dim_avg.index,
            color_continuous_scale='RdYlBu_r',
            title="行业维度平均分热力图"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

def render_priority_matrix_section(data):
    """渲染优先级矩阵部分"""
    st.subheader("🎯 优先级矩阵分析")

    # 获取所有推荐
    all_recommendations = data['recommendations'].copy()

    # 添加颜色映射
    def get_priority_color(score):
        if score >= 8.0:
            return '#10B981'  # 绿色 - 高优先级
        elif score >= 5.0:
            return '#F59E0B'  # 橙色 - 中优先级
        else:
            return '#EF4444'  # 红色 - 低优先级

    all_recommendations['color'] = all_recommendations['priority_score'].apply(get_priority_color)

    # 气泡图
    fig_bubble = px.scatter(
        all_recommendations,
        x='effort',
        y='impact',
        size='dimension_gap',
        color='priority_score',
        hover_name='initiative_name',
        hover_data=['company_name', 'dimension', 'duration_months', 'phase'],
        title="举措优先级矩阵（Impact vs Effort）",
        labels={'effort': '投入程度', 'impact': '影响力', 'dimension_gap': '维度差距'},
        color_continuous_scale='Viridis'
    )

    # 添加四象限划分
    fig_bubble.add_hline(y=3.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig_bubble.add_vline(x=3.5, line_dash="dash", line_color="gray", opacity=0.5)

    fig_bubble.update_layout(
        xaxis_title="投入程度 (1-5)",
        yaxis_title="影响力 (1-5)",
        showlegend=True,
        height=600
    )

    st.plotly_chart(fig_bubble, use_container_width=True)

    # 优先级列表
    st.write("**Top 10 高优先级举措推荐**")
    top_recs = all_recommendations.nlargest(10, 'priority_score')

    # 格式化显示
    top_recs_display = top_recs[[
        'company_name', 'initiative_name', 'dimension',
        'priority_score', 'impact', 'effort', 'duration_months', 'phase'
    ]].copy()

    top_recs_display['优先级评分'] = top_recs_display['priority_score'].apply(
        lambda x: f"{'🔥' * int(round(x/5))} {x:.2f}"
    )

    st.dataframe(
        top_recs_display.style
        .background_gradient(subset=['priority_score'], cmap='YlOrRd')
        .map(lambda x: 'font-weight: bold' if isinstance(x, str) and '🔥' in x else '',
                 subset=['优先级评分']),
        use_container_width=True
    )

def render_roadmap_section(data):
    """渲染路线图部分"""
    st.subheader("🗺️ 企业转型路线图")

    # 选择企业
    selected_company = st.selectbox(
        "选择企业查看路线图",
        options=data['dimension_scores']['company_name'].tolist(),
        key="roadmap_company"
    )

    company_id = data['dimension_scores'][
        data['dimension_scores']['company_name'] == selected_company
    ]['company_id'].iloc[0]

    # 显示路线图
    if company_id in data['roadmaps']:
        roadmap = data['roadmaps'][company_id]

        # 三个阶段的路线图
        for phase_name, phase_items in roadmap['phases'].items():
            if phase_items:  # 只显示有内容的阶段
                st.write(f"### {phase_name}")

                # 创建阶段卡片
                for item in phase_items:
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.write(f"**{item['initiative']}**")
                        st.write(f"📂 {item['dimension']}")
                        st.caption(item.get('description', ''))

                    with col2:
                        st.metric("时长", item['duration'])

                    with col3:
                        # 优先级星级
                        stars = int(round(item['priority_score'] / 5)) if item['priority_score'] <= 5 else 5
                        st.write(f"⭐ {'⭐' * stars} ({item['priority_score']:.2f})")

                st.divider()
    else:
        st.warning("该企业暂无路线图数据")

def render_export_section():
    """渲染导出部分"""
    st.subheader("📥 导出报告")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 导出数据分析")

        if st.button("📊 导出分析数据 (Excel)"):
            # 这里可以添加导出Excel的逻辑
            st.success("数据导出功能开发中...")

    with col2:
        st.write("### 生成分析报告")

        if st.button("📄 生成HTML报告"):
            # 这里可以添加生成HTML报告的逻辑
            st.success("HTML报告生成功能开发中...")

# 主函数
def main():
    """主函数"""
    # 加载数据
    data = load_data()

    # 渲染侧边栏
    filters = render_sidebar(data)

    # 筛选后的数据
    filtered_data = filter_data(data, filters)

    # 渲染主要内容
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 总体概览",
        "🏢 企业详情",
        "📊 行业对比",
        "🎯 优先级矩阵",
        "🗺️ 路线图",
        "📥 导出报告"
    ])

    with tab1:
        render_overview_section(data)

    with tab2:
        render_company_detail_section(data)

    with tab3:
        render_industry_comparison_section(data)

    with tab4:
        render_priority_matrix_section(data)

    with tab5:
        render_roadmap_section(data)

    with tab6:
        render_export_section()

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6B7280; font-size: 14px;'>"
        "企业AI成熟度分析报告 | 数据更新时间: 2026-05-11 | "
        f"共分析 {len(data['dimension_scores'])} 家企业</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()