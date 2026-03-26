#!/usr/bin/env python3
"""
GoodPaper - 学术论文格式检查与自动排版工具
主入口文件
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 确保 goodpaper_mvp 在路径中
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(
        prog="goodpaper",
        description="学术论文格式检查与自动排版工具",
    )
    parser.add_argument(
        "command",
        choices=["check", "format", "serve", "template"],
        help="命令: check=检查格式, format=自动排版, serve=启动Web服务, template=模板管理",
    )
    parser.add_argument("paper", nargs="?", help="论文文件路径 (.docx)")
    parser.add_argument("-t", "--template", help="模板文件路径 (.docx)")
    parser.add_argument("-p", "--package", help="内置模板包名称")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--port", type=int, default=8787, help="服务端口 (默认: 8787)")
    parser.add_argument("--host", default="127.0.0.1", help="服务主机 (默认: 127.0.0.1)")

    args = parser.parse_args()

    if args.command == "serve":
        # 启动内置 HTTP 服务
        from goodpaper_mvp.server import run_server

        print(f"🚀 启动 GoodPaper 服务...")
        print(f"📍 http://{args.host}:{args.port}")
        run_server(host=args.host, port=args.port)

    elif args.command == "check":
        if not args.paper:
            print("❌ 请指定论文文件: goodpaper check <paper.docx>")
            sys.exit(1)

        from goodpaper_mvp.core import analyze_document
        from pathlib import Path

        paper_path = Path(args.paper)
        if not paper_path.exists():
            print(f"❌ 文件不存在: {paper_path}")
            sys.exit(1)

        print(f"📄 正在检查: {paper_path.name}")
        print("-" * 50)

        # 使用默认模板
        from goodpaper_mvp.templates import get_default_template_package
        template_pkg = get_default_template_package()
        template_path = template_pkg.template_path if hasattr(template_pkg, 'template_path') else str(template_pkg)

        result = analyze_document(Path(template_path), paper_path)

        # 显示结果
        issues = result.get("issues", [])
        summary = result.get("summary", {})

        print(f"\n📊 检查结果:")
        print(f"   问题总数: {summary.get('total_issues', len(issues))}")
        print(f"   严重: {summary.get('error_count', 0)} | 警告: {summary.get('warning_count', 0)} | 提示: {summary.get('info_count', 0)}")

        if issues:
            print(f"\n🔍 前 5 个问题:")
            for i, issue in enumerate(issues[:5], 1):
                severity = issue.get("severity", "info")
                icon = "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
                print(f"   {i}. {icon} [{issue.get('category', 'unknown')}] {issue.get('message', '')}")

        # 保存报告
        report_path = paper_path.parent / f"{paper_path.stem}_report.json"
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 报告已保存: {report_path}")

    elif args.command == "format":
        if not args.paper:
            print("❌ 请指定论文文件: goodpaper format <paper.docx>")
            sys.exit(1)

        from goodpaper_mvp.core import format_document
        from pathlib import Path

        paper_path = Path(args.paper)
        if not paper_path.exists():
            print(f"❌ 文件不存在: {paper_path}")
            sys.exit(1)

        output_path = Path(args.output) if args.output else paper_path.parent / f"{paper_path.stem}_formatted.docx"

        print(f"📄 正在排版: {paper_path.name}")
        print("-" * 50)

        from goodpaper_mvp.templates import get_default_template_package
        template_ctx = get_default_template_package()

        format_document(str(paper_path), str(output_path), template_ctx)

        print(f"✅ 排版完成: {output_path}")

    elif args.command == "template":
        from goodpaper_mvp.templates import list_template_packages

        print("📋 可用模板:")
        print("-" * 50)

        packages = list_template_packages()
        for pkg in packages:
            pkg_dict = pkg.to_dict()
            print(f"\n📄 {pkg_dict.get('name', 'unknown')}")
            print(f"   版本: {pkg_dict.get('version', 'N/A')}")
            print(f"   描述: {pkg_dict.get('description', 'N/A')}")


if __name__ == "__main__":
    main()
