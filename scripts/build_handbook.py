#!/usr/bin/env python3
"""Build the offline handbook from the maintained SOP and requirement template."""

import argparse
import html
import json
import re
from pathlib import Path

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATH = re.compile(r"file://|/(?:Users|home)/|[A-Za-z]:\\Users\\", re.I)


def render_document(source, prefix):
    renderer = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = renderer.parse(source)
    if tokens and tokens[0].type == "heading_open" and tokens[0].tag == "h1":
        tokens = tokens[3:]
    headings = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            title = tokens[index + 1].content
            step = re.match(r"第 (\d+) 步", title)
            anchor = f"{prefix}-step-{step[1]}" if step else f"{prefix}-section-{len(headings) + 1}"
            token.attrSet("id", anchor)
            headings.append({"level": int(token.tag[1:]), "title": title, "id": anchor})
        if token.children:
            for child in token.children:
                if child.type == "link_open":
                    href = child.attrGet("href") or ""
                    if href == "../assets/requirement-template.md":
                        child.attrSet("href", "#template")
                    elif href == "../references/sop.md":
                        child.attrSet("href", "#sop")
                    elif href.startswith(("https://", "http://")):
                        child.attrSet("target", "_blank")
                        child.attrSet("rel", "noopener noreferrer")

    counter = 0

    def fence_rule(items, index, options, env):
        nonlocal counter
        counter += 1
        identifier = f"{prefix}-code-{counter}"
        text = html.escape(items[index].content)
        return (f'<div class="code-sample"><div class="code-toolbar"><span>可复制指令</span>'
                f'<button class="copy-button" type="button" data-copy-target="{identifier}">复制</button>'
                f'</div><pre id="{identifier}"><code>{text}</code></pre></div>\n')

    renderer.renderer.rules["fence"] = fence_rule
    renderer.renderer.rules["table_open"] = lambda *_: (
        '<div class="table-scroll" tabindex="0" role="region" aria-label="表格，可横向滚动"><table>\n')
    renderer.renderer.rules["table_close"] = lambda *_: '</table></div>\n'
    body = renderer.renderer.render(tokens, renderer.options, {})
    nav = "\n".join(
        f'<a href="#{item["id"]}" class="toc-link level-{item["level"]}">{html.escape(item["title"])}</a>'
        for item in headings if item["level"] <= 3
    )
    return body, nav, headings


def build(sop, template):
    if PRIVATE_PATH.search(sop + template):
        raise ValueError("交付源文档包含本机私人路径，请先改为可移植链接")
    sop_body, sop_nav, headings = render_document(sop, "sop")
    template_body, template_nav, _ = render_document(template, "template")
    phase_names = ["收口需求", "分析现状", "确定范围", "方案原型", "规则验收", "评审跟进", "验收上线", "效果复盘"]
    ids = {item["id"] for item in headings}
    roadmap = "".join(
        f'<a class="phase-link" data-step="{i}" href="#sop-step-{i}"><span>{i:02d}</span>{name}<b aria-hidden="true">↗</b></a>'
        for i, name in enumerate(phase_names, 1) if f"sop-step-{i}" in ids
    )
    download_template = template.replace("(../references/sop.md)", "(产品经理SOP.html#sop)")
    data = json.dumps({"template": download_template}, ensure_ascii=False)
    for char, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"),
                          ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        data = data.replace(char, escaped)
    version = re.search(r"版本：([^\s\\]+)", sop)
    updated = re.search(r"更新日期：([0-9-]+)", sop)
    replacements = {
        "@@STYLES@@": (ROOT / "assets" / "handbook.css").read_text(encoding="utf-8"),
        "@@SCRIPT@@": (ROOT / "assets" / "handbook.js").read_text(encoding="utf-8"),
        "@@SOP_BODY@@": sop_body,
        "@@TEMPLATE_BODY@@": template_body,
        "@@SOP_NAV@@": sop_nav,
        "@@TEMPLATE_NAV@@": template_nav,
        "@@ROADMAP@@": roadmap,
        "@@DATA@@": data,
        "@@VERSION@@": html.escape(version[1] if version else "1.1"),
        "@@UPDATED@@": html.escape(updated[1] if updated else "未注明"),
    }
    result = (ROOT / "assets" / "handbook-shell.html").read_text(encoding="utf-8")
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sop", type=Path, default=ROOT / "references" / "sop.md")
    parser.add_argument("--template", type=Path, default=ROOT / "assets" / "requirement-template.md")
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "产品经理SOP.html")
    args = parser.parse_args()
    try:
        result = build(args.sop.read_text(encoding="utf-8"), args.template.read_text(encoding="utf-8"))
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(json.dumps({"output": str(args.output.absolute()), "bytes": len(result.encode("utf-8"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
