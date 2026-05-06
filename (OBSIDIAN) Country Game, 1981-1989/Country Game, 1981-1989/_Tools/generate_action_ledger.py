from __future__ import annotations

import re
import shutil
import textwrap
from pathlib import Path
from typing import Iterable


VAULT = Path(r"C:\Users\lemon\Downloads\(OBSIDIAN) Country Game, 1981-1989\Country Game, 1981-1989")
SOURCE = VAULT / "_Sources" / "80s country game extracted transcript.txt"
ACTION_ROOT = VAULT / "15 Action Ledger"


GROUPS = {
    "atlas": {"tag": "group/atlas", "label": "Atlas and indexes", "class": "cg-atlas"},
    "faction": {"tag": "group/faction", "label": "Factions and states", "class": "cg-faction"},
    "cold-war": {"tag": "group/cold-war", "label": "Early Cold War crisis", "class": "cg-cold-war"},
    "letf-state": {"tag": "group/letf-state", "label": "L.E.T.F. state system", "class": "cg-letf"},
    "campaign": {"tag": "group/campaign", "label": "Campaigns and annexations", "class": "cg-campaign"},
    "ideology": {"tag": "group/ideology", "label": "Religion and culture", "class": "cg-ideology"},
    "technology": {"tag": "group/technology", "label": "Technology and weapons", "class": "cg-technology"},
    "timeline": {"tag": "group/timeline", "label": "Timeline", "class": "cg-timeline"},
    "final-war": {"tag": "group/final-war", "label": "Final war and aftermath", "class": "cg-final"},
}


def clean_ascii(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€”": "-",
        "â€“": "-",
        "Ã¡": "a",
        "Ã©": "e",
        "Ã£": "a",
        "Ãº": "u",
        "Ã­": "i",
        "Ã³": "o",
        "Ã§": "c",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def slug_filename(title: str) -> str:
    value = clean_ascii(title)
    value = value.replace(":", " -").replace("/", " and ")
    value = re.sub(r'[<>:"/\\|?*]', "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:150]


def link(title: str, label: str | None = None) -> str:
    title = clean_ascii(title)
    if label and clean_ascii(label) != title:
        return f"[[{title}|{clean_ascii(label)}]]"
    return f"[[{title}]]"


def badge(group: str) -> str:
    meta = GROUPS[group]
    return f'<span class="cg-badge {meta["class"]}">{meta["label"]}</span>'


def wrap(text: str) -> str:
    paras = [p.strip() for p in textwrap.dedent(clean_ascii(text)).strip().split("\n\n")]
    out: list[str] = []
    for para in paras:
        if (
            para.startswith("|")
            or para.startswith("#")
            or para.startswith("- ")
            or para.startswith("<")
            or "[[" in para
            or para.count("\n") > 4
        ):
            out.append(para)
        else:
            out.append(textwrap.fill(para, width=100))
    return "\n\n".join(out).strip() + "\n"


def frontmatter(title: str, group: str, kind: str, aliases: Iterable[str] = (), extra: dict | None = None) -> str:
    lines = ["---", f'title: "{clean_ascii(title)}"', "aliases:"]
    for alias in aliases:
        lines.append(f"  - {clean_ascii(alias)}")
    lines.extend(
        [
            "tags:",
            "  - country-game/wiki",
            f"  - {GROUPS[group]['tag']}",
            f"  - type/{kind}",
            'canon: "fictional alternate-history role-play based on 80s country game.pdf"',
        ]
    )
    if extra:
        for key, value in extra.items():
            lines.append(f'{key}: "{str(value).replace(chr(34), chr(39))}"')
    lines.extend(["---", ""])
    return "\n".join(lines)


def write_note(folder: str, title: str, group: str, kind: str, body: str, aliases: Iterable[str] = (), extra: dict | None = None) -> Path:
    folder_path = VAULT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    path = folder_path / f"{slug_filename(title)}.md"
    content = frontmatter(title, group, kind, aliases, extra)
    content += f"# {clean_ascii(title)}\n\n{badge(group)}\n\n{wrap(body)}"
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def heading_re() -> re.Pattern:
    return re.compile(
        r"^(January|February|March|April|May|June|July|August|September|October|November|December|Late|Mid)?\s*\d{4}:|"
        r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}:"
    )


def needs_title_continuation(value: str) -> bool:
    last_word = re.sub(r"[^A-Za-z0-9'.-]+$", "", value).split(" ")[-1].lower()
    return (
        last_word in {"for", "and", "in", "against", "north", "dual-", "the", "of", "jaime", "brazil's", "border", "south"}
        or value.count('"') % 2 == 1
        or value.endswith(",")
    )


def parse_sections() -> list[dict]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    h_re = heading_re()
    heads: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        raw = clean_ascii(line)
        if h_re.match(raw):
            title = raw
            j = i + 1
            while needs_title_continuation(title) and j < len(lines):
                nxt = clean_ascii(lines[j])
                if not nxt or h_re.match(nxt):
                    break
                title = f"{title} {nxt}"
                j += 1
            heads.append((i, title))

    sections: list[dict] = []
    for idx, (start, title) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        start_page = 1
        for prev in lines[: start + 1]:
            m = re.match(r"--- PAGE (\d+) ---", prev.strip())
            if m:
                start_page = int(m.group(1))
        end_page = start_page
        for item in lines[start + 1 : end]:
            m = re.match(r"--- PAGE (\d+) ---", item.strip())
            if m:
                end_page = int(m.group(1))
        sections.append(
            {
                "index": idx + 1,
                "title": clean_ascii(title),
                "event_file": slug_filename(title),
                "lines": lines[start + 1 : end],
                "start_page": start_page,
                "end_page": end_page,
            }
        )
    return sections


def classify_event(title: str) -> str:
    t = title.lower()
    if "final" in t or "nato-l.e.t.f" in t or "vs. united states" in t:
        return "final-war"
    if "phantom" in t or "project" in t or "interceptor" in t:
        return "technology"
    if "pantheon" in t or "morganism" in t or "necrocracy" in t or "religious" in t:
        return "ideology"
    if "ussr" in t and any(y in t for y in ["1981", "march", "april", "february"]):
        return "cold-war"
    if "egypt under" in t or "transformation" in t:
        return "letf-state"
    return "campaign"


def cleaned_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        line = clean_ascii(raw)
        if not line or line.startswith("--- PAGE "):
            continue
        if re.match(
            r"^(What's next|Whats next|What'?s the next move|What.*next move|Would you like|Let me know|This is going to get wild)",
            line,
            re.I,
        ):
            break
        out.append(line)
    return out


def is_action_heading(line: str) -> bool:
    if not line:
        return False
    if len(line) > 150:
        return False
    if re.match(r"^(What|Would you like|Let me know)", line, re.I):
        return False
    if line.endswith(":") and re.match(r'^\d+\.\s+[A-Z][A-Za-z0-9 .\'"&()/-]+:$', line):
        return True
    if line.endswith(":") and re.match(r'^[A-Z][A-Za-z0-9 .\'"&()/-]+:$', line):
        return True
    if re.match(r'^[A-Z][A-Za-z0-9 .\'"&()/-]+:\s+.+', line) and not line.startswith("http"):
        return True
    if re.match(r"^Operation [A-Z][A-Za-z0-9' -]+$", line):
        return True
    return False


def action_kind(heading: str, context: str) -> str:
    hay = f"{heading} {context}".lower()
    if "operation " in hay:
        return "operation"
    if any(w in hay for w in ["invad", "annex", "assault", "offensive", "campaign", "landing"]):
        return "military action"
    if any(w in hay for w in ["outcome", "result", "reaction", "impact", "fallout", "success", "failure"]):
        return "outcome or reaction"
    if any(w in hay for w in ["research", "project", "develop", "test", "designation", "technology"]):
        return "research or technology"
    if any(w in hay for w in ["declare", "announce", "request", "sanction", "alliance", "summit", "diplomatic"]):
        return "diplomatic action"
    if any(w in hay for w in ["religion", "pantheon", "goddess", "shrine", "morganism", "coronation"]):
        return "ideological action"
    if any(w in hay for w in ["rebuild", "repair", "fortify", "defense", "protect", "mobiliz"]):
        return "defense or consolidation"
    return "canon detail"


def actor_from_heading(heading: str) -> str:
    clean = re.sub(r"^\d+\.\s*", "", heading).strip()
    if ":" in clean:
        actor = clean.split(":", 1)[0].strip()
        if actor.lower() not in {
            "outcome",
            "summary",
            "plan",
            "impact",
            "objective",
            "objectives",
            "strategic objectives",
            "military strategy",
            "invasion plan",
            "global reactions",
            "forces deployed",
        }:
            return actor
    if clean.startswith("Operation "):
        return "Operation"
    return "Narrative"


def short_heading(heading: str) -> str:
    value = re.sub(r"^\d+\.\s*", "", heading).strip().strip(":")
    value = re.sub(r"\s+", " ", value)
    if len(value) > 82:
        value = value[:79].rstrip() + "..."
    return value


def action_records(sections: list[dict]) -> list[dict]:
    records: list[dict] = []
    for section in sections:
        lines = cleaned_lines(section["lines"])
        heading_indexes = [i for i, line in enumerate(lines) if is_action_heading(line)]
        for local_num, line_index in enumerate(heading_indexes, 1):
            next_index = heading_indexes[heading_indexes.index(line_index) + 1] if heading_indexes.index(line_index) + 1 < len(heading_indexes) else min(len(lines), line_index + 8)
            raw_heading = lines[line_index]
            context_lines = lines[line_index + 1 : min(next_index, line_index + 9)]
            context = " ".join(context_lines)
            if not context and raw_heading.lower() in {"outcome:", "summary:"}:
                continue
            records.append(
                {
                    "section": section,
                    "local_num": local_num,
                    "heading": raw_heading,
                    "context": context,
                    "kind": action_kind(raw_heading, context),
                    "actor": actor_from_heading(raw_heading),
                }
            )
    for i, record in enumerate(records, 1):
        record["number"] = i
        record["title"] = f"Action {i:04d} - {short_heading(record['heading'])}"
        record["file"] = slug_filename(record["title"])
    return records


def known_nodes() -> list[str]:
    nodes: set[str] = set()
    for folder in [
        "00 Atlas",
        "01 Factions",
        "02 Cold War Crisis",
        "03 LETF State",
        "04 Campaigns",
        "05 Ideology and Culture",
        "06 Technology",
        "08 Final War",
        "09 Countries and Territories",
        "10 Operations",
        "11 People and Leaders",
        "12 Institutions and Alliances",
        "13 Technology and Equipment",
        "14 Concepts and Provinces",
    ]:
        base = VAULT / folder
        if base.exists():
            nodes.update(path.stem for path in base.rglob("*.md"))
    return sorted(nodes, key=len, reverse=True)


ALIASES = {
    "United States of America": ["United States", "U.S.", "USA", "US"],
    "Lowest Egyptian Taper Fade": ["L.E.T.F.", "LETF", "Lowest Egyptian Taper Fade"],
    "Soviet Union": ["USSR", "Soviet Union", "Soviet"],
    "West Germany and NATO": ["West Germany", "NATO"],
    "Boombayah": ["Boombayah", "Brazil"],
    "SR-91 Phantom Sky": ["SR-91", "Phantom Sky"],
    "King Darius Morgan": ["King Darius Morgan", "Darius Morgan"],
    "Adolf Hitler in the Country Game": ["Adolf Hitler", "Hitler"],
    "North Atlantic Treaty Organization": ["NATO"],
    "United Nations": ["U.N.", "UN", "United Nations"],
}


def related_node_links(record: dict, nodes: list[str]) -> list[str]:
    hay = clean_ascii(f"{record['heading']} {record['context']} {record['section']['title']}").lower()
    found: list[str] = []
    for target, aliases in ALIASES.items():
        if any(alias.lower() in hay for alias in aliases):
            found.append(target)
    for node in nodes:
        if node in found or node == record["file"]:
            continue
        needle = node.lower()
        if len(needle) < 4:
            continue
        if needle in hay:
            found.append(node)
        if len(found) >= 24:
            break
    return found[:24]


def year_for_event(title: str) -> str:
    m = re.search(r"(1981|1982|1983|1984|1985|1986|1987|1988|1989)", title)
    return m.group(1) if m else "Undated"


def action_body(record: dict, nodes: list[str], previous_record: dict | None, next_record: dict | None) -> str:
    section = record["section"]
    group = classify_event(section["title"])
    related = related_node_links(record, nodes)
    related_lines = "\n".join(f"- {link(item)}" for item in related) or "- No automatic node matches"
    prev_next = []
    if previous_record:
        prev_next.append(f"- Previous: {link(previous_record['file'], previous_record['title'])}")
    if next_record:
        prev_next.append(f"- Next: {link(next_record['file'], next_record['title'])}")
    sequence_lines = "\n".join(prev_next) or "- No adjacent action in the extracted ledger"
    context = record["context"] or "No additional paragraph was available directly beneath this heading."
    return f"""
## Lead

{record['title']} is a granular action node from the complete Country Game action ledger. It breaks the dated event {link(section['event_file'], section['title'])} into a smaller move, reaction, result, plan, or operational detail.

## Infobox

| Field | Detail |
| --- | --- |
| Ledger number | {record['number']} |
| Event | {link(section['event_file'], section['title'])} |
| Year | {link(year_for_event(section['title']))} |
| Event action number | {record['local_num']} |
| Actor or heading owner | {record['actor']} |
| Action type | {record['kind']} |
| Source pages | {section['start_page']}-{section['end_page']} |

## Canon Heading

{record['heading']}

## Canon Context

{context}

## Related Nodes

{related_lines}

## Sequence

{sequence_lines}

## Ledger Note

This node is intentionally specific. It exists so the graph can show individual actions and outcomes instead of hiding them inside a long event article.
"""


def clean_action_root() -> None:
    if ACTION_ROOT.exists():
        resolved = ACTION_ROOT.resolve()
        vault_resolved = VAULT.resolve()
        if resolved == vault_resolved or vault_resolved not in resolved.parents:
            raise RuntimeError(f"Refusing to delete unexpected path: {resolved}")
        shutil.rmtree(resolved)


def write_action_notes(records: list[dict]) -> None:
    nodes = known_nodes()
    for i, record in enumerate(records):
        previous_record = records[i - 1] if i > 0 else None
        next_record = records[i + 1] if i + 1 < len(records) else None
        year = year_for_event(record["section"]["title"])
        group = classify_event(record["section"]["title"])
        write_note(
            f"15 Action Ledger/{year}",
            record["title"],
            group,
            "action",
            action_body(record, nodes, previous_record, next_record),
            aliases=[record["heading"]],
            extra={
                "ledger_number": record["number"],
                "event": record["section"]["event_file"],
                "action_type": record["kind"],
            },
        )


def write_indexes(records: list[dict]) -> None:
    by_year: dict[str, list[dict]] = {}
    by_kind: dict[str, list[dict]] = {}
    for record in records:
        by_year.setdefault(year_for_event(record["section"]["title"]), []).append(record)
        by_kind.setdefault(record["kind"], []).append(record)

    lines = [
        "## Lead",
        "",
        "The Complete Action Ledger lists every extracted operation, action, reaction, result, plan, and major sub-event heading from the PDF-derived event sections.",
        "",
        "## Year Indexes",
        "",
    ]
    for year in sorted(by_year):
        lines.append(f"- {link(f'{year} Action Ledger')} - {len(by_year[year])} action nodes")
    lines.extend(["", "## Action Type Indexes", ""])
    for kind in sorted(by_kind):
        title = f"Action Type - {kind.title()}"
        lines.append(f"- {link(title)} - {len(by_kind[kind])} nodes")
    lines.extend(["", "## Full Sequence", ""])
    for record in records:
        lines.append(f"- {link(record['file'], record['title'])} - {link(record['section']['event_file'], record['section']['title'])}")
    write_note("15 Action Ledger", "Complete Action Ledger", "atlas", "index", "\n".join(lines), aliases=["Action Ledger Index"])

    for year, items in sorted(by_year.items()):
        year_lines = [f"## Lead\n\n{year} Action Ledger lists every extracted action node for {year}.\n", "## Actions\n"]
        for item in items:
            year_lines.append(f"- {link(item['file'], item['title'])} - {item['kind']} - {link(item['section']['event_file'], item['section']['title'])}")
        write_note("15 Action Ledger/Year Indexes", f"{year} Action Ledger", "timeline", "index", "\n".join(year_lines))

    for kind, items in sorted(by_kind.items()):
        type_lines = [f"## Lead\n\nAction Type - {kind.title()} gathers all ledger nodes classified as {kind}.\n", "## Actions\n"]
        for item in items:
            type_lines.append(f"- {link(item['file'], item['title'])} - {link(item['section']['event_file'], item['section']['title'])}")
        write_note("15 Action Ledger/Type Indexes", f"Action Type - {kind.title()}", "atlas", "index", "\n".join(type_lines))


def patch_event_pages(records: list[dict]) -> None:
    by_event: dict[str, list[dict]] = {}
    for record in records:
        by_event.setdefault(record["section"]["event_file"], []).append(record)
    for event_file, items in by_event.items():
        matches = list((VAULT / "07 Timeline").glob(f"* Event Articles/{event_file}.md"))
        if not matches:
            continue
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        lines = ["## Complete Action Ledger Links\n"]
        for item in items:
            lines.append(f"- {link(item['file'], item['title'])} - {item['kind']} - {clean_ascii(item['heading'])}")
        block = "\n".join(lines).strip() + "\n\n"
        text = re.sub(r"\n## Complete Action Ledger Links\n.*?(?=\n## Granular Node Links|\n## Notes|\Z)", "\n", text, flags=re.S)
        if "\n## Granular Node Links" in text:
            text = text.replace("\n## Granular Node Links", f"\n{block}## Granular Node Links", 1)
        elif "\n## Notes" in text:
            text = text.replace("\n## Notes", f"\n{block}## Notes", 1)
        else:
            text = text.rstrip() + "\n\n" + block
        path.write_text(text, encoding="utf-8", newline="\n")


def extract_operation_names() -> list[str]:
    raw_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    names: list[str] = []
    stop_words = {
        "The",
        "This",
        "With",
        "Following",
        "Forces",
        "Force",
        "Strategic",
        "Objectives",
        "Objective",
        "From",
        "Hearing",
        "Brazil",
        "Plan",
        "Strategy",
        "Details",
        "and",
        "to",
        "succeeds",
        "are",
        "results",
        "is",
        "begins",
        "launches",
        "aims",
    }
    bad = {"Operation Plan", "Operation Strategy", "Operation Details", "Operation Against"}
    for idx, raw in enumerate(raw_lines):
        line = clean_ascii(raw)
        if "Operation " not in line:
            continue
        combined = line
        if idx + 1 < len(raw_lines):
            nxt = clean_ascii(raw_lines[idx + 1])
            if nxt and not nxt.startswith("--- PAGE"):
                combined += " " + nxt
        for match in re.finditer(r"Operation\s+[A-Z][A-Za-z0-9' -]*", combined):
            words = match.group(0).split()
            kept = []
            for word in words:
                clean_word = word.strip(".,:;()")
                if clean_word == "Operation" and kept:
                    break
                if clean_word.isdigit() and clean_word != "2":
                    break
                if kept and clean_word in stop_words:
                    break
                kept.append(clean_word)
                if len(kept) >= 5:
                    break
            name = " ".join(kept).strip()
            name = re.split(r"\s+-\s+|\s+:\s+", name)[0].strip()
            name = re.sub(r"\s+", " ", name)
            if any(name.startswith(x) for x in bad):
                continue
            if len(name.split()) < 3:
                continue
            if name not in names:
                names.append(name)
    return names


def cleanup_noisy_operation_notes(valid_names: set[str]) -> int:
    operations_dir = VAULT / "10 Operations"
    if not operations_dir.exists():
        return 0
    removed = 0
    noisy_patterns = [
        "Forces Deployed",
        "Strategic Objectives",
        " Objectives",
        " Objective",
        " From",
        " Hearing",
        " Brazil",
        " Operation ",
        " 1",
    ]
    for path in operations_dir.glob("Operation*.md"):
        stem = path.stem
        if stem in valid_names:
            continue
        if any(pattern in stem for pattern in noisy_patterns):
            resolved = path.resolve()
            if VAULT.resolve() not in resolved.parents:
                raise RuntimeError(f"Refusing to delete unexpected operation path: {resolved}")
            path.unlink()
            removed += 1
    return removed


def write_missing_operation_notes() -> int:
    valid_names = set(extract_operation_names())
    cleanup_noisy_operation_notes(valid_names)
    existing = {path.stem for path in (VAULT / "10 Operations").glob("*.md")} if (VAULT / "10 Operations").exists() else set()
    count = 0
    for name in sorted(valid_names):
        if slug_filename(name) in existing:
            continue
        body = f"""
## Lead

{name} is a named operation extracted directly from the PDF transcript and added to complete the operation registry.

## Canon Role

The PDF names {name} as part of the Country Game's sequence of invasions, campaigns, plans, counteroperations, or intelligence actions. This page exists so every named operation has its own graph node, even when the operation is also covered inside a broader event or regional article.

## Related Nodes

- [[Complete Action Ledger]]
- [[Major Operations of the Country Game]]
- [[Campaign Hub]]

## Source Lookup

Search the extracted transcript for `{name}` to find the exact surrounding event context.
"""
        write_note("10 Operations", name, "campaign", "operation", body)
        count += 1
    return count


def patch_atlas(records_count: int) -> None:
    atlas_path = VAULT / "00 Atlas" / "Country Game 1981-1989 Atlas.md"
    if atlas_path.exists():
        text = atlas_path.read_text(encoding="utf-8")
        if "[[Complete Action Ledger]]" not in text:
            text = text.replace(
                "- [[Granular Node Index]] lists the expanded small-node layer.",
                "- [[Granular Node Index]] lists the expanded small-node layer.\n- [[Complete Action Ledger]] lists every extracted action, reaction, outcome, plan, and operation-level move.",
            )
        text = re.sub(
            r"Action ledger nodes generated: \d+",
            f"Action ledger nodes generated: {records_count}",
            text,
        )
        if "Action ledger nodes generated:" not in text:
            text = text.rstrip() + f"\n\n## Expansion Status\n\nAction ledger nodes generated: {records_count}\n"
        atlas_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    sections = parse_sections()
    records = action_records(sections)
    clean_action_root()
    missing_ops = write_missing_operation_notes()
    write_action_notes(records)
    write_indexes(records)
    patch_event_pages(records)
    patch_atlas(len(records))
    print(f"Wrote {len(records)} action ledger nodes")
    print(f"Added {missing_ops} missing operation nodes")


if __name__ == "__main__":
    main()
