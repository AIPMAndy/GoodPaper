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
        # 启动 FastAPI 服务
        import uvicorn
        from goodpaper_mvp.fastapi_server import app

        print(f"🚀 启动 GoodPaper 服务...")
        print(f"📍 http://{args.host}:{args.port}")
        print(f"📖 API 文档: http://{args.host}:{args.port}/docs")
        uvicorn.run(
            "goodpaper_mvp.fastapi_server:app",
            host=args.host,
            port=args.port,
            reload=True,
        )

    elif args.command == "check":
        if not args.paper:
            print("❌ 请指定论文文件: goodpaper check <paper.docx>")
            sys.exit(1)

        from goodpaper_mvp.core_cli import check_paper_cli

        check_paper_cli(
            paper_path=args.paper,
            template_path=args.template,
            template_package=args.package,
        )

    elif args.command == "format":
        if not args.paper:
            print("❌ 请指定论文文件: goodpaper format <paper.docx>")
            sys.exit(1)

        from goodpaper_mvp.core_cli import format_paper_cli

        output_path = args.output or args.paper.replace(".docx", "_formatted.docx")
        format_paper_cli(
            paper_path=args.paper,
            template_path=args.template,
            template_package=args.package,
            output_path=output_path,
        )

    elif args.command == "template":
        from goodpaper_mvp.core_cli import list_templates_cli

        list_templates_cli()


if __name__ == "__main__":
    main()
