"""
企业AI成熟度分析运行脚本
一键执行数据处理、看板启动和报告生成
"""
import os
import subprocess
import webbrowser
import time
from datetime import datetime

def run_data_processing():
    """运行数据处理和分析"""
    print("🔧 正在执行数据处理和分析...")
    try:
        # 运行数据处理脚本
        result = subprocess.run(["python", "data_processing.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 数据处理完成")
            return True
        else:
            print("❌ 数据处理失败:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 运行数据处理器时出错: {e}")
        return False

def generate_report():
    """生成分析报告"""
    print("\n📄 正在生成分析报告...")
    try:
        result = subprocess.run(["python", "report_generator.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 报告生成完成")
            return True
        else:
            print("❌ 报告生成失败:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 生成报告时出错: {e}")
        return False

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'markdown'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    print("✅ 所有依赖已安装")
    return True

def run_dashboard():
    """启动Streamlit看板"""
    print("\n🚀 正在启动Streamlit看板...")

    # 检查是否已有端口被占用
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 8501))
        sock.close()
    except:
        print("⚠️  端口8501已被占用，请先关闭其他Streamlit应用")
        return False

    # 启动streamlit
    try:
        subprocess.Popen(['streamlit', 'run', 'ai_maturity_dashboard.py',
                         '--server.port=8501',
                         '--server.headless=True',
                         '--server.runOnSave=True'])

        print("✅ Streamlit看板已启动")
        print("📱 在浏览器中访问: http://localhost:8501")

        # 等待几秒后自动打开浏览器
        time.sleep(2)
        webbrowser.open('http://localhost:8501')

        return True
    except Exception as e:
        print(f"❌ 启动Streamlit时出错: {e}")
        return False

def show_files():
    """显示生成的文件"""
    print("\n📊 生成的文件列表:")
    files_to_check = [
        "ai_maturity_scores.csv",
        "ai_maturity_gaps.csv",
        "ai_maturity_recommendations.csv",
        "roadmaps.json",
        "analysis_report.html",
        "analysis_report.md"
    ]

    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} (未生成)")

def main():
    """主函数"""
    print("=" * 60)
    print("🏢 企业AI成熟度分析系统")
    print("=" * 60)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 检查依赖
    print("1. 检查依赖...")
    if not check_dependencies():
        return

    # 2. 运行数据处理
    print("\n2. 运行数据处理...")
    if not run_data_processing():
        return

    # 3. 生成报告
    print("\n3. 生成分析报告...")
    if not generate_report():
        return

    # 4. 显示生成的文件
    show_files()

    # 5. 启动看板（可选）
    print("\n" + "=" * 60)
    print("选择操作:")
    print("1. 启动Streamlit看板 (推荐)")
    print("2. 仅生成报告，不启动看板")
    print("3. 退出")

    try:
        choice = input("\n请输入选择 (1-3): ").strip()

        if choice == "1":
            print("\n启动看板...")
            run_dashboard()
            print("\n💡 提示: 按 Ctrl+C 停看板服务")
        elif choice == "2":
            print("\n✨ 分析完成！报告已生成。")
        elif choice == "3":
            print("\n👋 退出程序")
        else:
            print("\n❌ 无效选择，默认退出")
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except:
        print("\n❌ 输入错误，程序退出")

if __name__ == "__main__":
    main()