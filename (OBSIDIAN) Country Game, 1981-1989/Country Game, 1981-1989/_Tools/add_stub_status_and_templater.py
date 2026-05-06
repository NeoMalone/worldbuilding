from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path


VAULT = Path(r"C:\Users\lemon\Downloads\(OBSIDIAN) Country Game, 1981-1989\Country Game, 1981-1989")
TEMPLATE_DIR = VAULT / "99 Templates"
TEMPLATER_DATA = VAULT / ".obsidian" / "plugins" / "templater-obsidian" / "data.json"


def clean_ascii(value: str) -> str:
    value = value.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2026", "...")
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def wrap(text: str) -> str:
    paras = [p.strip() for p in textwrap.dedent(clean_ascii(text)).strip().split("\n\n")]
    out: list[str] = []
    for para in paras:
        if para.startswith("- ") or para.startswith("#") or para.startswith("|") or "[[" in para or para.startswith("<%"):
            out.append(para)
        else:
            out.append(textwrap.fill(para, width=100))
    return "\n\n".join(out).strip() + "\n"


def note_body(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def word_count(path: Path) -> int:
    return len(note_body(path.read_text(encoding="utf-8")).split())


def title_for(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.M)
    return clean_ascii(m.group(1)) if m else path.stem


def link_for(path: Path) -> str:
    return f"[[{path.stem}|{title_for(path)}]]"


def classify_stub(path: Path, text: str, words: int) -> tuple[bool, str, str]:
    rel = path.relative_to(VAULT).as_posix()
    if rel == "00 Atlas/Maintenance/Stub and Empty Article Index.md":
        return False, "", ""
    if re.match(r"^\d{4}-\d{2}-\d{2}\.md$", rel):
        return False, "", ""
    if rel.startswith("99 Templates/") or rel.startswith("_Tools/"):
        return False, "", ""
    if rel.startswith("15 Action Ledger/"):
        return False, "", ""
    if "## Stub Status" in text:
        return True, "already marked", "This note already had a stub status block."
    if "Search the extracted transcript for `" in text:
        return True, "operation registry stub", "This operation page exists because the operation name appears in the transcript, but it still needs a fuller campaign write-up."
    if "No direct source snippet found" in text or "No direct dated event mention found" in text:
        return True, "source-light granular stub", "This granular node is useful for graph structure but still needs stronger source context and a fuller canon summary."
    if "No dated events are assigned directly to this hub" in text:
        return True, "thin graph hub", "This hub is structurally useful, but it currently has little direct content assigned to it."
    if words < 120 and not rel.startswith("_Sources/"):
        return True, "thin note", "This note is short enough that it should be considered a candidate for later expansion."
    return False, "", ""


def add_status_tag(text: str, tag: str) -> str:
    if tag in text:
        return text
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) != 3:
        return text
    fm = parts[1]
    body = parts[2]
    if "tags:" not in fm:
        fm += f"\ntags:\n  - {tag}\n"
    else:
        fm = re.sub(r"(tags:\n(?:  - .+\n)*)", lambda m: m.group(1) + f"  - {tag}\n", fm, count=1)
    return f"---{fm}---{body}"


def stub_block(kind: str, reason: str) -> str:
    return wrap(
        f"""
## Stub Status

This page is currently marked as a **{kind}**. It is not useless or empty; it is a graph anchor that keeps this part of the Country Game canon visible while the surrounding article is still thin.

**Why it is marked:** {reason}

## How To Expand With Templater

Use [[Country Game - Stub Expansion Template]] or [[Country Game - Full Article Template]] with the Templater command palette. Good expansion sources are [[Complete Action Ledger]], [[Granular Node Index]], the related event pages linked above, and [[80s country game source note]].

## Expansion Checklist

- [ ] Add a stronger lead paragraph explaining the subject in plain wiki style.
- [ ] Add source-backed details from the extracted transcript or PDF page range.
- [ ] Link at least three related countries, operations, people, technologies, or concepts.
- [ ] Add an "Outcome" or "Legacy" section if this page describes an action, operation, or event.
- [ ] Remove `status/stub` from the frontmatter once the page has a real article body.
"""
    )


def create_templates() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    templates = {
        "Country Game - Full Article Template.md": r'''<%*
const title = tp.file.title;
const today = tp.date.now("YYYY-MM-DD");
-%>
---
title: "<% title %>"
aliases:
  - 
tags:
  - country-game/wiki
  - status/draft
  - type/article
canon: "fictional alternate-history role-play based on 80s country game.pdf"
created: "<% today %>"
---

# <% title %>

## Lead

Write a concise encyclopedia-style summary of what this subject is, when it appears, and why it matters in the Country Game canon.

## Infobox

| Field | Detail |
| --- | --- |
| Canon role |  |
| First appearance |  |
| Main actors |  |
| Related operations |  |
| Related territories |  |

## Background

Explain the setup or earlier events that make this subject important.

## Canon Account

Describe what happens in chronological order. Prefer links to action-ledger nodes and dated event pages.

## Outcome

Summarize what changed because of this subject.

## Related Nodes

- [[Complete Action Ledger]]
- [[Granular Node Index]]
- [[Timeline 1981-1989]]

## Source Notes

- [[80s country game source note]]
''',
        "Country Game - Stub Expansion Template.md": r'''<%*
const title = tp.file.title;
const today = tp.date.now("YYYY-MM-DD");
-%>
## Expansion Draft - <% today %>

### Better Lead

Replace this with a fuller lead for **<% title %>**. Include the subject's role, the year or campaign, and why it matters.

### Source Details To Add

- Source page or event:
- Important action-ledger links:
- Countries/actors involved:
- Equipment or institutions involved:

### Missing Sections

- [ ] Background
- [ ] Main canon account
- [ ] Outcome
- [ ] Related nodes
- [ ] Source notes

### Cleanup

- [ ] Remove or rewrite the Stub Status block.
- [ ] Remove `status/stub` from frontmatter when the article is no longer a stub.
''',
        "Country Game - Operation Template.md": r'''<%*
const title = tp.file.title;
-%>
---
title: "<% title %>"
aliases:
  - 
tags:
  - country-game/wiki
  - group/campaign
  - type/operation
  - status/draft
canon: "fictional alternate-history role-play based on 80s country game.pdf"
---

# <% title %>

<span class="cg-badge cg-campaign">Campaigns and annexations</span>

## Lead

Describe the operation's target, belligerents, year, and strategic purpose.

## Operational Summary

| Field | Detail |
| --- | --- |
| Year |  |
| Main attacker |  |
| Target |  |
| Outcome |  |

## Phases

1. 
2. 
3. 

## Forces And Equipment

- 

## Outcome And Legacy

-

## Related Nodes

- [[Major Operations of the Country Game]]
- [[Complete Action Ledger]]
''',
        "Country Game - Territory Template.md": r'''<%*
const title = tp.file.title;
-%>
---
title: "<% title %>"
aliases:
  - 
tags:
  - country-game/wiki
  - group/faction
  - type/territory
  - status/draft
canon: "fictional alternate-history role-play based on 80s country game.pdf"
---

# <% title %>

<span class="cg-badge cg-faction">Factions and states</span>

## Lead

Explain how this territory appears in the canon and which campaign or faction controls it.

## Canon Timeline

- 

## Strategic Importance

- 

## Related Nodes

- [[Country and Territory Index]]
- [[Complete Action Ledger]]
''',
        "Country Game - Action Node Template.md": r'''<%*
const title = tp.file.title;
-%>
---
title: "<% title %>"
aliases:
  - 
tags:
  - country-game/wiki
  - type/action
  - status/draft
canon: "fictional alternate-history role-play based on 80s country game.pdf"
---

# <% title %>

## Lead

Summarize this individual action, reaction, outcome, or plan.

## Canon Heading


## Canon Context


## Links

- [[Complete Action Ledger]]
- [[Timeline 1981-1989]]
''',
    }
    for name, content in templates.items():
        (TEMPLATE_DIR / name).write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def configure_templater() -> None:
    TEMPLATER_DATA.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "command_timeout": 5,
        "templates_folder": "99 Templates",
        "templates_pairs": [],
        "trigger_on_file_creation": False,
        "auto_jump_to_cursor": True,
        "enable_system_commands": False,
        "shell_path": "",
        "user_scripts_folder": "",
        "enable_folder_templates": False,
        "folder_templates": [],
        "syntax_highlighting": True,
        "syntax_highlighting_mobile": False,
        "enabled_templates_hotkeys": [],
        "startup_templates": [],
    }
    if TEMPLATER_DATA.exists():
        try:
            existing = json.loads(TEMPLATER_DATA.read_text(encoding="utf-8"))
            existing.update(data)
            data = existing
        except Exception:
            pass
    TEMPLATER_DATA.write_text(json.dumps(data, indent=2), encoding="utf-8", newline="\n")


def patch_notes() -> list[tuple[Path, int, str]]:
    patched: list[tuple[Path, int, str]] = []
    for path in sorted(VAULT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        words = word_count(path)
        is_stub, kind, reason = classify_stub(path, text, words)
        if not is_stub or kind == "already marked":
            continue
        text = add_status_tag(text, "status/stub")
        text = text.rstrip() + "\n\n" + stub_block(kind, reason)
        path.write_text(text, encoding="utf-8", newline="\n")
        patched.append((path, words, kind))
    return patched


def cleanup_non_wiki_daily_note() -> None:
    daily = VAULT / "2026-05-04.md"
    if not daily.exists():
        return
    text = daily.read_text(encoding="utf-8")
    if "This page is currently marked as a **thin note**" in text and "# 2026-05-04" not in text:
        daily.write_text("", encoding="utf-8", newline="\n")


def write_stub_index(patched: list[tuple[Path, int, str]]) -> None:
    maintenance = VAULT / "00 Atlas" / "Maintenance"
    maintenance.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[tuple[Path, int, str]]] = {}
    for item in patched:
        grouped.setdefault(item[2], []).append(item)
    lines = [
        "---",
        'title: "Stub and Empty Article Index"',
        "aliases:",
        "  - Stub Index",
        "tags:",
        "  - country-game/wiki",
        "  - group/atlas",
        "  - type/index",
        "  - status/maintenance",
        'canon: "fictional alternate-history role-play based on 80s country game.pdf"',
        "---",
        "",
        "# Stub and Empty Article Index",
        "",
        '<span class="cg-badge cg-atlas">Atlas and indexes</span>',
        "",
        "## Lead",
        "",
        "This maintenance page lists notes that were thin, source-light, or operation-registry placeholders when the Templater pass ran. These are not bad pages; they are expansion targets.",
        "",
        "## Templater Workflow",
        "",
        "- Use [[Country Game - Stub Expansion Template]] to expand an existing stub.",
        "- Use [[Country Game - Full Article Template]] when turning a stub into a full article.",
        "- Use [[Country Game - Operation Template]] for operation pages.",
        "- Templater is configured to use the `99 Templates` folder.",
        "",
    ]
    for kind in sorted(grouped):
        lines.extend([f"## {kind.title()}", ""])
        for path, words, _ in grouped[kind]:
            lines.append(f"- {link_for(path)} - {words} words currently")
        lines.append("")
    (maintenance / "Stub and Empty Article Index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def current_stub_items() -> list[tuple[Path, int, str]]:
    items: list[tuple[Path, int, str]] = []
    for path in sorted(VAULT.rglob("*.md")):
        rel = path.relative_to(VAULT).as_posix()
        if rel == "00 Atlas/Maintenance/Stub and Empty Article Index.md":
            continue
        if rel.startswith("99 Templates/") or rel.startswith("_Tools/") or rel.startswith("15 Action Ledger/"):
            continue
        if re.match(r"^\d{4}-\d{2}-\d{2}\.md$", rel):
            continue
        text = path.read_text(encoding="utf-8")
        if "## Stub Status" not in text and "status/stub" not in text:
            continue
        m = re.search(r"currently marked as a \*\*([^*]+)\*\*", text)
        kind = m.group(1) if m else "stub"
        items.append((path, word_count(path), kind))
    return items


def patch_atlas_and_index() -> None:
    atlas = VAULT / "00 Atlas" / "Country Game 1981-1989 Atlas.md"
    if atlas.exists():
        text = atlas.read_text(encoding="utf-8")
        if "[[Stub and Empty Article Index]]" not in text:
            text = text.replace(
                "- [[Complete Action Ledger]] lists every extracted action, reaction, outcome, plan, and operation-level move.",
                "- [[Complete Action Ledger]] lists every extracted action, reaction, outcome, plan, and operation-level move.\n- [[Stub and Empty Article Index]] tracks pages that still need expansion.\n- [[Country Game - Full Article Template]] and [[Country Game - Stub Expansion Template]] provide Templater layouts.",
            )
            atlas.write_text(text, encoding="utf-8", newline="\n")
    canon = VAULT / "00 Atlas" / "Canon Index.md"
    if canon.exists():
        text = canon.read_text(encoding="utf-8")
        if "[[Stub and Empty Article Index]]" not in text:
            text = text.rstrip() + "\n\n## Maintenance\n\n- [[Stub and Empty Article Index]]\n- [[Country Game - Full Article Template]]\n- [[Country Game - Stub Expansion Template]]\n"
            canon.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    create_templates()
    configure_templater()
    cleanup_non_wiki_daily_note()
    patched = patch_notes()
    write_stub_index(current_stub_items())
    patch_atlas_and_index()
    print(f"Created {len(list(TEMPLATE_DIR.glob('*.md')))} Templater templates")
    print(f"Marked and described {len(patched)} stubs/thin notes")


if __name__ == "__main__":
    main()
