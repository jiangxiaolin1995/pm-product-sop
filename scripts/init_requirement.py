#!/usr/bin/env python3
"""Create a new requirement record without replacing an existing file."""

import argparse
import datetime as dt
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def label(value):
    value = value.strip()
    if not value or any(char in value for char in "\r\n\x00"):
        raise argparse.ArgumentTypeError("名称必须是非空的单行文字")
    return value


def calendar_date(value):
    try:
        if dt.date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期必须是有效的 YYYY-MM-DD") from exc
    return value


def markdown_text(value):
    value = html.escape(value, quote=False)
    for char in ("\\", "|", "[", "]", "*", "_", "`", "#"):
        value = value.replace(char, "\\" + char)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=label)
    parser.add_argument("--requirement", required=True, type=label)
    parser.add_argument("--mode", choices=("快速", "标准", "探索"), default="标准")
    parser.add_argument("--date", required=True, type=calendar_date)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    template = (ROOT / "assets" / "requirement-template.md").read_text(encoding="utf-8")
    project, requirement = map(markdown_text, (args.project, args.requirement))
    record = template.replace("【项目名】", project).replace("【需求名】", requirement)
    replacements = {
        "| 项目／需求名称 | 【待填】 |": f"| 项目／需求名称 | {project} / {requirement} |",
        "| 流程模式与选择理由 | 【快速／标准／探索；理由】 |":
            f"| 流程模式与选择理由 | {args.mode}；【待填：选择理由】 |",
        "| 当前阶段与推进状态 | 【待填】 |": "| 当前阶段与推进状态 | 第 1 步 · 待分析 |",
        "| 最近更新时间／记录人 | 【待填】 |":
            f"| 最近更新时间／记录人 | {args.date} / AI 初始化 |",
        "(../references/sop.md)": f"(<{ROOT / 'references' / 'sop.md'}>)",
    }
    for old, new in replacements.items():
        record = record.replace(old, new)

    output = args.output.expanduser().absolute()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            handle.write(record)
    except FileExistsError:
        parser.error(f"记录已存在，未覆盖；请读取后继续维护：{output}")
    print(json.dumps({"created": str(output), "mode": args.mode}, ensure_ascii=False))


if __name__ == "__main__":
    main()
