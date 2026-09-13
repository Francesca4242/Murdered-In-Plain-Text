#!/usr/bin/env python3
"""Compile the Twee source of Murdered In Plain Text into a playable index.html.

The SugarCube 2.37.3 runtime is not vendored as a dependency: it is kept as a
shell (build/sugarcube-2.37.3-shell.html) extracted from the Twine-published
story, with a {{STORYDATA}} placeholder where the story data belongs. This
script parses the Twee source and splices a fresh <tw-storydata> block in.

Usage:
    python3 build/build.py [source.twee] [-o index.html] [--check]

--check validates the story without writing output: it reports duplicate
passage names, links that point at passages which do not exist, and passages
that nothing links to.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "build" / "sugarcube-2.37.3-shell.html"
DEFAULT_SOURCE = ROOT / "Murdered In Plain Text.twee"
DEFAULT_OUTPUT = ROOT / "index.html"

SPECIAL = {"StoryTitle", "StoryData"}
HEADER_RE = re.compile(r"^::\s*(?P<rest>.+)$")
META_RE = re.compile(
    r"^(?P<name>.*?)"
    r"(?:\s*\[(?P<tags>[^\]]*)\])?"
    r"(?:\s*(?P<meta>\{.*\}))?\s*$"
)

# Ways a passage can be linked to from another passage.
LINK_PATTERNS = (
    re.compile(r'data-passage\s*=\s*"([^"]+)"'),     # <button data-passage="X">
    re.compile(r"data-passage\s*=\s*'([^']+)'"),
    re.compile(r"\[\[([^\]]+)\]\]"),                  # [[X]] / [[text|X]]
    re.compile(r'<<link\s+"[^"]*"\s+"([^"]+)"'),      # <<link "text" "X">>
    re.compile(r'<<goto\s+"([^"]+)"'),                # <<goto "X">>
    re.compile(r'Engine\.play\(\s*[\'"]([^\'"]+)'),   # Engine.play('X')
)


class Passage:
    def __init__(self, name: str, tags: str, meta: str) -> None:
        self.name = name
        self.tags = tags or ""
        self.meta = meta or ""
        self.lines: list[str] = []

    @property
    def text(self) -> str:
        return "\n".join(self.lines).strip("\n")


def parse(source: str) -> tuple[list[Passage], dict]:
    passages: list[Passage] = []
    current: Passage | None = None
    for raw in source.splitlines():
        header = HEADER_RE.match(raw) if raw.startswith(":: ") else None
        if header:
            parts = META_RE.match(header.group("rest"))
            current = Passage(
                parts.group("name").strip(),
                parts.group("tags"),
                parts.group("meta"),
            )
            passages.append(current)
        elif current is not None:
            current.lines.append(raw)
    story = {p.name: p for p in passages}
    if "StoryData" not in story:
        raise SystemExit("error: source has no :: StoryData passage")
    data = json.loads(story["StoryData"].text)
    return [p for p in passages if p.name not in SPECIAL], data


def link_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for pattern in LINK_PATTERNS:
        for hit in pattern.findall(text):
            target = hit.split("|")[-1].split("->")[-1].strip()
            if target and not target.startswith(("http", "$", "_")):
                targets.add(html.unescape(target))
    return targets


def check(passages: list[Passage], data: dict) -> int:
    names = [p.name for p in passages]
    known = set(names)
    problems = 0

    duplicates = sorted({n for n in names if names.count(n) > 1})
    for name in duplicates:
        print(f"duplicate passage: {name!r}")
        problems += 1

    start = data.get("start", "Start")
    if start not in known:
        print(f"start passage {start!r} does not exist")
        problems += 1

    linked: set[str] = set()
    for passage in passages:
        for target in link_targets(passage.text):
            linked.add(target)
            if target not in known:
                print(f"broken link: {passage.name!r} -> {target!r}")
                problems += 1

    special = {"StoryInit", "StoryCaption", "StoryInterface", "PassageReady",
               "PassageDone", "PassageHeader", "PassageFooter", "StoryScript",
               "StoryStylesheet", start}
    for passage in passages:
        if passage.name in special or "widget" in passage.tags:
            continue
        if passage.name not in linked:
            print(f"unreachable passage (nothing links to it): {passage.name!r}")
            problems += 1

    print(f"{len(passages)} passages checked, {problems} problem(s) found")
    return problems


def raw(text: str, what: str) -> str:
    """Return text unchanged, refusing anything that would close its element.

    Script and stylesheet content is embedded verbatim, so a literal
    "</script>" or "</style>" inside it would end the element early.
    """
    for tag in ("</script", "</style"):
        if tag in text.lower():
            raise SystemExit(f"error: {what} content contains {tag}>")
    return text


def render(passages: list[Passage], data: dict) -> str:
    script = [p for p in passages if "script" in p.tags.split()]
    stylesheet = [p for p in passages if "stylesheet" in p.tags.split()]
    story = [p for p in passages
             if not {"script", "stylesheet"} & set(p.tags.split())]

    pids = {p.name: i + 1 for i, p in enumerate(story)}
    start = data.get("start", "Start")

    tag_colors = "".join(
        f'<tw-tag name="{html.escape(name)}" color="{html.escape(color)}"></tw-tag>'
        for name, color in (data.get("tag-colors") or {}).items()
    )

    attrs = (
        f'<tw-storydata name="{html.escape(data.get("name", "Murdered In Plain Text"))}" '
        f'startnode="{pids[start]}" creator="build.py" creator-version="1.0.0" '
        f'format="{html.escape(data.get("format", "SugarCube"))}" '
        f'format-version="{html.escape(data.get("format-version", "2.37.3"))}" '
        f'ifid="{html.escape(data["ifid"])}" options="" tags="" '
        f'zoom="{data.get("zoom", 1)}" hidden>'
    )

    # <style> and <script> are raw-text elements: their content must NOT be
    # entity-escaped or the browser hands SugarCube literal "&lt;" sequences.
    # <tw-passagedata> is an ordinary element, so its content must be.
    parts = [attrs]
    parts.append(
        '<style role="stylesheet" id="twine-user-stylesheet" '
        'type="text/twine-css">'
        + raw("\n\n".join(p.text for p in stylesheet), "stylesheet")
        + "</style>"
    )
    parts.append(
        '<script role="script" id="twine-user-script" '
        'type="text/twine-javascript">'
        + raw("\n\n".join(p.text for p in script), "script")
        + "</script>"
    )
    parts.append(tag_colors)
    for passage in story:
        parts.append(
            f'<tw-passagedata pid="{pids[passage.name]}" '
            f'name="{html.escape(passage.name, quote=True)}" '
            f'tags="{html.escape(" ".join(passage.tags.split()), quote=True)}" '
            f'position="0,0" size="100,100">'
            + html.escape(passage.text, quote=True)
            + "</tw-passagedata>"
        )
    parts.append("</tw-storydata>")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=str(DEFAULT_SOURCE))
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check", action="store_true",
                        help="validate the story instead of writing output")
    args = parser.parse_args()

    source = Path(args.source)
    passages, data = parse(source.read_text(encoding="utf-8"))

    if args.check:
        return 1 if check(passages, data) else 0

    if not SHELL.exists():
        raise SystemExit(f"error: missing runtime shell at {SHELL}")
    shell = SHELL.read_text(encoding="utf-8")
    if "{{STORYDATA}}" not in shell:
        raise SystemExit("error: runtime shell has no {{STORYDATA}} placeholder")

    output = Path(args.output)
    output.write_text(shell.replace("{{STORYDATA}}", render(passages, data)),
                      encoding="utf-8")
    print(f"built {output} from {source} ({len(passages)} passages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
