from __future__ import annotations

import json
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VAULT = Path(r"C:\Users\lemon\Downloads\(OBSIDIAN) Country Game, 1981-1989\Country Game, 1981-1989")
SOURCE = VAULT / "_Sources" / "80s country game extracted transcript.txt"
PDF_SOURCE = Path(r"C:\Users\lemon\Downloads\80s country game.pdf")


GROUPS = {
    "atlas": {
        "tag": "group/atlas",
        "label": "Atlas and indexes",
        "color": "#FFD166",
        "rgb": 0xFFD166,
        "class": "cg-atlas",
        "hub": "Atlas Hub",
        "folder": "00 Atlas",
    },
    "faction": {
        "tag": "group/faction",
        "label": "Factions and states",
        "color": "#118AB2",
        "rgb": 0x118AB2,
        "class": "cg-faction",
        "hub": "Faction Hub",
        "folder": "01 Factions",
    },
    "cold-war": {
        "tag": "group/cold-war",
        "label": "Early Cold War crisis",
        "color": "#EF476F",
        "rgb": 0xEF476F,
        "class": "cg-cold-war",
        "hub": "Cold War Crisis Hub",
        "folder": "02 Cold War Crisis",
    },
    "letf-state": {
        "tag": "group/letf-state",
        "label": "L.E.T.F. state system",
        "color": "#8338EC",
        "rgb": 0x8338EC,
        "class": "cg-letf",
        "hub": "L.E.T.F. State Hub",
        "folder": "03 LETF State",
    },
    "campaign": {
        "tag": "group/campaign",
        "label": "Campaigns and annexations",
        "color": "#F77F00",
        "rgb": 0xF77F00,
        "class": "cg-campaign",
        "hub": "Campaign Hub",
        "folder": "04 Campaigns",
    },
    "ideology": {
        "tag": "group/ideology",
        "label": "Religion and culture",
        "color": "#06D6A0",
        "rgb": 0x06D6A0,
        "class": "cg-ideology",
        "hub": "Ideology Hub",
        "folder": "05 Ideology and Culture",
    },
    "technology": {
        "tag": "group/technology",
        "label": "Technology and weapons",
        "color": "#4D908E",
        "rgb": 0x4D908E,
        "class": "cg-technology",
        "hub": "Technology Hub",
        "folder": "06 Technology",
    },
    "timeline": {
        "tag": "group/timeline",
        "label": "Timeline",
        "color": "#577590",
        "rgb": 0x577590,
        "class": "cg-timeline",
        "hub": "Timeline Hub",
        "folder": "07 Timeline",
    },
    "final-war": {
        "tag": "group/final-war",
        "label": "Final war and aftermath",
        "color": "#E63946",
        "rgb": 0xE63946,
        "class": "cg-final",
        "hub": "Final War Hub",
        "folder": "08 Final War",
    },
}


ENTITY_LINKS = {
    "United States": "United States of America",
    "USA": "United States of America",
    "U.S.": "United States of America",
    "US": "United States of America",
    "L.E.T.F.": "Lowest Egyptian Taper Fade",
    "LETF": "Lowest Egyptian Taper Fade",
    "Lowest Egyptian Taper Fade": "Lowest Egyptian Taper Fade",
    "USSR": "Soviet Union",
    "Soviet": "Soviet Union",
    "Soviet Union": "Soviet Union",
    "Canada": "Canada",
    "West Germany": "West Germany and NATO",
    "NATO": "West Germany and NATO",
    "Boombayah": "Boombayah",
    "Brazil": "Boombayah",
    "Morganism": "Morganism",
    "King Darius Morgan": "King Darius Morgan",
    "Darius Morgan": "King Darius Morgan",
    "Hitler": "Adolf Hitler in the Country Game",
    "Adolf Hitler": "Adolf Hitler in the Country Game",
    "Phantom Sky": "SR-91 Phantom Sky",
    "SR-91": "SR-91 Phantom Sky",
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
    value = value.replace(":", " -")
    value = value.replace("/", " and ")
    value = re.sub(r'[<>:"/\\|?*]', "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:150]


def link(title: str, label: str | None = None) -> str:
    title = clean_ascii(title)
    if label and label != title:
        return f"[[{title}|{clean_ascii(label)}]]"
    return f"[[{title}]]"


def badge(group: str) -> str:
    meta = GROUPS[group]
    return f'<span class="cg-badge {meta["class"]}">{meta["label"]}</span>'


def frontmatter(title: str, group: str, kind: str, aliases: Iterable[str] = (), extra: dict | None = None) -> str:
    tags = ["country-game/wiki", GROUPS[group]["tag"], f"type/{kind}"]
    data = {
        "title": clean_ascii(title),
        "aliases": [clean_ascii(a) for a in aliases],
        "tags": tags,
        "canon": "fictional alternate-history role-play based on 80s country game.pdf",
    }
    if extra:
        data.update(extra)
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f'{key}: "{str(value).replace(chr(34), chr(39))}"')
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def wrap(text: str) -> str:
    text = clean_ascii(text)
    paras = [p.strip() for p in textwrap.dedent(text).strip().split("\n\n")]
    wrapped = []
    for para in paras:
        if (
            para.startswith("|")
            or para.startswith("#")
            or para.startswith("- ")
            or para.startswith(">")
            or para.startswith("<")
            or "[[" in para
            or para.count("\n") > 4
        ):
            wrapped.append(para)
        else:
            wrapped.append(textwrap.fill(para, width=100))
    return "\n\n".join(wrapped).strip() + "\n"


def write_note(folder: str, title: str, group: str, kind: str, body: str, aliases: Iterable[str] = (), extra: dict | None = None) -> Path:
    folder_path = VAULT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    path = folder_path / f"{slug_filename(title)}.md"
    content = frontmatter(title, group, kind, aliases, extra)
    content += f"# {clean_ascii(title)}\n\n{badge(group)}\n\n"
    content += wrap(body)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def parse_sections() -> list[dict]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    heading_re = re.compile(
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

    heads: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        raw = clean_ascii(line)
        if heading_re.match(raw):
            title = raw
            j = i + 1
            join_next = needs_title_continuation(title)
            while join_next and j < len(lines):
                nxt = clean_ascii(lines[j])
                if not nxt or heading_re.match(nxt):
                    break
                title = f"{title} {nxt}"
                j += 1
                join_next = needs_title_continuation(title)
            heads.append((i, title))

    sections = []
    for idx, (start, title) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        chunk = lines[start + 1 : end]
        start_page = 1
        for prev in lines[: start + 1]:
            m = re.match(r"--- PAGE (\d+) ---", prev.strip())
            if m:
                start_page = int(m.group(1))
        end_page = start_page
        for item in chunk:
            m = re.match(r"--- PAGE (\d+) ---", item.strip())
            if m:
                end_page = int(m.group(1))
        sections.append(
            {
                "index": idx + 1,
                "title": clean_ascii(title),
                "lines": chunk,
                "start_line": start + 1,
                "end_line": end,
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
    if "1989:" in t and ("united states leaves" in t or "canada" in t or "poland" in t):
        return "campaign"
    return "campaign"


def cleaned_section_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
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
        cleaned.append(line)
    return cleaned


def section_text(lines: list[str]) -> str:
    cleaned = cleaned_section_lines(lines)
    text = "\n".join(cleaned)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_detailed_account(lines: list[str]) -> str:
    section_heading_re = re.compile(
        r"^(Outcome|Summary|The Plan|Plan|Research Focus|Counteroperation Steps|Strategic Objectives|"
        r"Military Strategy|Invasion Plan|Global Reactions|Forces Deployed|Mission Objectives|"
        r"Mission Plan|Mission Outcome|Performance Review|Funding and Support|Operation Strategy|"
        r"Findings|Key Insights|Next Steps for L\.E\.T\.F\.|Reconstruction Goals|Military Goals):$",
        re.I,
    )
    out: list[str] = []
    for line in cleaned_section_lines(lines):
        if section_heading_re.match(line):
            out.extend(["", f"### {line[:-1]}", ""])
        elif re.match(r"^[A-Z][A-Za-z0-9 .'\-()&]+:$", line) and len(line) <= 80:
            out.extend(["", f"### {line[:-1]}", ""])
        elif re.match(r"^\d+\.\s+[A-Z].{0,85}$", line):
            out.extend(["", line, ""])
        else:
            out.append(line)
    detailed = "\n".join(out)
    detailed = re.sub(r"\n{3,}", "\n\n", detailed)
    return detailed.strip()


def actors_for_text(title: str, body: str) -> list[str]:
    hay = f"{title}\n{body}".lower()
    found = []
    for needle, target in ENTITY_LINKS.items():
        if needle.lower() in hay and target not in found:
            found.append(target)
    return found[:10]


def event_folder(section: dict) -> str:
    m = re.search(r"(1981|1982|1983|1984|1985|1986|1987|1988|1989)", section["title"])
    year = m.group(1) if m else "Undated"
    return f"07 Timeline/{year} Event Articles"


def event_lead(section: dict, group: str, actors: list[str]) -> str:
    title = section["title"]
    actors_text = ", ".join(link(a) for a in actors[:5]) if actors else "the major player states"
    group_link = link(GROUPS[group]["hub"])
    year = re.search(r"(1981|1982|1983|1984|1985|1986|1987|1988|1989)", title)
    year_link = link(year.group(1)) if year else link("Timeline 1981-1989")
    return (
        f"{title} was a dated episode in the fictional Country Game canon. It belongs to the "
        f"{group_link} cluster and is linked to {year_link}. The principal connected actors are "
        f"{actors_text}. The account below converts the PDF transcript into an encyclopedia-style "
        f"event article while preserving the scenario's in-universe sequence and outcome."
    )


def make_event_body(section: dict) -> str:
    title = section["title"]
    group = classify_event(title)
    body = section_text(section["lines"])
    actors = actors_for_text(title, body)
    actor_links = "\n".join(f"- {link(actor)}" for actor in actors) or "- No major actor links detected"
    hub_links = "\n".join(
        [
            f"- {link('Country Game 1981-1989 Atlas')}",
            f"- {link(GROUPS[group]['hub'])}",
            f"- {link('Timeline 1981-1989')}",
            f"- {link('Major Operations of the Country Game')}",
        ]
    )
    # Keep the source account detailed, but remove chatty trailing prompts.
    detailed = format_detailed_account(section["lines"])
    return f"""
## Lead

{event_lead(section, group, actors)}

## Infobox

| Field | Detail |
| --- | --- |
| Event | {clean_ascii(title)} |
| Source pages | {section['start_page']}-{section['end_page']} of [[80s country game source note]] |
| Graph group | {GROUPS[group]['label']} |
| Event number | {section['index']} of 77 |
| Article type | Dated event article |

## Connected Actors

{actor_links}

## Graph Links

{hub_links}

## Detailed Canon Account

{detailed}

## Notes

This article is an in-universe summary of a fictional alternate-history game transcript, not a factual history entry. The original transcript sometimes includes deliberately absurd or anachronistic elements; this page keeps those details as part of the game canon.
"""


MAJOR_ARTICLES = [
    {
        "folder": "00 Atlas",
        "title": "Country Game 1981-1989 Atlas",
        "group": "atlas",
        "kind": "hub",
        "aliases": ["Country Game Atlas", "1981-1989 Country Game"],
        "body": """
## Overview

The Country Game 1981-1989 is a fictional alternate-history geopolitical role-play beginning in February 1981. The initial setup assigns four player countries and modifiers: the United States receives a tripled defense budget, West Germany controls the only working silicon-mining technology, Canada begins as a tax-free state, and the Soviet Union holds abundant nuclear weapons but suffers from disastrous military leadership. The PDF then develops into a sprawling Cold War collapse scenario, a surreal imperial rise under the Lowest Egyptian Taper Fade, and a final global war between the L.E.T.F. and the United States.

The canon is intentionally strange. It mixes real Cold War equipment, fictional state modifiers, bizarre state religions, secret aircraft projects, absurd cultural propaganda, and continent-scale annexation campaigns. These notes preserve that tone while organizing it like a wiki: factions, operations, ideologies, country arcs, annual timelines, and dated event articles.

## Navigation

- [[Graph Legend]] explains the color-coded graph groups.
- [[Canon Index]] lists the major synthesized articles.
- [[Timeline 1981-1989]] links every year and dated event article.
- [[Faction Hub]] gathers state and player-country articles.
- [[Campaign Hub]] gathers wars, annexations, and regional conquest arcs.
- [[Final War Hub]] follows the collapse of NATO, final global conquest, and the U.S.-L.E.T.F. war.
- [[80s country game source note]] links the PDF and extracted transcript.

## Canon Structure

The vault is deliberately linked through hub notes. In Obsidian's graph view, event pages attach to year pages, year pages attach to the timeline, and faction pages attach to the factions that drive the scenario. This creates dense local clusters instead of one long line of disconnected notes.

## Reading Order

1. Begin with [[Initial Player Setup]] for the four starting countries and their powers.
2. Read [[Early Cold War Crisis]] for the Soviet escalation, Cuban annexation, U.S. countermeasures, and collapse of the USSR.
3. Continue with [[Lowest Egyptian Taper Fade]] and [[Morganism]] for the replacement of the USSR player with Egypt and the emergence of the L.E.T.F.
4. Follow [[U.S.-L.E.T.F. Alliance]] and [[Major Operations of the Country Game]] for the main expansion chronology.
5. Finish with [[Final NATO LETF War]], [[L.E.T.F. Final Global Conquest]], and [[Final Global War]].

## Canon Note

All articles are written as encyclopedia-style summaries of a fictional role-play transcript. The pages are not factual world history and do not endorse the ideologies, conquests, or political figures depicted in the scenario.
""",
    },
    {
        "folder": "00 Atlas",
        "title": "Graph Legend",
        "group": "atlas",
        "kind": "hub",
        "aliases": ["Color Legend", "Graph Groups"],
        "body": """
## Color Groups

The Obsidian graph is configured with color groups based on tags. Each generated note carries one primary group tag, and hub links are used to pull related notes close together.

| Color | Tag | Meaning |
| --- | --- | --- |
| <span class="cg-swatch cg-atlas"></span> Gold | #group/atlas | Indexes, source notes, navigation, and vault maps |
| <span class="cg-swatch cg-faction"></span> Blue | #group/faction | Player countries, successor states, alliances, and named political actors |
| <span class="cg-swatch cg-cold-war"></span> Pink red | #group/cold-war | Early 1981 Soviet crisis, Cuba, Canada, West Germany, and NATO emergency politics |
| <span class="cg-swatch cg-letf"></span> Violet | #group/letf-state | L.E.T.F. state formation, administration, imperial structure, and leadership |
| <span class="cg-swatch cg-campaign"></span> Orange | #group/campaign | Annexation campaigns, invasions, regional wars, and military operations |
| <span class="cg-swatch cg-ideology"></span> Green | #group/ideology | Morganism, pantheon pages, propaganda, religion, and cultural institutions |
| <span class="cg-swatch cg-technology"></span> Teal | #group/technology | SR-91 Phantom Sky, interceptors, weapons, and anachronism notes |
| <span class="cg-swatch cg-timeline"></span> Steel blue | #group/timeline | Year pages and dated event article infrastructure |
| <span class="cg-swatch cg-final"></span> Red | #group/final-war | NATO collapse, final conquest, nuclear war, and postwar aftermath |

## Why The Graph Clusters

Each article links upward to a hub and sideways to related actors. The graph should therefore form readable neighborhoods: early Cold War notes around [[Cold War Crisis Hub]], L.E.T.F. institutional notes around [[L.E.T.F. State Hub]], campaign pages around [[Campaign Hub]], and endgame pages around [[Final War Hub]].
""",
    },
    {
        "folder": "00 Atlas",
        "title": "Canon Index",
        "group": "atlas",
        "kind": "index",
        "aliases": ["Article Index", "Main Index"],
        "body": """
## Major Articles

- [[Initial Player Setup]]
- [[United States of America]]
- [[Soviet Union]]
- [[Canada]]
- [[West Germany and NATO]]
- [[Boombayah]]
- [[Lowest Egyptian Taper Fade]]
- [[Adolf Hitler in the Country Game]]
- [[King Darius Morgan]]
- [[Morganism]]
- [[Pantheon of Morganism]]
- [[Necrocracy]]
- [[Department of Music and Bluntz Beats]]
- [[Early Cold War Crisis]]
- [[U.S.-L.E.T.F. Alliance]]
- [[Middle Eastern Expansion]]
- [[Former Soviet Territorial Campaigns]]
- [[Americas Campaigns]]
- [[Asia Pacific Campaigns]]
- [[European Campaigns]]
- [[African and Polar Campaigns]]
- [[Major Operations of the Country Game]]
- [[SR-91 Phantom Sky]]
- [[Military Technology and Anachronisms]]
- [[Operation Watchful Fade 2]]
- [[Final NATO LETF War]]
- [[L.E.T.F. Final Global Conquest]]
- [[Final Global War]]

## Event Indexes

- [[Timeline 1981-1989]]
- [[1981]]
- [[1982]]
- [[1983]]
- [[1984]]
- [[1985]]
- [[1986]]
- [[1987]]
- [[1988]]
- [[1989]]
""",
    },
    {
        "folder": "01 Factions",
        "title": "Initial Player Setup",
        "group": "faction",
        "kind": "article",
        "aliases": ["Game Setup", "Country Powers"],
        "body": """
## Lead

The initial player setup defines the power balance of the Country Game in February 1981. Four players receive countries and modifiers, establishing both the geopolitical frame and the rules of escalation. The setup is explicitly Cold War-era: nuclear weapons, NATO, the Berlin Wall, and realistic equipment constraints are expected to matter.

## Assigned Countries

| Player role | Country | Starting modifier |
| --- | --- | --- |
| User | [[United States of America]] | Defense budget tripled, giving the United States accelerated research, readiness, and procurement capacity |
| Dad | [[West Germany and NATO|West Germany]] | Sole possession of technology able to mine silicon, making West Germany a strategic electronics chokepoint |
| Mom | [[Canada]] | No taxes at the start of the game, creating investment potential but raising questions about defense funding |
| Brother Landon | [[Soviet Union]] | Large nuclear arsenal, but very poor generals and a badly led military structure |

## Rules And Tone

The player asks for a simulator that responds to country moves with likely outcomes rather than choosing actions for the players. The requested style is detailed and equipment-specific: campaigns should name aircraft, ships, armored vehicles, units, seized territory, defensive alliances, and battle results. The PDF also establishes an anachronism rule. If a country tries to use a future weapon in the wrong decade, the simulation should correct the mismatch or prompt research toward an era-appropriate analogue.

## Strategic Meaning

The setup creates three immediate pressure points. First, the Soviet Union is dangerous because of its nuclear stockpile but unstable because of incompetent command. Second, West Germany becomes a high-value target because silicon mining is central to advanced electronics. Third, the United States begins with the fiscal capacity to dominate research and rapid deployment. Canada's tax-free status is initially economic rather than military, but later events force it to adopt a war tax and integrate more deeply with NORAD.

## Linked Starting Arc

The first phase of the game is covered in [[Early Cold War Crisis]], [[February 1981 - Developments]], and [[February 1981 - Key Developments]]. Those pages show the starting modifiers turning into the Berlin Wall humanitarian crossing, Canadian rearmament, Soviet escalation, and the first U.S. interceptor research programs.
""",
    },
    {
        "folder": "01 Factions",
        "title": "United States of America",
        "group": "faction",
        "kind": "article",
        "aliases": ["USA", "U.S.", "United States"],
        "body": """
## Lead

The United States of America is one of the central player states in the Country Game. Its opening modifier is a tripled defense budget, which gives it unmatched procurement capacity, early access to classified aerospace programs, and the ability to underwrite allies or partners. Across the canon, the United States moves from Cold War defender to controversial partner of the [[Lowest Egyptian Taper Fade]], then to the surviving belligerent in the [[Final Global War]].

## Early Cold War Role

In February and March 1981, the United States reacts to the [[Soviet Union]]'s nuclear threats by raising alert status, reinforcing NATO, deploying air and naval forces, and funding advanced interceptor research. Strategic Air Command, NORAD cooperation, F-15 and F-14 interceptors, Ohio-class submarines, AWACS aircraft, and early anti-missile concepts all appear in the early crisis. The U.S. also conducts sanctions and naval operations against North Korea when it supports Soviet plans.

## Research State

The tripled defense budget drives several advanced programs. The most important is [[SR-91 Phantom Sky]], a hypersonic reconnaissance aircraft later designated SR-91 "Phantom Sky" and nicknamed "Ethereal Falcon." The U.S. also develops missile defense, reconnaissance, high-speed interceptor, and prototype aircraft programs. The technology arc is one of the canon's main ways to translate the budget modifier into durable geopolitical power.

## Alliance With The L.E.T.F.

After the collapse of the USSR and the rise of the L.E.T.F., the United States enters a shocking alliance with [[Lowest Egyptian Taper Fade]]. The alliance first enables campaigns against Israel, Jordan, Cuba, Saudi Arabia, Iraq, and later Mexico and Central America. In the wiki's classification, this alliance is both a diplomatic turning point and a moral fracture: it gives the L.E.T.F. the airpower and logistics to expand while isolating the United States from traditional partners.

## Americas And Hemisphere Policy

The United States helps invade Mexico through a combined northern offensive and L.E.T.F. southern landings from Cuba. It later expands through Central America and Colombia, fortifies borders, and operates against Boombayah and its allies through covert or unidentified activity. The United States repeatedly frames territorial control as stabilization, but the resulting occupation zones generate insurgencies and international backlash.

## Final Position

In 1989, the United States leaves NATO and formalizes its alliance with the L.E.T.F., helping complete the collapse of Western resistance. After the L.E.T.F. achieves near-global domination, however, it backstabs the United States and initiates the [[Final Global War]]. The U.S. launches a full nuclear response, raises NORAD readiness, establishes air superiority where possible, and ultimately survives as the only organized superpower after the L.E.T.F. disintegrates.

## See Also

- [[U.S.-L.E.T.F. Alliance]]
- [[SR-91 Phantom Sky]]
- [[Military Technology and Anachronisms]]
- [[Final Global War]]
""",
    },
    {
        "folder": "01 Factions",
        "title": "Soviet Union",
        "group": "faction",
        "kind": "article",
        "aliases": ["USSR", "Union of Soviet Socialist Republics"],
        "body": """
## Lead

The Soviet Union is the first major antagonist of the Country Game and the initial country assigned to Landon. It begins with a plentiful nuclear stockpile but a deeply incompetent officer corps. This combination makes the USSR frightening in theory and self-destructive in practice. Its arc is short, chaotic, and decisive: public nuclear threats, failed invasions, bizarre propaganda changes, Cuban annexation, and an attempted thermonuclear self-destruction lead to the collapse of the Soviet state by mid-1981.

## Nuclear Threat

The Soviet Union opens the active scenario by publicly announcing that it plans to cause global nuclear war. The announcement triggers NATO emergency planning, U.S. DEFCON escalation, West German defensive measures, and internal Soviet panic. Because the Soviet modifier includes poor generals, the threat immediately begins to backfire. Officers split over whether to obey, nuclear security weakens, and a silo malfunction in Kazakhstan undermines Soviet credibility.

## East Germany And Cuba

The USSR attempts to invade East Germany after West Germany allows 5,000 East Germans to cross through Berlin Wall checkpoints. The attack uses Tu-22M bombers, MiG fighters, T-72 mechanized formations, and a Baltic landing toward Rostock, but NATO airpower and poor Soviet coordination ruin the operation. The Soviet campaign in Cuba is more successful at first: Havana and other major cities are seized, the island is annexed, and missile sites are prepared. This victory creates the Cuban Crisis of 1981 and provokes U.S. blockade planning.

## Propaganda And Instability

The Soviet government repeatedly changes its flag, first with absurd animal imagery and later with a low taper fade symbol. It also pursues a global speaker project intended to broadcast slogans worldwide. These actions make the USSR look erratic to its own citizens, its allies, and its enemies. North Korea offers limited aid, but Soviet logistical problems and U.S. sanctions make the partnership weak.

## Collapse

The decisive event is the April 1981 self-destructive nuclear plan. Soviet leaders attempt to launch their arsenal against their own territory and Canada. U.S. and NATO forces respond through Operation Sky Shield, destroying launch sites, intercepting bombers, and exploiting dissent among Soviet officers. The Soviet government implodes, Brezhnev is removed, and the USSR becomes a derelict patchwork of rogue generals, separatist territories, failed states, and unclaimed regions.

## Legacy

The Soviet collapse creates the territorial vacuum that later enables L.E.T.F. campaigns into Ukraine, the Caucasus, Siberia, Central Asia, Kazakhstan, and the former Russian federal districts. In this sense, the USSR does not merely fail; its failure becomes the map on which the L.E.T.F. builds its empire.
""",
    },
    {
        "folder": "01 Factions",
        "title": "Canada",
        "group": "faction",
        "kind": "article",
        "aliases": ["Tax-Free Canada"],
        "body": """
## Lead

Canada begins the Country Game with a tax-free national modifier. At first this gives it economic appeal and makes it a refuge for people fleeing Soviet threats. The Cold War crisis rapidly changes the country's role: Canada adopts a temporary war tax, reinforces NORAD, purchases advanced equipment, defends its symbolic maple forests, and eventually becomes a major target of the L.E.T.F. in 1989.

## Tax-Free Modifier

The tax-free status is economically powerful but strategically awkward. Without taxes, Canada can attract investment and migration, but it lacks an obvious mechanism to fund large-scale defense. The Soviet nuclear announcement forces a compromise. Prime Minister Pierre Trudeau introduces a War Preparedness Tax, preserving the idea of Canada as an unusually low-tax state while acknowledging that the crisis requires revenue.

## Defense Program

Canadian defense investments focus on radar systems, NORAD integration, F-15 purchases, and forest defense units. The maple tree subplot gives Canada a symbolic role in the early canon: Soviet rhetoric against maple trees becomes a strange but persistent expression of hostility. Canada responds with ranger deployments, air defense cooperation with the United States, and public mobilization around national forests.

## Diplomatic Role

Canada generally condemns Soviet and L.E.T.F. aggression while avoiding reckless unilateral escalation. It relies on NATO alignment and U.S. support for strategic defense. During Operation Watchful Fade 2, Canada is described as passive but diplomatically aligned with NATO, indicating caution rather than surrender.

## 1989 Invasion

The L.E.T.F. launches Operation Maple Fade in 1989, using positions in Cuba, Hawaii, and Chukotka to invade Canada. The campaign aims to annex Canada as the Northern Province of the Fade and seize resources such as oil, timber, and natural gas. The invasion closes the loop on Canada's early status: the country that began as a tax haven and symbolic Soviet target becomes one of the last major North American fronts of the L.E.T.F. expansion.

## See Also

- [[February 1981 - Key Developments]]
- [[March 1981 - Global Chaos Unfolds]]
- [[1989 - L.E.T.F. Launches Full-Scale Invasion of Canada|1989: L.E.T.F. Launches Full-Scale Invasion of Canada (Operation Maple Fade)]]
""",
    },
    {
        "folder": "01 Factions",
        "title": "West Germany and NATO",
        "group": "faction",
        "kind": "article",
        "aliases": ["West Germany", "NATO"],
        "body": """
## Lead

West Germany is a starting player country and one of the most important NATO actors in the Country Game. Its unique modifier is exclusive silicon-mining technology, making it essential to electronics, microchips, and high-technology defense production. NATO functions first as the anti-Soviet defense structure, then as the last organized barrier against the L.E.T.F.

## Silicon Monopoly

West Germany's silicon-mining monopoly gives it strategic leverage beyond its normal Cold War position. It becomes a technology chokepoint that both reassures NATO and attracts Soviet attention. The PDF treats this modifier as a reason for emergency protection: if West Germany falls, advanced electronics and semiconductor supply could be compromised.

## Humanitarian Crossing

The first major West German move is the decision to allow 5,000 East Germans to cross into West Germany through Berlin Wall checkpoints. The event is framed as humanitarian and propagandistic, showing Western freedom while humiliating the Soviet-aligned East German system. It sparks Stasi surveillance, Soviet anger, East German unrest, and increased NATO tension.

## Defense Against The USSR

When the Soviet Union attempts to invade East Germany, West Germany and NATO help repel the attack. F-4 Phantoms, coastal defenses, NATO naval support, and American airpower stop Soviet bombers, mechanized formations, and the Rostock landing. The failed invasion strengthens NATO's position and contributes to Soviet isolation.

## NATO Against The L.E.T.F.

After the Soviet collapse, NATO's role shifts. The L.E.T.F. expands through the Middle East, Africa, Asia, and Europe, repeatedly drawing condemnation and resistance. NATO survives as a shrinking coalition until 1989. The United States eventually leaves NATO and allies with the L.E.T.F., leaving West Germany and Denmark as final strongholds. In [[Final NATO LETF War]], nuclear strikes and Operation Nordic Breakpoint end organized NATO resistance.

## Historical Note Inside The Canon

The PDF includes a NATO membership list as of 1989. It names the 1949 founding members, Greece and Turkey in 1952, West Germany in 1955, and Spain in 1982. The generated notes keep this as a reference page while distinguishing it from the fictional outcome, where NATO is destroyed before the final U.S.-L.E.T.F. war.
""",
    },
    {
        "folder": "01 Factions",
        "title": "Boombayah",
        "group": "faction",
        "kind": "article",
        "aliases": ["Brazil", "Madison's Brazil"],
        "body": """
## Lead

Boombayah is the renamed form of Brazil under Madison's leadership. It begins as a player country with the modifier "equal rights for all," positioning it as a moral counterweight to the U.S.-L.E.T.F. alliance. Its arc includes diplomatic advocacy, support for Mexico and India, resistance to L.E.T.F. expansion, internal coups, anarchist insurgency, and eventual annexation.

## Equal Rights Modifier

Brazil's starting modifier gives it a distinctive ideological identity. Madison's government promotes equality, asylum, diplomacy, and opposition to illegal annexations. When the United States and the L.E.T.F. invade Mexico, Brazil condemns the campaign, pushes sanctions at the United Nations, and offers aid to displaced civilians.

## Renaming

In 1987, Brazil officially renames itself Boombayah. The rebrand is described as energetic, modern, and unconventional. It alters national symbols and signals a desire to lead South America through a bold identity. Other states are puzzled, supportive, or mocking depending on their relationship to Madison's government.

## Coup And Jaime Cuerbo

Unidentified forces covertly fund and arm anarchist movements inside Boombayah. Jaime Cuerbo becomes the central insurgent figure, receiving aircraft, naval vessels, and land vehicles. Madison responds with martial law while trying to continue support for India against the L.E.T.F. This dual burden becomes one of Boombayah's defining problems: external moral leadership and internal fragmentation collide.

## Resistance And Annexation

Boombayah funds Indian forces during Operation Mystic Fade, helping slow the L.E.T.F. invasion. It later faces escalating U.S.-L.E.T.F. pressure, South American campaigns, and internal chaos. By 1987 the L.E.T.F. imposes martial law in South America, conducts espionage, and finally annexes Boombayah. Remnants of Madison's government and anti-L.E.T.F. forces continue to appear as part of the global backlash.

## See Also

- [[Americas Campaigns]]
- [[1987 - Boombayah's Renaming and the Classified Coup]]
- [[1987 - The L.E.T.F. Invades India, Boombayah Funds Indian Forces, and Jaime Cuerbo Expands Anarchist Campaign]]
""",
    },
    {
        "folder": "03 LETF State",
        "title": "Lowest Egyptian Taper Fade",
        "group": "letf-state",
        "kind": "article",
        "aliases": ["L.E.T.F.", "LETF", "Lowest Egyptian Taper Fade"],
        "body": """
## Lead

The Lowest Egyptian Taper Fade, abbreviated L.E.T.F., is the dominant fictional empire of the Country Game. It emerges after the Soviet player country collapses and is replaced by Egypt, now ruled in-canon by Adolf Hitler and later transformed into a surreal militarized theocracy. From 1981 to 1989, the L.E.T.F. expands from Egypt into the Middle East, Africa, the former Soviet territories, Asia, Europe, Oceania, polar regions, and parts of the Americas.

## Formation

The L.E.T.F. begins as Egypt under a new authoritarian leadership structure. Early projects include a reproductive campaign, attempts to ship pyramids to the United States as gifts, obsidian and silver statues, and a renamed state identity centered on the "low taper fade." The Sphinx heads are replaced in the scenario, and state symbolism becomes a mix of Egyptian imagery, barbershop aesthetics, Roman imperial imitation, and Morganist religion.

## Government

The state develops a strange hierarchy. Adolf Hitler acts as living ruler and later vice-ruler, while King Darius Morgan is elevated as a religious leader. Magnus Maximus eventually becomes an eternal ruler through the doctrine of [[Necrocracy]], meaning the empire claims partial rule by the dead. Ministries and departments become ideological organs: the Department of Religion spreads Morganism, while the Department of Music weaponizes loudspeakers and "Bluntz Beats."

## Military System

The L.E.T.F. combines modern equipment, mass conscription, religious fervor, and symbolic warfare. Its forces repeatedly use T-72 tanks, BMP-1 infantry fighting vehicles, MiG-21 fighters, Su-17 bombers, later Su-24s, propaganda aircraft, ceremonial loudspeakers, and immense infantry formations. The empire's expansion succeeds largely because the United States supplies airpower, logistics, or direct military support during much of the canon.

## Expansion Pattern

The empire's campaigns follow a recognizable pattern: identify a symbolic or strategic target, announce a province name, deploy overwhelming ground forces, add U.S. air or naval support when available, replace local institutions with Morganist shrines, and then struggle with insurgency. This pattern appears in Israel, Jordan, Saudi Arabia, Iraq, Turkey, the Caucasus, Ukraine, Central Asia, China, India, Australia, Italy, France, the United Kingdom, Africa, and the final polar campaigns.

## Weaknesses

The L.E.T.F. is repeatedly overextended. Every successful annexation increases the number of insurgencies, supply lines, occupied capitals, and symbolic obligations it must defend. The empire also depends on contradictory foundations: religious zeal, absurd cultural propaganda, necrocratic legitimacy, U.S. support, and brute force. These contradictions are survivable while the United States is an ally, but fatal when the L.E.T.F. turns against it in [[Final Global War]].

## End

After achieving near-global domination with the United States as its only peer, the L.E.T.F. betrays the U.S. and triggers total nuclear war. Its leaders are killed or captured, its infrastructure collapses, and its territories fragment. The empire's rise is therefore the main middle arc of the Country Game, while its destruction defines the ending.
""",
    },
    {
        "folder": "03 LETF State",
        "title": "Adolf Hitler in the Country Game",
        "group": "letf-state",
        "kind": "article",
        "aliases": ["Hitler", "LETF Hitler"],
        "body": """
## Lead

Adolf Hitler appears in the Country Game as the fictional leader of Egypt after the Soviet player country collapses. The generated wiki treats this as in-universe alternate-history content only. His role is not historical biography; it is a fictional state-leadership element inside the L.E.T.F. arc.

## Entry Into The Canon

After the USSR collapses, the player previously controlling the Soviet Union becomes Egypt. The new Egypt is described as led by Adolf Hitler and possessing a powerful military "like the Roman Empire, but with guns." This transition begins the second major phase of the PDF: the Soviet nuclear crisis gives way to the bizarre imperial expansion of Egypt and then the L.E.T.F.

## Policies

The early Hitler-led Egypt initiates a reproductive campaign, monumental engineering projects, obsidian and silver statues, and ceremonial state-building. The country later renames itself the Lowest Egyptian Taper Fade, with Hitler positioned as the central political actor who authorizes expansion and religious restructuring.

## Relationship To Morganism

As [[Morganism]] grows, Hitler's role changes. King Darius Morgan becomes the religious head, Magnus Maximus becomes the eternal ruler in the necrocratic system, and Hitler becomes vice-ruler or acting ruler. The state therefore shifts from personal dictatorship toward a theatrical sacred monarchy and necrocracy, even while Hitler remains a major political figure.

## Life-Extension Project

The 1984 life-extension arc introduces the Chrono-Fade Life Prolonger, a device that allegedly extends Hitler's life to June 12, 2011. In the canon, this blends pseudoscience, ritual, and state propaganda. It also shows how the L.E.T.F. uses technology and religion together to stabilize leadership myths.

## Final War

During the final U.S.-L.E.T.F. war, the United States targets L.E.T.F. leadership residences and symbolic sites. Hitler survives initial strikes in fortified bunkers but is ultimately captured or killed by U.S. special forces, according to the final outcome. His fictional arc ends with the collapse of the empire he helped initiate.
""",
    },
    {
        "folder": "03 LETF State",
        "title": "King Darius Morgan",
        "group": "letf-state",
        "kind": "article",
        "aliases": ["Darius Morgan", "Divine Bald King"],
        "body": """
## Lead

King Darius Morgan is the central sacred figure of the L.E.T.F. state religion. Crowned as head of the Department of Religion in April 1981, he becomes the living symbol of Morganism, the spiritual justification for conquest, and one of the leaders the L.E.T.F. later tries to protect during the final war.

## Coronation

The coronation occurs at the Great Sphinx of Giza, which the scenario has transformed with the likeness of Darius Morgan. A gold crown decorated with low taper fade imagery is placed in a ceremony attended by national and military leaders. Hitler proclaims him the "Divine Bald King," establishing the direct link between state power and religious office.

## Religious Role

In Morganism, Darius Morgan embodies perfection, wisdom, and the power of the Fade. Soldiers pray to him before battles, shrines are erected in annexed capitals, and victories are described as divine confirmations. He remains alive but is also classified as a "living goddess" in the expanded pantheon, reflecting the canon's deliberately contradictory religious language.

## Political Importance

Darius Morgan's importance is not only symbolic. The Department of Religion uses his image to integrate conquered territories, replace local institutions, and ritualize military expansion. The L.E.T.F. frames annexations as both strategic victories and sacred expansions of Morganist space.

## Final War

When the L.E.T.F. declares war on the United States, half its army is assigned to protect leaders such as Darius Morgan, Adolf Hitler, Grog Morgan, Mr. Clean, Vex Bolts, and the grave of Magnus Maximus. The U.S. nuclear and special operations campaign targets those leadership sites. Darius Morgan survives initial strikes in bunkers but is ultimately captured or killed in the collapse.
""",
    },
    {
        "folder": "05 Ideology and Culture",
        "title": "Morganism",
        "group": "ideology",
        "kind": "article",
        "aliases": ["Morganist Religion", "Religion of the Fade"],
        "body": """
## Lead

Morganism is the official state religion of the L.E.T.F. and one of the main organizing systems of the Country Game. It turns conquest, leadership worship, music, absurd imagery, and battlefield ritual into a single imperial ideology. Morganism begins with [[King Darius Morgan]] and expands into a pantheon that includes Grog Morgan, Dave Bluntz, Vex Bolt, Skibbity Toilet, Mr. Clean, Magnus Maximus, and other figures.

## Origins

Morganism is formalized when the L.E.T.F. crowns King Darius Morgan as head of the Department of Religion. The religion fuses state worship, military ritual, and visual symbolism around the low taper fade. It spreads through ceremonies at altered Egyptian monuments, shrines in annexed territories, and battlefield prayers before major campaigns.

## Beliefs

The doctrine is not systematic in a normal theological sense. Its central ideas are loyalty to the Fade, reverence for Darius Morgan, rejection of Vex Bolt's negative qualities, and sanctification of L.E.T.F. expansion. Soldiers are encouraged to interpret victories as divine approval and defeats as failures of faith, discipline, or ritual purity.

## Rituals

Common practices include battlefield prayers, loudspeaker broadcasts, music festivals after annexations, symbolic banishments of Vex Bolt, statues in obsidian or silver, and ceremonial alteration of landmarks. Annexed cities often receive Morganist shrines, while older religious or civic institutions are repurposed into imperial cult sites.

## Political Function

Morganism gives the L.E.T.F. a method for absorbing conquered territory. Instead of treating annexations only as military occupation, the empire renames provinces, installs shrines, and frames local integration as sacred conversion. This helps explain why symbolic targets such as Mecca, Medina, Vatican City, Rome, Beijing, and polar regions become important beyond their military value.

## Contradictions

The religion contains deliberate contradictions: living goddesses who are male, dead figures holding offices, absurd deities with serious military roles, and necrocratic claims that the dead rule through ritual interpretation. These contradictions are not errors in the wiki; they are part of the PDF's surreal canon.
""",
    },
    {
        "folder": "05 Ideology and Culture",
        "title": "Pantheon of Morganism",
        "group": "ideology",
        "kind": "article",
        "aliases": ["Morganist Pantheon"],
        "body": """
## Lead

The Pantheon of Morganism is the expanding group of sacred figures worshipped by the L.E.T.F. It begins with King Darius Morgan and grows as the empire conquers territory and invents new religious offices. The pantheon is both theology and state propaganda: each figure represents a virtue, vice, institution, or battlefield function useful to the L.E.T.F.

## Major Figures

| Figure | Role in canon |
| --- | --- |
| [[King Darius Morgan]] | Living sacred leader, divine center of Morganism, head of religious authority |
| Grog Morgan | Goddess of strength and resilience |
| Dave Bluntz | Dead goddess of leisure and music; head of the Department of Music |
| Vex Bolt | Demonic goddess of hatred, disgust, envy, and other negative forces |
| Skibbity Toilet | God of war and fools, associated with chaos and battlefield absurdity |
| Magnus Maximus | Eternal ruler in the necrocratic system |
| Mr. Clean | Goddess of happiness and lightning, associated with purification and power |

## Dave Bluntz And Music

Dave Bluntz is a key cultural figure because he connects worship to military practice. His department installs loudspeakers on tanks, bases, and battlefield installations. "Bluntz Beats" are supposed to inspire troops and confuse enemies, but they also become a source of international ridicule and a marker of L.E.T.F. absurdism.

## Vex Bolt

Vex Bolt functions as a negative theological pole. By declaring hatred, disgust, envy, and destruction to be associated with a demonic figure, Morganist priests create rituals of banishment and self-purification. Politically, this allows the state to label dissent or disloyalty as spiritual contamination.

## Skibbity Toilet And Mr. Clean

Skibbity Toilet represents chaotic war energy and foolishness, while Mr. Clean represents happiness, lightning, and purification. Their inclusion shows the pantheon's flexible, meme-like structure. The L.E.T.F. can absorb almost any symbol and turn it into a state religious function.

## Necrocratic Expansion

When [[Necrocracy]] is declared, the pantheon gains a governmental role. Dead figures are no longer merely honored; they can be treated as rulers, officeholders, or sources of command interpreted by priests. This gives the L.E.T.F. a sacred justification for decisions that no living electorate or cabinet can challenge.
""",
    },
    {
        "folder": "05 Ideology and Culture",
        "title": "Necrocracy",
        "group": "ideology",
        "kind": "article",
        "aliases": ["Partial Necrocracy", "LETF Necrocracy"],
        "body": """
## Lead

Necrocracy is the L.E.T.F. doctrine of partial rule by the dead. Declared in 1984, it transforms the empire from an authoritarian theocracy into a stranger political-religious system in which deceased figures can hold sovereign authority through rituals and priestly interpretation.

## Declaration

The L.E.T.F. declares itself a partial necrocracy after integrating Magnus Maximus as supreme ruler. Magnus Maximus is dead, but the state proclaims him the Eternal Sovereign. Adolf Hitler remains the living vice-ruler, handling day-to-day administration while claiming to act beneath the authority of a dead ruler.

## Governmental Logic

Necrocracy solves several political problems for the L.E.T.F. First, it creates a ruler who cannot be voted out, assassinated in a normal way, or criticized as merely human. Second, it gives priests enormous interpretive power, because orders from the dead must be translated through ritual. Third, it helps unify conquered territories under a mythology that is bigger than any single living leader.

## Institutions

Necrocratic rule depends on shrines, graves, ceremonial councils, and religious administrators. The grave of Magnus Maximus becomes a political site. The Department of Religion gains power because it can interpret dead authority. The life-extension project for Hitler also fits this framework: the L.E.T.F. blurs life, death, machinery, and religious legitimacy.

## Consequences

The doctrine strengthens internal propaganda but worsens the empire's irrationality. Military plans become easier to sacralize, dissent becomes easier to criminalize, and practical logistics can be ignored in favor of divine or necrocratic claims. By the end of the canon, the same sacred leadership sites become targets during the U.S. nuclear response.
""",
    },
    {
        "folder": "05 Ideology and Culture",
        "title": "Department of Music and Bluntz Beats",
        "group": "ideology",
        "kind": "article",
        "aliases": ["Bluntz Beats", "Department of Music"],
        "body": """
## Lead

The Department of Music is a Morganist cultural institution headed by Dave Bluntz, a deceased pantheon figure. Its signature battlefield practice is the use of huge loudspeaker systems to blast "Bluntz Beats" during L.E.T.F. operations. The department is part propaganda office, part morale system, and part psychological warfare unit.

## Battlefield Use

L.E.T.F. tanks, bases, and artillery positions are fitted with loudspeakers. Before and during battles, soldiers hear music associated with recreational drug imagery, Morganist triumph, and the pantheon. The intended effects are morale, intimidation, confusion, and religious immersion.

## Military Value

The military value is inconsistent. Some L.E.T.F. soldiers claim the music energizes them, and the spectacle can confuse defenders. At the same time, loudspeakers can reveal positions, attract ridicule, and deepen the impression that L.E.T.F. command culture is unstable. The wiki treats Bluntz Beats as a real in-canon practice but not as a consistently rational doctrine.

## Cultural Role

After annexations, Dave Bluntz-themed festivals appear in cities such as Basra and Baghdad. Music becomes a tool for turning conquered space into Morganist space. The Department of Music therefore works alongside the Department of Religion: one supplies sound and spectacle, the other supplies doctrine.

## See Also

- [[Pantheon of Morganism]]
- [[Morganism]]
- [[Lowest Egyptian Taper Fade]]
""",
    },
    {
        "folder": "02 Cold War Crisis",
        "title": "Early Cold War Crisis",
        "group": "cold-war",
        "kind": "article",
        "aliases": ["1981 Soviet Crisis", "Cuban Crisis of 1981"],
        "body": """
## Lead

The Early Cold War Crisis is the opening conflict arc of the Country Game. It runs from February to April 1981 and centers on the Soviet Union's nuclear threats, the Berlin Wall humanitarian crossing, the failed Soviet invasion of East Germany, the annexation of Cuba, North Korean aid efforts, U.S. counterintelligence, and the eventual collapse of the USSR.

## Causes

The crisis begins when the Soviet Union publicly announces plans to cause a global nuclear war. Because the USSR has abundant nuclear weapons but incompetent generals, the announcement produces fear without reliable control. NATO responds defensively, the United States shifts alert posture, Canada prepares its defenses, and West Germany becomes a frontline state.

## Berlin And East Germany

West Germany allows 5,000 East Germans to cross through Berlin Wall checkpoints. The move is humanitarian but also propagandistic, and it humiliates the Soviet bloc. The USSR responds by attempting to invade East Germany. The operation fails because of poor coordination, NATO intelligence, West German defenses, and American air support.

## Cuba

The USSR then invades Cuba under the cover of a diplomatic visit. It captures Havana, occupies major cities, and annexes the island. This triggers the Cuban Crisis of 1981. The United States prepares blockade and strike options, Canada reinforces NORAD cooperation, and West Germany uses the event as anti-Soviet propaganda.

## Intelligence And Sabotage

The crisis includes an assassination plot against East Germany's leader, a Soviet global speaker project, U.S. Operation Silent Sky, and broader counterintelligence operations. These episodes show the conflict moving beyond conventional war into sabotage, propaganda, and technological absurdity.

## Collapse Of The USSR

The arc ends with the Soviet self-destructive nuclear plan. U.S. and NATO forces execute Operation Sky Shield, destroying silos, intercepting bombers, and exploiting mutiny inside Soviet command. The USSR collapses into a derelict patchwork of rogue generals, failed regions, separatist movements, and unclaimed territory. Cuba regains independence under chaotic circumstances.

## Importance

The early crisis removes the Soviet Union from the board and creates the vacuum that the L.E.T.F. later exploits. It also establishes the United States as the most capable military-technology power in the setting.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "U.S.-L.E.T.F. Alliance",
        "group": "campaign",
        "kind": "article",
        "aliases": ["US LETF Alliance", "United States LETF Alliance"],
        "body": """
## Lead

The U.S.-L.E.T.F. Alliance is the central diplomatic rupture of the Country Game. It begins in 1981 when the United States forms a strategic partnership with the Lowest Egyptian Taper Fade. The alliance transforms the L.E.T.F. from a regional empire into a global threat by giving it access to American airpower, naval support, intelligence, logistics, and diplomatic shielding.

## Formation

The alliance first appears during the joint campaign against Israel. The United States sees tactical value in using L.E.T.F. proximity to reshape the Middle East, while the L.E.T.F. needs American strength to overcome military losses. The partnership immediately shocks the world because it contradicts normal alliance expectations and places the United States beside a state openly pursuing annexation.

## Military Pattern

The alliance usually follows a division of labor. L.E.T.F. ground forces provide numbers, religious fervor, occupation troops, and symbolic annexation. The United States provides air superiority, naval blockade, reconnaissance, special operations, and veto protection in international institutions. This pattern appears in Israel, Jordan, Cuba, Saudi Arabia, Iraq, Mexico, Central America, and several later campaigns.

## Political Cost

The alliance isolates both partners. The United Nations condemns repeated annexations, traditional U.S. allies protest, and domestic American opposition grows. Brazil/Boombayah emerges as a moral counterweight, while NATO becomes increasingly strained. The alliance succeeds militarily but corrodes the United States' legitimacy.

## Strategic Benefit

For the L.E.T.F., the alliance is decisive. American support compensates for overextended logistics and makes otherwise impossible campaigns feasible. For the United States, the alliance expands influence across the Americas and Middle East, but it also creates a future rival whose empire eventually becomes too large to control.

## End

The alliance formally reaches its height when the United States leaves NATO in 1989 and aligns openly with the L.E.T.F. It ends when the L.E.T.F. backstabs the United States after near-total global domination. The resulting [[Final Global War]] destroys the L.E.T.F. and leaves the United States as the only organized superpower.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Middle Eastern Expansion",
        "group": "campaign",
        "kind": "article",
        "aliases": ["LETF Middle East Campaigns", "Middle East Arc"],
        "body": """
## Lead

The Middle Eastern Expansion is the first major imperial campaign arc of the L.E.T.F. It begins with attacks on Israel and Sudan in 1981 and grows into the annexation of Jordan, Saudi Arabia, Iraq, Syria, Turkey, Yemen, Oman, Kuwait, and eventually the remaining Middle East. The arc combines resource motives, religious symbolism, and U.S.-enabled military operations.

## Israel And Sudan

The first L.E.T.F. invasion targets Israel and Sudan. Israel initially resists successfully, but after the U.S.-L.E.T.F. alliance forms, the joint campaign overwhelms Israel. Israel is annexed as the Sacred Southern Province, creating intense global condemnation and resistance movements. Sudan is partially annexed earlier, with northern regions brought under L.E.T.F. control.

## Jordan And Saudi Arabia

Jordan is annexed in July 1981, linking Egypt, Israel, and the wider Middle East. Saudi Arabia becomes the next critical target because of oil, Mecca, and Medina. The L.E.T.F. exhausts its military to capture Riyadh, the holy cities, and oil fields, creating a major economic boost but also severe insurgencies and outrage across the Muslim world.

## Iraq, Syria, And Turkey

Iraq is annexed through Operation Euphrates Fade, with Basra and Baghdad falling under joint U.S.-L.E.T.F. pressure. Syria and Turkey follow in 1982 through Operation Crescent Fade. The L.E.T.F. gains Damascus, Ankara, Istanbul, and access to trade routes into Europe, but resistance grows in cities and border regions.

## Arabian Peninsula

North Yemen, South Yemen, and Oman are targeted for control over the Bab-el-Mandeb Strait, the Gulf of Aden, and Arabian Sea access. The campaigns further integrate the Arabian Peninsula into Morganist territory while worsening logistical strain.

## Final Middle East Sweep

In 1989, Operation Desert Fade targets Iran, Bahrain, Qatar, the United Arab Emirates, and Lebanon. This is described as a final effort to dominate remaining Middle Eastern energy resources and complete Morganist control of the region.

## Consequences

The Middle Eastern arc gives the L.E.T.F. oil, religious symbolism, strategic depth, and a route into Europe and Asia. It also creates some of the empire's deepest insurgencies, because the annexations repeatedly attack major cultural, religious, and political centers.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Former Soviet Territorial Campaigns",
        "group": "campaign",
        "kind": "article",
        "aliases": ["Former USSR Campaigns", "Russian Militia Campaigns"],
        "body": """
## Lead

The Former Soviet Territorial Campaigns are the L.E.T.F. operations into the vacuum left by the Soviet collapse. After the USSR becomes derelict, its territory fragments into rogue militias, failed regions, separatist governments, and unclaimed strategic zones. The L.E.T.F. uses this fragmentation to annex Ukraine, the Caucasus, former Russian federal districts, Siberia, Central Asia, Kazakhstan, and the Far East.

## Ukraine And Caucasus

Ukraine is targeted in 1983 for its agricultural value and geopolitical position. The Caucasus campaigns target Armenia, Azerbaijan, Georgia, and later Southern and North Caucasian militias. The L.E.T.F. seeks oil, gas, mountain defensive positions, trade routes, and religious expansion.

## Central And Northwestern Militias

The 1983 multi-front expansion targets Central and Northwestern militias, including Moscow and St. Petersburg. These campaigns are important because they allow the L.E.T.F. to occupy symbolic centers of former Soviet power and claim industrial infrastructure.

## Siberia, Far East, And Kazakhstan

The 1984 and 1985 campaigns push into Siberia, the Far Eastern District, and Kazakhstan. Resource extraction is central: oil, gas, minerals, and strategic depth. These areas also support later expansion toward Mongolia and China.

## Central Asia

Central Asia becomes a staging zone for campaigns into Mongolia, China, and South Asia. The L.E.T.F. annexes or pressures Kyrgyzstan, Tajikistan, Uzbekistan, Turkmenistan, and surrounding territories. Control of these routes helps support the later full-scale invasion of China.

## Strategic Result

By absorbing the former Soviet space, the L.E.T.F. gains resources, manpower, continental depth, and access to Europe and Asia. It also inherits severe problems: scattered insurgencies, long supply lines, nuclear remnants, damaged infrastructure, and territories with weak loyalty to the imperial center.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Americas Campaigns",
        "group": "campaign",
        "kind": "article",
        "aliases": ["Western Hemisphere Campaigns", "LETF Americas Arc"],
        "body": """
## Lead

The Americas Campaigns cover the L.E.T.F. and U.S. operations in Cuba, Newport County, Mexico, Central America, Colombia, Brazil/Boombayah, the Caribbean, Canada, and South America. The arc is unusual because the United States is both a participant in expansion and, eventually, the L.E.T.F.'s final enemy.

## Cuba And Newport County

Cuba is first annexed by the Soviet Union, regains independence after the Soviet collapse, and is later annexed by the L.E.T.F. with U.S. assistance. It becomes a staging ground for operations in the Caribbean and Mexico. Newport County, Rhode Island is placed under L.E.T.F. control as a spiritual protectorate, heavily monitored by U.S. military and intelligence assets.

## Mexico And Central America

The U.S.-L.E.T.F. invasion of Mexico combines northern U.S. advances with L.E.T.F. landings from Cuba. The campaign includes a propaganda bribery effort using free water. Central America is later brought under U.S. control, giving the alliance a land bridge and additional staging zones.

## Colombia And South America

The United States pushes into Colombia while the L.E.T.F. campaigns in Chile, Bolivia, and other South American territories. Brazil, later [[Boombayah]], resists diplomatically and supports anti-L.E.T.F. forces, but covert destabilization and military campaigns weaken it.

## Boombayah

Boombayah is the main South American counterweight. It funds Indian forces, opposes aggression, and attempts to lead an equality-centered international bloc. It is destabilized by unidentified forces, Jaime Cuerbo's anarchist campaign, martial law, and eventual L.E.T.F. annexation.

## 1989 Endgame

In 1989, Operation Maple Fade targets Canada, Operation Island Fade targets the Bahamas, Dominican Republic, Haiti, and Trinidad and Tobago, and Operation Andean Fade targets Venezuela, Guyana, Suriname, French Guiana, Ecuador, Peru, Paraguay, and Uruguay. By the end of the alliance phase, the Americas are divided between U.S. control and L.E.T.F. occupied territories.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Asia Pacific Campaigns",
        "group": "campaign",
        "kind": "article",
        "aliases": ["Asian Campaigns", "Pacific Campaigns"],
        "body": """
## Lead

The Asia Pacific Campaigns trace the L.E.T.F.'s eastward expansion through Mongolia, China, Japan, India, Australia, Korea, Southeast Asia, Pacific islands, and remaining Asian states. The arc is characterized by enormous troop deployments, naval blockades, propaganda aircraft, and repeated attempts to replace local religions with Morganism.

## Mongolia And China

Mongolia is annexed through Operation Eternal Steppe and becomes the Great Steppe Province of the Fade. It provides a staging ground for China. The invasion of China uses northern forces from Mongolia, western forces from Central Asia, and naval pressure against coastal cities. China eventually falls after a massive campaign, giving the L.E.T.F. industrial and demographic power.

## Japan And Hawaii

The 1985 joint operations include the transfer of Hawaii and the invasion of Japan. Japan becomes a major regional flashpoint because of U.S. Pacific interests, L.E.T.F. ambitions, and its role as a future source of anti-L.E.T.F. resistance.

## India

Operation Mystic Fade targets India with millions of troops, naval blockades, and religious conversion goals. Northern India falls, but resistance in southern and central regions is strengthened by Boombayah funding, equipment, and advisors. India becomes an example of how the L.E.T.F. can win territory yet still face durable resistance.

## Australia And Korea

Australia is invaded in 1987, creating prolonged resistance. Switzerland and South Korea later appear in global backlash reporting, with South Korea invaded alongside North Korea. These campaigns widen the conflict into a global anti-L.E.T.F. network.

## Final Regional Sweep

In 1988, Operation Eastern Sovereignty and Operation Final Horizon target remaining Asian and Pacific states, including Afghanistan, the Maldives, Timor-Leste, the Philippines, Macau, Hong Kong, and smaller Pacific nations. The goal is total regional completion rather than limited strategic gain.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "European Campaigns",
        "group": "campaign",
        "kind": "article",
        "aliases": ["LETF European Campaigns", "European Fade Campaigns"],
        "body": """
## Lead

The European Campaigns mark the L.E.T.F.'s confrontation with NATO and the remaining independent states of Europe. Beginning with Turkey and the Caucasus as gateways, the L.E.T.F. eventually invades Italy, San Marino, Vatican City, France, Spain, Portugal, the United Kingdom, Finland, Poland, Kaliningrad, East Germany, Greece, Malta, the Balkans, Western Europe, Northern Europe, Denmark, and West Germany.

## Southern Europe

Operation Roman Fade targets Italy, San Marino, and Vatican City. The capture of Vatican City has enormous symbolic consequences, turning global religious backlash against the L.E.T.F. Operation Iberian Fade later targets Spain and Portugal, while Operation Aegean Fade targets Cyprus, Greece, and Malta.

## Western And Northern Europe

Operation Gallic Fade targets France, Operation Albion Fade targets the United Kingdom, and Operation Northern Dominion targets Belgium, the Netherlands, Luxembourg, Andorra, Ireland, Norway, and Sweden. These campaigns are designed to crush NATO's European depth and seize industrial and naval infrastructure.

## Eastern Europe

Operation Eastern Fade targets Poland and Kaliningrad, while Operation Iron Fade targets East Germany without initially invading West Germany. The L.E.T.F. uses these operations to eliminate former Soviet remnants, pressure NATO, and rebuild divisions reminiscent of Cold War geography.

## Balkans

Operation Balkan Fade targets Yugoslavia, Romania, Hungary, Bulgaria, and Albania. This campaign extends L.E.T.F. control over southeastern Europe and access to the Black Sea.

## NATO Collapse

The European arc culminates in [[Final NATO LETF War]]. West Germany and Denmark launch nuclear strikes against major L.E.T.F. capitals, including Cairo, Moscow, and Washington D.C. The L.E.T.F. responds with Operation Nordic Breakpoint, annexing Denmark and West Germany and ending organized NATO resistance.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "African and Polar Campaigns",
        "group": "campaign",
        "kind": "article",
        "aliases": ["African Campaigns", "Polar Fade"],
        "body": """
## Lead

The African and Polar Campaigns cover the L.E.T.F.'s expansion across North Africa, Central Africa, Southern Africa, the Arctic, the North Pole, Antarctica, and the final remaining African states. These campaigns combine resource extraction, symbolic domination, and the desire to claim the last unabsorbed territories on Earth.

## North Africa

The L.E.T.F. begins in Egypt and then expands through Libya, Chad, Niger, Cameroon, Nigeria, Morocco, Algeria, and Tunisia. Operation Atlas Fade targets Morocco, while Operation Maghreb Fade targets Algeria and Tunisia. These campaigns focus on oil, gas, minerals, Mediterranean access, and suppression of resistance.

## Central And Southern Africa

Operation Equatorial Fade targets Congo, Zaire, Angola, and Namibia. Operation Southern Fade targets South Africa for gold, diamonds, platinum, and maritime positioning. The L.E.T.F. treats Africa as both a resource base and a symbolic core of the empire.

## Polar Operations

Operation Polar Fade targets the Arctic, North Pole, and South Pole. The campaign is less about conventional state conquest and more about claiming global completeness, resource rights, and extreme-terrain bases. Earlier Antarctic annexation planning also appears in the 1983 multi-front expansion.

## Final African Conquest

Operation Eternal Fade is the final African sweep. It targets Ethiopia, Somalia, Uganda, Kenya, Tanzania, Zambia, Zimbabwe, Mozambique, Madagascar, Benin, Togo, Nigeria, Ghana, Ivory Coast, Burkina Faso, Mali, Mauritania, Senegal, Gambia, Guinea-Bissau, Equatorial Guinea, Sierra Leone, Liberia, and remaining unclaimed African states. After this operation, the world is effectively divided between the L.E.T.F. and the United States.

## Consequences

The African and Polar campaigns give the L.E.T.F. near-total territorial reach but leave it catastrophically overextended. The final conquest strains logistics, damages infrastructure, and creates the conditions for collapse when the alliance with the United States breaks.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Major Operations of the Country Game",
        "group": "campaign",
        "kind": "index",
        "aliases": ["Operation Index", "List of Operations"],
        "body": """
## Lead

This page indexes the named and recurring operations of the Country Game. Operations are fictional in-universe campaign labels from the PDF transcript and generated wiki.

## Early Crisis Operations

- Operation Flaming Sword: U.S. contingency planning around Cuba during the Soviet annexation crisis.
- Operation Silent Sky: U.S. counterintelligence response to the Soviet global speaker project.
- Operation Sky Shield: U.S. and NATO action to stop the Soviet self-destructive nuclear plan.

## L.E.T.F. Expansion Operations

- Operation Cuban Fade: L.E.T.F. annexation of Cuba with U.S. support.
- Operation Euphrates Fade: Annexation of Iraq.
- Operation Crescent Fade: Syria and Turkey campaign.
- Operation Sahara Fade: Libya, Chad, Niger, Cameroon, and Nigeria campaign.
- Operation Eternal Steppe: Mongolia campaign.
- Operation Northern Fade: U.S.-L.E.T.F. invasion of Mexico in 1985.
- Operation Mystic Fade: Invasion of India.
- Operation Roman Fade: Italy, San Marino, and Vatican City.
- Operation Gallic Fade: France.
- Operation Northern Fade / Operation Northern Shield: Greenland, Iceland, and Finland-related northern campaigns.
- Operation Equatorial Fade: Congo, Zaire, Angola, and Namibia.
- Operation Albion Fade: United Kingdom.
- Operation Southern Fade: South Africa.
- Operation Eastern Sovereignty: Asia and Pacific campaign.
- Operation Final Horizon: Remaining Asian and Pacific states.
- Operation Iberian Fade: Spain and Portugal.
- Operation Atlas Fade: Morocco.
- Operation Maghreb Fade: Algeria and Tunisia.
- Operation Polar Fade: Arctic and Antarctic regions.
- Operation Maple Fade: Canada.
- Operation Eastern Fade: Poland and Kaliningrad.
- Operation Iron Fade: East Germany.
- Operation Island Fade: Caribbean nations.
- Operation Andean Fade: South America.
- Operation Desert Fade: Remaining Middle East.
- Operation Aegean Fade: Cyprus, Greece, and Malta.
- Operation Balkan Fade: Balkans.
- Operation Northern Dominion: Western and Northern Europe.

## Endgame Operations

- Operation Nordic Breakpoint: L.E.T.F. campaign against Denmark and West Germany after nuclear strikes.
- Operation Eternal Fade: Final African conquest and reconstruction effort.
- Operation Total Fade: L.E.T.F. war plan against the United States.
- Operation Liberty Storm: U.S. response in the final global war.
""",
    },
    {
        "folder": "06 Technology",
        "title": "SR-91 Phantom Sky",
        "group": "technology",
        "kind": "article",
        "aliases": ["Phantom Sky", "Ethereal Falcon", "SR-91"],
        "body": """
## Lead

The SR-91 Phantom Sky is the United States' top-secret hypersonic reconnaissance aircraft in the Country Game. It is one of the clearest results of the U.S. tripled defense budget modifier and becomes a recurring surveillance asset against L.E.T.F.-occupied territories.

## Development

The program begins as part of U.S. research into advanced interceptors, reconnaissance, and missile defense during the Soviet nuclear crisis. By 1985, the Department of Defense assigns the designation SR-91, following the naming logic of the SR-71 Blackbird. Its nickname, "Ethereal Falcon," emphasizes stealth, speed, and high-altitude invisibility.

## Capabilities

The Phantom Sky operates at hypersonic speeds, with the transcript describing Mach 5 overflight profiles. It carries high-resolution imaging, infrared scanning, and classified limited strike potential. Its purpose is to collect intelligence over hostile or monitored territory without detection.

## Test Mission

The first major test mission overflies L.E.T.F.-occupied Newport County and Hawaii. It photographs defensive emplacements, modified T-72 tanks near Newport Harbor, Morganist ceremonies, troop deployments, and joint U.S.-L.E.T.F. base activity. A mid-mission refueling trial extends the aircraft's range to the Pacific.

## Strategic Importance

The SR-91 gives the United States a way to monitor the L.E.T.F. even while allied with it. This matters because the alliance is never entirely stable. The aircraft validates U.S. technological superiority and supports later countermeasures as the L.E.T.F. grows beyond American control.

## Anachronism Notes

The aircraft is fictional and more advanced than real 1980s public aerospace technology. The PDF's initial rules allow such developments when framed as research or prototypes. The SR-91 is therefore best read as a game-canon experimental successor to the SR-71, not a real 1985 aircraft.
""",
    },
    {
        "folder": "06 Technology",
        "title": "Military Technology and Anachronisms",
        "group": "technology",
        "kind": "article",
        "aliases": ["Anachronisms", "Technology Rules"],
        "body": """
## Lead

Military technology in the Country Game is governed by an initial realism rule: the simulation should flag weapons that do not belong to the chosen period and suggest research or era-appropriate alternatives. The PDF then mixes real 1980s systems, plausible experimental programs, fictional projects, and occasional anachronisms.

## Era-Appropriate Systems

Many systems fit the early-to-mid 1980s setting: F-15 Eagles, F-14 Tomcats, F-16s, F-4 Phantoms, A-10 Thunderbolts, B-52 bombers, M1 Abrams tanks, T-72 tanks, BMP-1 vehicles, MiG-21s, Su-17s, Su-24s, Tu-95 bombers, Tu-22M bombers, AWACS aircraft, Los Angeles-class submarines, and Ohio-class submarines. These create the baseline Cold War military texture.

## Fictional Or Prototype Systems

The Dark Angel 12, SR-91 Phantom Sky, and some advanced interceptor programs are fictional or speculative. They are justified in-canon by the U.S. tripled defense budget and classified research. Prototype references such as the A-12 Archangel and YF-12 also fit the canon's habit of reviving or extending experimental aircraft into operational roles.

## Anachronisms

Some details stretch or break the 1980s rule. F-22 Raptors and B-2 bombers appear in the final war even though they are not operational 1989 systems. Advanced drones, cyber language, and some hypersonic capabilities also exceed normal public 1980s technology. Rather than deleting those details, the wiki flags them as canon anachronisms or prototype exaggerations.

## Graph Use

Technology pages link the early Cold War crisis to the final war. They explain how the United States translates its budget modifier into reconnaissance, missile defense, and air superiority, and how the L.E.T.F. relies on Soviet-style equipment, captured resources, mass troop deployments, and symbolic modifications.

## Recommended Interpretation

For future writing in this vault, treat ordinary Cold War equipment as standard, treat SR-91 and similar systems as classified game-canon prototypes, and treat F-22/B-2 usage before operational availability as an anachronism unless explicitly reframed as a prototype research outcome.
""",
    },
    {
        "folder": "04 Campaigns",
        "title": "Operation Watchful Fade 2",
        "group": "campaign",
        "kind": "article",
        "aliases": ["Watchful Fade 2"],
        "body": """
## Lead

Operation Watchful Fade 2 is a 1987 L.E.T.F. intelligence operation designed to identify which countries are actively opposing the empire and which are afraid enough to remain neutral or become vulnerable to pressure. It is one of the clearest examples of the L.E.T.F. shifting from pure conquest to global strategic management.

## Method

The operation uses high-altitude reconnaissance, espionage networks, signals intelligence, psychological assessment, and diplomatic monitoring. The SR-91 Poltergeist is named as an advanced reconnaissance platform, indicating U.S.-aided technology or derivative aircraft in L.E.T.F. service.

## Findings

Hostile nations include the United Kingdom, Japan, France, Australia, and Boombayah remnants. These states provide diplomatic, military, or covert support to resistance movements. Neutral or passive actors include Germany, Canada, and exiled Indian forces. Fearful states include Italy, Saudi Arabia, and South Africa.

## Strategic Consequences

The operation gives the L.E.T.F. a target list. Hostile nations become candidates for direct invasion, while fearful nations become candidates for intimidation, propaganda, or coerced alignment. The sequence of later campaigns shows the operation's effect: Italy, France, the United Kingdom, South Africa, and other listed regions soon become targets.

## Importance

Watchful Fade 2 functions like a midgame intelligence census of the world. It shows that the L.E.T.F. is no longer reacting only to nearby borders; it is categorizing the entire international system as enemies, neutrals, or future prey.
""",
    },
    {
        "folder": "08 Final War",
        "title": "Final NATO LETF War",
        "group": "final-war",
        "kind": "article",
        "aliases": ["The Final NATO-L.E.T.F. War", "Operation Nordic Breakpoint"],
        "body": """
## Lead

The Final NATO LETF War is the 1989 endgame conflict between the L.E.T.F. and the last NATO strongholds, especially West Germany and Denmark. It follows widespread L.E.T.F. annexations across Europe and the United States' departure from NATO. The war ends with the collapse of organized NATO resistance.

## Trigger

West Germany and Denmark launch nuclear strikes against major L.E.T.F. capitals, including Cairo, Moscow, Washington D.C., and other strategic locations. The strikes are intended to deter or cripple L.E.T.F. domination, but they also provide the L.E.T.F. with the justification for its final European campaign.

## Operation Nordic Breakpoint

The L.E.T.F. deploys millions of troops, Fade Tanks, Su-24s, MiG-21s, drones, naval forces, submarines, and amphibious units. The United States supports the campaign with A-12 Archangel and YF-12 prototypes, interceptors, reconnaissance, and air superiority operations. Denmark is attacked through Copenhagen and Jutland, while West Germany is attacked through Berlin, Hamburg, and the Ruhr.

## Outcome

Copenhagen falls after urban combat. Berlin and Hamburg fall after prolonged resistance. NATO air superiority collapses, though nuclear fallout disrupts L.E.T.F. operations. Denmark becomes the Nordic Province of the Fade, and West Germany becomes part of the Western European Province of the Fade.

## Consequences

The collapse of NATO removes the last organized Western military alliance from the setting. The United Nations effectively ceases to matter, resistance movements become fragmented, and the U.S.-L.E.T.F. alliance appears unchallenged. This victory directly precedes [[L.E.T.F. Final Global Conquest]] and indirectly sets up [[Final Global War]].
""",
    },
    {
        "folder": "08 Final War",
        "title": "L.E.T.F. Final Global Conquest",
        "group": "final-war",
        "kind": "article",
        "aliases": ["Operation Eternal Fade", "Final Global Conquest"],
        "body": """
## Lead

L.E.T.F. Final Global Conquest, also called Operation Eternal Fade, is the last imperial expansion before the final U.S.-L.E.T.F. split. After NATO collapses, the L.E.T.F. repairs devastated capitals, honors its political and religious figures, and launches a final exhausting campaign to annex remaining African countries.

## Reconstruction

The L.E.T.F. rebuilds Cairo, Fade's Crown, and other damaged capitals. It also checks on major religious and political symbols: King Darius Morgan, Adolf Hitler, the grave of Magnus Maximus, Grog Morgan, Vex Bolts, and Mr. Clean. Reconstruction is therefore both practical and ceremonial.

## African Campaign

The final campaign targets Ethiopia, Somalia, Uganda, Kenya, Tanzania, Zambia, Zimbabwe, Mozambique, Madagascar, Benin, Togo, Nigeria, Ghana, Ivory Coast, Burkina Faso, Mali, Mauritania, Senegal, Gambia, Guinea-Bissau, Equatorial Guinea, Sierra Leone, Liberia, and remaining unclaimed states. The L.E.T.F. deploys millions of troops, aircraft, artillery, amphibious forces, and desert warfare units.

## Result

The entire African continent is unified under the African Province of the Fade. The United Nations dissolves because there are no remaining member states capable of meaningful operation. The world is divided between L.E.T.F. territories and the United States.

## Importance

This is the L.E.T.F.'s maximum extent. It achieves the total domination it has pursued since 1981, but only by exhausting its firepower, stretching its logistics, and creating a brittle empire dependent on continued alliance with the United States. That alliance collapses immediately afterward.
""",
    },
    {
        "folder": "08 Final War",
        "title": "Final Global War",
        "group": "final-war",
        "kind": "article",
        "aliases": ["L.E.T.F. vs. United States", "Operation Total Fade", "Operation Liberty Storm"],
        "body": """
## Lead

The Final Global War is the concluding conflict of the Country Game. After achieving near-total global domination alongside the United States, the L.E.T.F. betrays its former ally and declares war. The United States responds with full nuclear retaliation, total military mobilization, heightened NORAD readiness, and efforts to establish air superiority across its controlled territories.

## Belligerents

The L.E.T.F. commits its entire society to war. Half its army protects leaders and sacred figures, while the other half attacks America. It launches nuclear strikes against Washington, D.C., the Pentagon, NORAD, U.S. cities, military bases, and population centers. The United States targets Cairo, Fade's Crown, occupied capitals, leadership residences, monuments, bunkers, and L.E.T.F. military concentrations.

## Military Course

The war includes nuclear exchanges, amphibious invasion attempts, U.S. counterattacks, air battles, naval interceptions, and special operations. L.E.T.F. forces use MiG-21s, Su-24s, F-16s, nuclear weapons, and mass infantry. The United States uses its full air force, bombers, reconnaissance aircraft, experimental interceptors, carrier groups, submarines, missile destroyers, radar networks, and NORAD command systems.

## Casualties And Destruction

The PDF describes hundreds of millions dead from nuclear strikes, conventional combat, famine, disease, and infrastructure collapse. Major cities are destroyed or rendered uninhabitable. The world population is reduced by more than seventy percent, and civilization enters a dark age.

## Outcome

The L.E.T.F. is defeated. Its leaders are killed or captured, including King Darius Morgan and Adolf Hitler after initial bunker survival. Mr. Clean and Vex Bolts are presumed dead in nuclear blasts. L.E.T.F. territories fragment into chaos, and resistance movements reclaim regions. The United States suffers catastrophic damage, including the destruction of the White House, but NORAD remains operational and the U.S. survives as the only organized superpower.

## Aftermath

The final state of the world is post-apocalyptic. The L.E.T.F. is disbanded, its empire collapses, and survivors face reconstruction under a shattered global order. The war resolves the entire 1981-1989 arc by destroying the empire created through the U.S.-L.E.T.F. alliance.
""",
    },
]


def make_hubs(sections: list[dict]) -> None:
    for key, meta in GROUPS.items():
        title = meta["hub"]
        related_events = [
            s for s in sections if classify_event(s["title"]) == key
        ][:30]
        events = "\n".join(f"- {link(slug_filename(s['title']), s['title'])}" for s in related_events) or "- No dated events are assigned directly to this hub."
        body = f"""
## Hub Purpose

This hub gathers pages in the {meta['label']} graph group. Notes link here so Obsidian can pull related articles into a visible neighborhood.

## Group Tag

`#{meta['tag']}`

## Key Links

- {link('Country Game 1981-1989 Atlas')}
- {link('Canon Index')}
- {link('Timeline 1981-1989')}

## Dated Event Pages In This Group

{events}
"""
        write_note("00 Atlas/Graph Hubs", title, key, "hub", body)


def make_source_note() -> None:
    src_pdf_in_vault = VAULT / "_Sources" / "80s country game.pdf"
    if PDF_SOURCE.exists() and not src_pdf_in_vault.exists():
        shutil.copy2(PDF_SOURCE, src_pdf_in_vault)
    body = """
## Source Files

- [[80s country game.pdf]]
- [[80s country game extracted transcript.txt]]

## Description

This note anchors the generated wiki to the attached PDF. The extracted transcript was produced with pdfplumber and then transformed into encyclopedia-style Obsidian notes. The generated articles are in-universe summaries of the fictional role-play canon, not factual history.

## Extraction Notes

The PDF contains 319 pages and was split into 77 dated event sections. The event articles include source page ranges so the relevant place in the PDF can be found again.
"""
    write_note("_Sources", "80s country game source note", "atlas", "source", body, aliases=["Source PDF", "80s country game.pdf"])


def make_timeline(sections: list[dict]) -> None:
    years: dict[str, list[dict]] = {str(y): [] for y in range(1981, 1990)}
    for section in sections:
        m = re.search(r"(1981|1982|1983|1984|1985|1986|1987|1988|1989)", section["title"])
        if m:
            years[m.group(1)].append(section)

    overview_lines = []
    for year, items in years.items():
        overview_lines.append(f"## {year}\n")
        overview_lines.append(f"- {link(year)}")
        for item in items:
            overview_lines.append(f"- {link(slug_filename(item['title']), item['title'])}")
        overview_lines.append("")
    write_note(
        "07 Timeline",
        "Timeline 1981-1989",
        "timeline",
        "index",
        "## Lead\n\nThe timeline indexes every dated event article generated from the PDF.\n\n" + "\n".join(overview_lines),
        aliases=["Country Game Timeline"],
    )

    for year, items in years.items():
        body_lines = [f"## Lead\n\n{year} in the Country Game canon links the major dated events for this year.\n"]
        body_lines.append("## Events\n")
        for item in items:
            body_lines.append(f"- {link(slug_filename(item['title']), item['title'])} - source pages {item['start_page']}-{item['end_page']}")
        if not items:
            body_lines.append("- No dated event sections found for this year.")
        write_note("07 Timeline/Year Pages", year, "timeline", "year", "\n".join(body_lines), aliases=[f"{year} timeline"])


def write_event_pages(sections: list[dict]) -> None:
    for section in sections:
        title = slug_filename(section["title"])
        group = classify_event(section["title"])
        write_note(
            event_folder(section),
            title,
            group,
            "event",
            make_event_body(section),
            aliases=[section["title"]],
            extra={
                "source_page_start": section["start_page"],
                "source_page_end": section["end_page"],
                "event_number": section["index"],
            },
        )


def write_css() -> None:
    snippets = VAULT / ".obsidian" / "snippets"
    snippets.mkdir(parents=True, exist_ok=True)
    css = """
.cg-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  color: #111;
  font-weight: 700;
  font-size: 0.78em;
  line-height: 1.6;
  margin: 0.25rem 0 0.75rem;
}
.cg-swatch {
  display: inline-block;
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 4px;
  vertical-align: -0.12rem;
  margin-right: 0.25rem;
  border: 1px solid rgba(0, 0, 0, 0.25);
}
.cg-atlas { background: #FFD166; }
.cg-faction { background: #118AB2; color: #fff; }
.cg-cold-war { background: #EF476F; color: #fff; }
.cg-letf { background: #8338EC; color: #fff; }
.cg-campaign { background: #F77F00; color: #111; }
.cg-ideology { background: #06D6A0; color: #111; }
.cg-technology { background: #4D908E; color: #fff; }
.cg-timeline { background: #577590; color: #fff; }
.cg-final { background: #E63946; color: #fff; }
"""
    (snippets / "country-game-wiki.css").write_text(css.strip() + "\n", encoding="utf-8", newline="\n")

    appearance_path = VAULT / ".obsidian" / "appearance.json"
    try:
        appearance = json.loads(appearance_path.read_text(encoding="utf-8"))
    except Exception:
        appearance = {}
    snippets_enabled = appearance.get("enabledCssSnippets", [])
    if "country-game-wiki" not in snippets_enabled:
        snippets_enabled.append("country-game-wiki")
    appearance["enabledCssSnippets"] = snippets_enabled
    appearance_path.write_text(json.dumps(appearance, indent=2), encoding="utf-8", newline="\n")


def write_graph_config() -> None:
    graph_path = VAULT / ".obsidian" / "graph.json"
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except Exception:
        graph = {}
    graph.update(
        {
            "collapse-filter": True,
            "search": "",
            "showTags": True,
            "showAttachments": False,
            "hideUnresolved": False,
            "showOrphans": True,
            "collapse-color-groups": False,
            "colorGroups": [
                {"query": f"tag:#{meta['tag']}", "color": {"a": 1, "rgb": meta["rgb"]}}
                for meta in GROUPS.values()
            ],
            "collapse-display": True,
            "showArrow": False,
            "textFadeMultiplier": 0,
            "nodeSizeMultiplier": 1.2,
            "lineSizeMultiplier": 1.1,
            "collapse-forces": True,
            "centerStrength": 0.518713248970312,
            "repelStrength": 10,
            "linkStrength": 1,
            "linkDistance": 220,
            "scale": 1,
            "close": True,
        }
    )
    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8", newline="\n")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing extracted transcript: {SOURCE}")
    for folder in ["00 Atlas", "01 Factions", "02 Cold War Crisis", "03 LETF State", "04 Campaigns", "05 Ideology and Culture", "06 Technology", "07 Timeline", "08 Final War"]:
        (VAULT / folder).mkdir(parents=True, exist_ok=True)

    sections = parse_sections()
    make_source_note()
    for article in MAJOR_ARTICLES:
        write_note(
            article["folder"],
            article["title"],
            article["group"],
            article["kind"],
            article["body"],
            article.get("aliases", []),
        )
    make_hubs(sections)
    make_timeline(sections)
    write_event_pages(sections)
    write_css()
    write_graph_config()
    print(f"Wrote {len(MAJOR_ARTICLES)} major articles")
    print(f"Wrote {len(sections)} event articles")
    print("Updated graph color groups and CSS snippet")


if __name__ == "__main__":
    main()
