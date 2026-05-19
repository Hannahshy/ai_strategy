#!/bin/bash

# 企业AI成熟度分析系统 - 演示脚本
echo "=========================================="
echo "🏢 企业AI成熟度分析系统演示"
echo "=========================================="

# 1. 数据处理演示
echo ""
echo "1️⃣ 正在执行数据分析..."
python data_processing.py
if [ $? -eq 0 ]; then
    echo "✅ 数据分析完成"
else
    echo "❌ 数据分析失败"
    exit 1
fi

# 2. 生成报告演示
echo ""
echo "2️⃣ 正在生成分析报告..."
python report_generator_clean.py
if [ $? -eq 0 ]; then
    echo "✅ 报告生成完成"
else
    echo "❌ 报告生成失败"
    exit 1
fi

# 3. 检查生成的文件
echo ""
echo "3️⃣ 生成的文件列表:"
echo "----------------------------------------"
ls -la analysis_report.* | awk '{print $9 ": " $5 " bytes"}'

# 4. 显示报告预览
echo ""
echo "4️⃣ 报告内容预览:"
echo "----------------------------------------"
echo "📄 分析标题:"
head -1 analysis_report.md
echo ""
echo "📊 关键数据:"
grep -A 5 "核心发现" analysis_report.md
echo ""
echo "💡 主要建议:"
grep -A 3 "建议重点" analysis_report.md

# 5. 启动Streamlit（可选）
echo ""
echo "5️⃣ 是否启动Streamlit看板？(y/n)"
read -r choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo ""
    echo "🚀 启动Streamlit看板..."
    echo "请在浏览器中访问: http://localhost:8501"
    echo "按 Ctrl+C 停止服务"
    streamlit run ai_maturity_dashboard.py
fi

echo ""
echo "=========================================="
echo "🎉 演示完成！"
echo ""
echo "📁 生成的文件:"
echo "   - analysis_report.md (Markdown格式)"
echo "   - analysis_report.html (HTML格式)"
echo ""
echo "🌐 查看HTML报告: open analysis_report.html"
echo "🎨 启动交互看板: streamlit run ai_maturity_dashboard.py"
echo "=========================================="