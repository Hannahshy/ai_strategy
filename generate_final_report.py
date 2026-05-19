"""
生成最终分析报告
"""
import report_generator

# 生成Markdown报告
print("正在生成分析报告...")
report = report_generator.generate_report()

# 保存Markdown文件
with open("analysis_report.md", "w", encoding="utf-8") as f:
    f.write(report)
print("✅ Markdown报告已保存")

# 生成HTML文件
html_content = report_generator.markdown_to_html(report)
with open("analysis_report.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ HTML报告已保存")

print("\n📊 报告生成完成！")
print("- analysis_report.md")
print("- analysis_report.html")
print("\n📝 报告包含内容：")
print("- 执行摘要")
print("- 数据概览")
print("- 关键发现")
print("- 模型结果")
print("- 建议措施")