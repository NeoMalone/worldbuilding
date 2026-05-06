from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


VAULT = Path(r"C:\Users\lemon\Downloads\(OBSIDIAN) Country Game, 1981-1989\Country Game, 1981-1989")
SOURCE = VAULT / "_Sources" / "80s country game extracted transcript.txt"


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


def frontmatter(title: str, group: str, kind: str, aliases: Iterable[str] = ()) -> str:
    lines = [
        "---",
        f'title: "{clean_ascii(title)}"',
        "aliases:",
    ]
    for alias in aliases:
        lines.append(f"  - {clean_ascii(alias)}")
    lines.extend(
        [
            "tags:",
            "  - country-game/wiki",
            f"  - {GROUPS[group]['tag']}",
            f"  - type/{kind}",
            'canon: "fictional alternate-history role-play based on 80s country game.pdf"',
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def wrap(text: str) -> str:
    paras = [p.strip() for p in clean_ascii(text).strip().split("\n\n")]
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
            out.append("\n".join(re.findall(r".{1,100}(?:\s+|$)", para)))
    return "\n\n".join(out).strip() + "\n"


def write_note(folder: str, title: str, group: str, kind: str, body: str, aliases: Iterable[str] = ()) -> Path:
    folder_path = VAULT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    path = folder_path / f"{slug_filename(title)}.md"
    content = frontmatter(title, group, kind, aliases)
    content += f"# {clean_ascii(title)}\n\n{badge(group)}\n\n{wrap(body)}"
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def spec(
    title: str,
    folder: str,
    group: str,
    kind: str,
    role: str,
    aliases: Iterable[str] = (),
    links: Iterable[str] = (),
) -> dict:
    return {
        "title": title,
        "folder": folder,
        "group": group,
        "kind": kind,
        "role": role,
        "aliases": list(aliases),
        "links": list(links),
    }


def territory(title: str, region: str, aliases: Iterable[str] = (), links: Iterable[str] = ()) -> dict:
    role = (
        f"{title} is a country, territory, or strategic region in the {region} portion of the Country Game canon. "
        "This node exists to make the graph more granular: it gathers every direct mention, nearby event article, "
        "and major campaign connection instead of leaving the place buried inside a larger regional summary."
    )
    return spec(title, "09 Countries and Territories", "faction", "territory", role, aliases, ["Campaign Hub", *links])


def operation(title: str, role: str, aliases: Iterable[str] = (), links: Iterable[str] = ()) -> dict:
    return spec(title, "10 Operations", "campaign", "operation", role, aliases, ["Major Operations of the Country Game", *links])


def person(title: str, role: str, aliases: Iterable[str] = (), links: Iterable[str] = ()) -> dict:
    return spec(title, "11 People and Leaders", "faction", "person", role, aliases, ["Faction Hub", *links])


def institution(title: str, role: str, aliases: Iterable[str] = (), links: Iterable[str] = (), group: str = "faction") -> dict:
    return spec(title, "12 Institutions and Alliances", group, "institution", role, aliases, ["Faction Hub", *links])


def equipment(title: str, role: str, aliases: Iterable[str] = (), links: Iterable[str] = ()) -> dict:
    return spec(title, "13 Technology and Equipment", "technology", "equipment", role, aliases, ["Technology Hub", "Military Technology and Anachronisms", *links])


def concept(title: str, role: str, aliases: Iterable[str] = (), links: Iterable[str] = (), group: str = "ideology") -> dict:
    return spec(title, "14 Concepts and Provinces", group, "concept", role, aliases, ["Country Game 1981-1989 Atlas", *links])


TERRITORIES = [
    territory("East Germany", "early Cold War crisis", ["German Democratic Republic", "GDR"], ["West Germany and NATO", "Early Cold War Crisis"]),
    territory("Cuba", "Caribbean and early Cold War crisis", [], ["Early Cold War Crisis", "Americas Campaigns"]),
    territory("North Korea", "Soviet aid and Pacific diplomacy", [], ["Soviet Union", "Early Cold War Crisis"]),
    territory("Egypt", "L.E.T.F. origin", [], ["Lowest Egyptian Taper Fade", "Adolf Hitler in the Country Game"]),
    territory("Israel", "Middle Eastern expansion", [], ["Middle Eastern Expansion"]),
    territory("Sudan", "Middle Eastern and African expansion", [], ["Middle Eastern Expansion", "African and Polar Campaigns"]),
    territory("Newport County", "American foothold and L.E.T.F. protectorate", ["Newport County, Rhode Island"], ["Americas Campaigns", "SR-91 Phantom Sky"]),
    territory("Jordan", "Middle Eastern expansion", [], ["Middle Eastern Expansion"]),
    territory("Saudi Arabia", "Middle Eastern expansion", [], ["Middle Eastern Expansion", "Operation Watchful Fade 2"]),
    territory("Iraq", "Middle Eastern expansion", [], ["Middle Eastern Expansion"]),
    territory("Syria", "Middle Eastern expansion", [], ["Middle Eastern Expansion"]),
    territory("Turkey", "Middle Eastern and European gateway", [], ["Middle Eastern Expansion", "European Campaigns"]),
    territory("Libya", "North African expansion", [], ["African and Polar Campaigns"]),
    territory("Chad", "Central African expansion", [], ["African and Polar Campaigns"]),
    territory("Niger", "West African expansion", [], ["African and Polar Campaigns"]),
    territory("Cameroon", "West African expansion", [], ["African and Polar Campaigns"]),
    territory("Nigeria", "West African expansion", [], ["African and Polar Campaigns"]),
    territory("North Yemen", "Arabian Peninsula expansion", [], ["Middle Eastern Expansion"]),
    territory("South Yemen", "Arabian Peninsula expansion", [], ["Middle Eastern Expansion"]),
    territory("Oman", "Arabian Peninsula expansion", [], ["Middle Eastern Expansion"]),
    territory("Armenia", "Caucasus campaign", [], ["Former Soviet Territorial Campaigns"]),
    territory("Azerbaijan", "Caucasus campaign", [], ["Former Soviet Territorial Campaigns"]),
    territory("Georgia", "Caucasus campaign", [], ["Former Soviet Territorial Campaigns"]),
    territory("Ukraine", "former Soviet territorial campaign", [], ["Former Soviet Territorial Campaigns"]),
    territory("Kuwait", "Middle Eastern expansion", [], ["Middle Eastern Expansion"]),
    territory("Antarctica", "polar and multi-front expansion", [], ["African and Polar Campaigns"]),
    territory("Siberia", "former Soviet territorial campaign", [], ["Former Soviet Territorial Campaigns"]),
    territory("Far Eastern District", "former Soviet territorial campaign", ["Russian Far East"], ["Former Soviet Territorial Campaigns"]),
    territory("Kazakhstan", "Central Asian expansion", [], ["Former Soviet Territorial Campaigns"]),
    territory("Kyrgyzstan", "Central Asian expansion", [], ["Former Soviet Territorial Campaigns"]),
    territory("Tajikistan", "Central Asian expansion", [], ["Former Soviet Territorial Campaigns"]),
    territory("Uzbekistan", "Central Asian expansion", [], ["Former Soviet Territorial Campaigns"]),
    territory("Turkmenistan", "Central Asian expansion", [], ["Former Soviet Territorial Campaigns"]),
    territory("Hawaii", "Pacific staging and transferred territory", [], ["Americas Campaigns", "Asia Pacific Campaigns"]),
    territory("Japan", "Asia-Pacific campaign", [], ["Asia Pacific Campaigns", "Operation Watchful Fade 2"]),
    territory("Mongolia", "Asian expansion", [], ["Asia Pacific Campaigns"]),
    territory("China", "Asian expansion", [], ["Asia Pacific Campaigns"]),
    territory("Mexico", "North American campaign", [], ["Americas Campaigns"]),
    territory("Argentina", "South American campaign", [], ["Americas Campaigns", "Boombayah"]),
    territory("Colombia", "South American campaign", [], ["Americas Campaigns"]),
    territory("Chile", "South American campaign", [], ["Americas Campaigns"]),
    territory("Bolivia", "South American campaign", [], ["Americas Campaigns"]),
    territory("India", "South Asian campaign", [], ["Asia Pacific Campaigns", "Boombayah"]),
    territory("Australia", "Pacific campaign", [], ["Asia Pacific Campaigns", "Operation Watchful Fade 2"]),
    territory("Czechoslovakia", "European campaign", [], ["European Campaigns"]),
    territory("Austria", "European campaign", [], ["European Campaigns"]),
    territory("Liechtenstein", "European campaign", [], ["European Campaigns"]),
    territory("Switzerland", "European campaign", [], ["European Campaigns", "Operation Watchful Fade 2"]),
    territory("South Korea", "Korean campaign", [], ["Asia Pacific Campaigns", "Operation Watchful Fade 2"]),
    territory("Italy", "Southern European campaign", [], ["European Campaigns", "Operation Watchful Fade 2"]),
    territory("San Marino", "Southern European campaign", [], ["European Campaigns"]),
    territory("Vatican City", "Southern European and symbolic campaign", [], ["European Campaigns", "Morganism"]),
    territory("France", "Western European campaign", [], ["European Campaigns", "Operation Watchful Fade 2"]),
    territory("Greenland", "North Atlantic campaign", [], ["European Campaigns"]),
    territory("Iceland", "North Atlantic campaign", [], ["European Campaigns"]),
    territory("Congo", "Central African campaign", [], ["African and Polar Campaigns"]),
    territory("Zaire", "Central African campaign", ["Democratic Republic of the Congo"], ["African and Polar Campaigns"]),
    territory("Angola", "Central African campaign", [], ["African and Polar Campaigns"]),
    territory("Namibia", "Southern African campaign", [], ["African and Polar Campaigns"]),
    territory("United Kingdom", "European campaign", ["UK", "Britain"], ["European Campaigns", "Operation Watchful Fade 2"]),
    territory("South Africa", "Southern African campaign", [], ["African and Polar Campaigns", "Operation Watchful Fade 2"]),
    territory("Afghanistan", "final Asian campaign", [], ["Asia Pacific Campaigns"]),
    territory("Maldives", "final Asian campaign", [], ["Asia Pacific Campaigns"]),
    territory("Timor-Leste", "final Asian-Pacific campaign", ["East Timor"], ["Asia Pacific Campaigns"]),
    territory("Philippines", "final Asian-Pacific campaign", [], ["Asia Pacific Campaigns"]),
    territory("Macau", "Asian-Pacific campaign", [], ["Asia Pacific Campaigns"]),
    territory("Hong Kong", "Asian-Pacific campaign", [], ["Asia Pacific Campaigns"]),
    territory("Spain", "Iberian campaign", [], ["European Campaigns"]),
    territory("Portugal", "Iberian campaign", [], ["European Campaigns"]),
    territory("Morocco", "North African campaign", [], ["African and Polar Campaigns"]),
    territory("Algeria", "Maghreb campaign", [], ["African and Polar Campaigns"]),
    territory("Tunisia", "Maghreb campaign", [], ["African and Polar Campaigns"]),
    territory("Arctic", "polar campaign", [], ["African and Polar Campaigns"]),
    territory("North Pole", "polar campaign", [], ["African and Polar Campaigns"]),
    territory("South Pole", "polar campaign", [], ["African and Polar Campaigns"]),
    territory("Finland", "Northern European campaign", [], ["European Campaigns"]),
    territory("Poland", "Eastern European campaign", [], ["European Campaigns"]),
    territory("Kaliningrad", "Eastern European campaign", [], ["European Campaigns"]),
    territory("Bahamas", "Caribbean campaign", ["The Bahamas"], ["Americas Campaigns"]),
    territory("Dominican Republic", "Caribbean campaign", [], ["Americas Campaigns"]),
    territory("Haiti", "Caribbean campaign", [], ["Americas Campaigns"]),
    territory("Trinidad and Tobago", "Caribbean campaign", [], ["Americas Campaigns"]),
    territory("Venezuela", "South American campaign", [], ["Americas Campaigns"]),
    territory("Guyana", "South American campaign", [], ["Americas Campaigns"]),
    territory("Suriname", "South American campaign", [], ["Americas Campaigns"]),
    territory("French Guiana", "South American campaign", [], ["Americas Campaigns"]),
    territory("Ecuador", "South American campaign", [], ["Americas Campaigns"]),
    territory("Peru", "South American campaign", [], ["Americas Campaigns"]),
    territory("Paraguay", "South American campaign", [], ["Americas Campaigns"]),
    territory("Uruguay", "South American campaign", [], ["Americas Campaigns"]),
    territory("Iran", "remaining Middle East campaign", [], ["Middle Eastern Expansion"]),
    territory("Bahrain", "remaining Middle East campaign", [], ["Middle Eastern Expansion"]),
    territory("Qatar", "remaining Middle East campaign", [], ["Middle Eastern Expansion"]),
    territory("United Arab Emirates", "remaining Middle East campaign", ["UAE"], ["Middle Eastern Expansion"]),
    territory("Lebanon", "remaining Middle East campaign", [], ["Middle Eastern Expansion"]),
    territory("Cyprus", "Aegean campaign", [], ["European Campaigns"]),
    territory("Greece", "Aegean campaign", [], ["European Campaigns", "West Germany and NATO"]),
    territory("Malta", "Aegean campaign", [], ["European Campaigns"]),
    territory("Yugoslavia", "Balkan campaign", [], ["European Campaigns"]),
    territory("Romania", "Balkan campaign", [], ["European Campaigns"]),
    territory("Hungary", "Balkan campaign", [], ["European Campaigns"]),
    territory("Bulgaria", "Balkan campaign", [], ["European Campaigns"]),
    territory("Albania", "Balkan campaign", [], ["European Campaigns"]),
    territory("Belgium", "Northern Dominion campaign", [], ["European Campaigns", "West Germany and NATO"]),
    territory("Netherlands", "Northern Dominion campaign", [], ["European Campaigns", "West Germany and NATO"]),
    territory("Luxembourg", "Northern Dominion campaign", [], ["European Campaigns", "West Germany and NATO"]),
    territory("Andorra", "Northern Dominion campaign", [], ["European Campaigns"]),
    territory("Ireland", "Northern Dominion campaign", [], ["European Campaigns"]),
    territory("Norway", "Northern Dominion campaign", [], ["European Campaigns", "West Germany and NATO"]),
    territory("Sweden", "Northern Dominion campaign", [], ["European Campaigns"]),
    territory("Denmark", "final NATO campaign", [], ["Final NATO LETF War", "West Germany and NATO"]),
    territory("Ethiopia", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Somalia", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Uganda", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Kenya", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Tanzania", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Zambia", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Zimbabwe", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Mozambique", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Madagascar", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Benin", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Togo", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Ghana", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Ivory Coast", "final African campaign", ["Cote d'Ivoire"], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Burkina Faso", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Mali", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Mauritania", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Senegal", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Gambia", "final African campaign", ["The Gambia"], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Guinea-Bissau", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Equatorial Guinea", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Sierra Leone", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
    territory("Liberia", "final African campaign", [], ["African and Polar Campaigns", "L.E.T.F. Final Global Conquest"]),
]


OPERATIONS = [
    operation("Operation Flaming Sword", "A U.S. contingency plan for intervention if Soviet-occupied Cuba becomes a permanent strategic threat.", links=["Early Cold War Crisis", "Cuba"]),
    operation("Operation Silent Sky", "A U.S. counterintelligence campaign against the Soviet global speaker project and its infrastructure.", links=["Early Cold War Crisis"]),
    operation("Operation Sky Shield", "The U.S. and NATO air-wing response that prevents the Soviet self-destructive nuclear launch.", links=["Early Cold War Crisis", "Soviet Union"]),
    operation("Operation Cuban Fade", "The U.S.-supported L.E.T.F. annexation of Cuba after the Soviet collapse.", links=["Americas Campaigns", "Cuba"]),
    operation("Operation Euphrates Fade", "The L.E.T.F. and U.S. campaign that captures Basra, Baghdad, and Iraq's oil infrastructure.", links=["Middle Eastern Expansion", "Iraq"]),
    operation("Operation Crescent Fade", "The campaign against Syria and Turkey, opening routes from the Middle East toward Europe.", links=["Middle Eastern Expansion", "Syria", "Turkey"]),
    operation("Operation Sahara Fade", "The African expansion into Libya, Chad, Niger, Cameroon, and Nigeria.", links=["African and Polar Campaigns"]),
    operation("Operation Eternal Steppe", "The invasion of Mongolia and conversion of the country into the Great Steppe Province of the Fade.", links=["Asia Pacific Campaigns", "Mongolia"]),
    operation("Operation Northern Fade - Mexico", "The 1985 U.S.-L.E.T.F. invasion of Mexico with a northern U.S. front and L.E.T.F. landings from Cuba.", ["Operation Northern Fade"], ["Americas Campaigns", "Mexico"]),
    operation("Operation Mystic Fade", "The L.E.T.F. invasion of India and the campaign opposed by Boombayah-funded Indian forces.", links=["Asia Pacific Campaigns", "India", "Boombayah"]),
    operation("Operation Roman Fade", "The invasion of Italy, San Marino, and Vatican City.", links=["European Campaigns", "Italy", "Vatican City"]),
    operation("Operation Gallic Fade", "The invasion of France and a major stage in the L.E.T.F. assault on Western Europe.", links=["European Campaigns", "France"]),
    operation("Operation Northern Fade - Greenland and Iceland", "The North Atlantic campaign targeting Greenland and Iceland after the French campaign planning phase.", ["Operation Northern Fade"], ["European Campaigns", "Greenland", "Iceland"]),
    operation("Operation Equatorial Fade", "The Central and Southern African campaign targeting Congo, Zaire, Angola, and Namibia.", links=["African and Polar Campaigns"]),
    operation("Operation Albion Fade", "The L.E.T.F. invasion of the United Kingdom.", links=["European Campaigns", "United Kingdom"]),
    operation("Operation Southern Fade", "The L.E.T.F. invasion of South Africa.", links=["African and Polar Campaigns", "South Africa"]),
    operation("Operation Eastern Sovereignty", "The full-scale Asia and Pacific campaign spanning South Asia, Southeast Asia, Pacific territories, Macau, and Hong Kong.", links=["Asia Pacific Campaigns"]),
    operation("Operation Final Horizon", "The campaign to annex remaining Asian and Pacific nations after the main regional push.", links=["Asia Pacific Campaigns"]),
    operation("Operation Iberian Fade", "The campaign against Spain and Portugal.", links=["European Campaigns", "Spain", "Portugal"]),
    operation("Operation Atlas Fade", "The invasion of Morocco and the beginning of a North African consolidation push.", links=["African and Polar Campaigns", "Morocco"]),
    operation("Operation Maghreb Fade", "The campaign against Algeria and Tunisia after the annexation of Morocco.", links=["African and Polar Campaigns", "Algeria", "Tunisia"]),
    operation("Operation Polar Fade", "The attempt to annex the Arctic, North Pole, South Pole, and polar resource zones.", links=["African and Polar Campaigns", "Arctic"]),
    operation("Operation Maple Fade", "The L.E.T.F. invasion of Canada from Cuba, Hawaii, and Chukotka.", links=["Americas Campaigns", "Canada"]),
    operation("Operation Eastern Fade", "The invasion of Poland and Kaliningrad and the declared end of remaining Russian influence.", links=["European Campaigns", "Poland", "Kaliningrad"]),
    operation("Operation Iron Fade", "The campaign against East Germany that avoids West Germany at first while recreating a Cold War-style divide.", links=["European Campaigns", "East Germany"]),
    operation("Operation Island Fade", "The Caribbean campaign against the Bahamas, Dominican Republic, Haiti, and Trinidad and Tobago.", links=["Americas Campaigns"]),
    operation("Operation Andean Fade", "The South American campaign against Venezuela, Guyana, Suriname, French Guiana, Ecuador, Peru, Paraguay, and Uruguay.", links=["Americas Campaigns"]),
    operation("Operation Desert Fade", "The 1989 campaign against the remaining Middle East: Iran, Bahrain, Qatar, UAE, and Lebanon.", links=["Middle Eastern Expansion"]),
    operation("Operation Aegean Fade", "The campaign against Cyprus, Greece, and Malta.", links=["European Campaigns"]),
    operation("Operation Balkan Fade", "The full-scale annexation campaign against Yugoslavia, Romania, Hungary, Bulgaria, and Albania.", links=["European Campaigns"]),
    operation("Operation Northern Dominion", "The war against Belgium, the Netherlands, Luxembourg, Andorra, Ireland, Norway, and Sweden.", links=["European Campaigns"]),
    operation("Operation Nordic Breakpoint", "The final L.E.T.F. campaign against Denmark and West Germany after nuclear strikes on major capitals.", links=["Final NATO LETF War"]),
    operation("Operation Eternal Fade", "The final African conquest and reconstruction operation that leaves only the United States and L.E.T.F. standing.", links=["L.E.T.F. Final Global Conquest"]),
    operation("Operation Total Fade", "The L.E.T.F. war plan against the United States in the final global war.", links=["Final Global War"]),
    operation("Operation Liberty Storm", "The United States' final-war response to the L.E.T.F. betrayal.", links=["Final Global War"]),
    operation("Operation Watchful Fade 2", "The 1987 intelligence operation identifying hostile, neutral, and fearful countries.", links=["Operation Watchful Fade 2"]),
]


PEOPLE = [
    person("Ronald Reagan", "The U.S. president associated with defense-budget allocation, interceptor research, and Cold War response.", links=["United States of America"]),
    person("Helmut Schmidt", "The West German chancellor attached to the humanitarian East German crossing and early NATO crisis response.", links=["West Germany and NATO"]),
    person("Pierre Trudeau", "The Canadian prime minister who introduces the War Preparedness Tax during Soviet escalation.", links=["Canada"]),
    person("Leonid Brezhnev", "The Soviet premier whose erratic decisions drive the nuclear crisis, flag changes, and self-destructive Soviet arc.", links=["Soviet Union"]),
    person("Kim Il-sung", "The North Korean leader who considers and provides limited support for Soviet plans against Canada.", links=["North Korea", "Soviet Union"]),
    person("Erich Honecker", "The East German leader targeted by a Soviet assassination plot after East Germany drifts toward NATO protection.", links=["East Germany", "West Germany and NATO"]),
    person("Fidel Castro", "The Cuban leader whose position becomes tenuous after Soviet occupation and Cuba's return to independence.", links=["Cuba"]),
    person("Madison", "The player-associated leader of Brazil/Boombayah and the equal-rights counterweight to L.E.T.F. expansion.", links=["Boombayah"]),
    person("Landon", "The player-associated controller first tied to the USSR and then to Egypt/L.E.T.F. after Soviet collapse.", links=["Soviet Union", "Lowest Egyptian Taper Fade"]),
    person("Jaime Cuerbo", "The anarchist leader armed by unidentified forces during the Boombayah destabilization arc.", links=["Boombayah", "Americas Campaigns"]),
    person("Magnus Maximus", "The dead eternal ruler of the L.E.T.F. necrocratic system.", links=["Necrocracy", "Pantheon of Morganism"]),
    person("Grog Morgan", "A Morganist goddess of strength and resilience.", links=["Pantheon of Morganism", "Morganism"]),
    person("Dave Bluntz", "The dead goddess of leisure and music and head of the Department of Music.", links=["Department of Music and Bluntz Beats", "Pantheon of Morganism"]),
    person("Vex Bolt", "The demonic Morganist goddess of hatred, disgust, envy, and other negative forces.", ["Vex Bolts"], ["Pantheon of Morganism"]),
    person("Skibbity Toilet", "The Morganist god of war and fools, used as a chaotic battlefield symbol.", links=["Pantheon of Morganism"]),
    person("Mr. Clean", "A Morganist goddess of happiness and lightning, associated with purification and power.", links=["Pantheon of Morganism"]),
    person("Osama bin Laden", "An in-canon L.E.T.F. pilot figure in the 1984 pantheon and military expansion arc.", links=["Lowest Egyptian Taper Fade"]),
]


INSTITUTIONS = [
    institution("North Atlantic Treaty Organization", "The NATO alliance, first a Cold War defense bloc and later the last organized barrier against the L.E.T.F.", ["NATO"], ["West Germany and NATO"]),
    institution("United Nations", "The diplomatic body that repeatedly condemns annexations and eventually dissolves when no meaningful member system remains.", ["U.N.", "UN"], ["Campaign Hub"]),
    institution("NORAD", "The North American aerospace defense structure central to Canadian and U.S. warning and missile defense.", links=["United States of America", "Canada"]),
    institution("Strategic Air Command", "The U.S. nuclear air command placed on heightened alert during the Soviet nuclear crisis.", ["SAC"], ["United States of America"]),
    institution("United States Department of Defense", "The U.S. defense bureaucracy that designates the SR-91 Phantom Sky and manages advanced programs.", ["DoD", "Department of Defense"], ["SR-91 Phantom Sky", "United States of America"]),
    institution("Central Intelligence Agency", "The U.S. intelligence service tied to covert operations, Cuban destabilization, and broader alliance-era activity.", ["CIA"], ["United States of America"]),
    institution("KGB", "The Soviet intelligence service used for assassination plots, espionage, and crisis operations.", links=["Soviet Union", "Early Cold War Crisis"]),
    institution("Stasi", "The East German secret police that intensifies surveillance around Berlin Wall crossings.", ["East German Secret Police"], ["East Germany"]),
    institution("Department of Religion", "The L.E.T.F. institution that crowns and administers King Darius Morgan's religious authority.", links=["King Darius Morgan", "Morganism"], group="letf-state"),
    institution("Department of Music", "The L.E.T.F. office headed by Dave Bluntz and responsible for Bluntz Beats.", links=["Department of Music and Bluntz Beats"], group="ideology"),
    institution("Warsaw Pact", "The Soviet-aligned military sphere referenced by the Cold War setting and later shattered by Soviet collapse.", links=["Soviet Union", "Early Cold War Crisis"]),
    institution("Boombayah Anarchist Party", "The movement funded and armed during the classified coup against Madison's government.", ["Anarchist Party"], ["Boombayah", "Jaime Cuerbo"]),
    institution("Indian Forces", "The forces resisting L.E.T.F. invasion with Boombayah funding and advisory support.", links=["India", "Boombayah"]),
    institution("L.E.T.F. Generals", "The imperial command class responsible for repeated large-scale annexation planning.", links=["Lowest Egyptian Taper Fade"], group="letf-state"),
]


EQUIPMENT = [
    equipment("F-15 Eagle", "A U.S. air-superiority fighter used in early Cold War interception and later support roles.", ["F-15", "F-15s"]),
    equipment("F-14 Tomcat", "A U.S. Navy interceptor associated with AIM-54 Phoenix use in Operation Sky Shield.", ["F-14", "F-14s"]),
    equipment("F-16 Fighting Falcon", "A U.S. fighter used across multiple campaigns and later mentioned in final-war air combat.", ["F-16", "F-16s"]),
    equipment("F-16XL", "A prototype/advanced F-16 variant referenced during the Jordan campaign.", ["F-16XL prototypes"]),
    equipment("F-4 Phantom II", "A NATO and West German aircraft used against Soviet air operations near East Germany.", ["F-4 Phantom", "F-4 Phantoms"]),
    equipment("A-10 Thunderbolt II", "A U.S. ground-attack aircraft supporting NATO against Soviet mechanized formations.", ["A-10 Thunderbolt", "A-10 Thunderbolts"]),
    equipment("B-52 Stratofortress", "A U.S. strategic bomber used in the opening nuclear-alert posture.", ["B-52", "B-52 bombers"]),
    equipment("B-2 Spirit", "A final-war U.S. bomber reference that is anachronistic unless read as a prototype in this canon.", ["B-2", "B-2 Bombers"]),
    equipment("F-22 Raptor", "A final-war U.S. fighter reference that functions as a canon anachronism or advanced prototype.", ["F-22", "F-22 Raptors"]),
    equipment("A-12 Archangel", "A high-speed U.S. prototype aircraft launched during the final NATO-L.E.T.F. war.", ["A-12"]),
    equipment("YF-12", "A U.S. interceptor prototype referenced during the final-war air campaigns.", ["YF-12 prototype"]),
    equipment("SR-71 Blackbird", "A real reconnaissance aircraft used as a comparison point for the fictional SR-91 Phantom Sky.", ["SR-71"]),
    equipment("Dark Angel 12", "An experimental reconnaissance aircraft used in Operation Sky Shield.", links=["Operation Sky Shield"]),
    equipment("AWACS", "Airborne command-and-control aircraft coordinating interception and battlefield air operations.", ["Airborne Warning and Control System"]),
    equipment("AIM-54 Phoenix", "A long-range air-to-air missile carried by F-14 Tomcats in the Soviet crisis response.", ["Phoenix missiles"]),
    equipment("Tomahawk Cruise Missile", "A cruise missile used by U.S. submarines against Soviet launch sites.", ["Tomahawk cruise missiles"]),
    equipment("Ohio-Class Submarine", "A U.S. ballistic or cruise-missile submarine platform repeatedly positioned in strategic crises.", ["Ohio-class submarines"]),
    equipment("Los Angeles-Class Submarine", "A U.S. attack submarine used in North Korea-related naval operations.", ["Los Angeles-class submarines"]),
    equipment("P-3 Orion", "A U.S. maritime patrol aircraft used to monitor North Korean trade and naval routes.", ["P-3 Orion aircraft"]),
    equipment("M1 Abrams", "A U.S. main battle tank deployed in the Mexico invasion and other late-canon ground operations.", ["M1 Abrams tanks"]),
    equipment("AH-64 Apache", "A U.S. attack helicopter referenced in the Mexico invasion force.", ["Apache helicopters", "Apache"]),
    equipment("T-72 Tank", "A Soviet-designed tank used by the USSR and later heavily by the L.E.T.F.", ["T-72", "T-72 tanks"]),
    equipment("BMP-1 Infantry Fighting Vehicle", "A Soviet infantry fighting vehicle used throughout L.E.T.F. mechanized campaigns.", ["BMP-1", "BMP-1 vehicles"]),
    equipment("MiG-21", "A Soviet-designed fighter used by the USSR and L.E.T.F. air forces.", ["MiG-21s"]),
    equipment("Su-17", "A Soviet strike aircraft used in L.E.T.F. bombing operations.", ["Su-17", "Su-17s"]),
    equipment("Sukhoi Su-24", "A Soviet strike aircraft used by the L.E.T.F. in endgame operations.", ["Su-24", "Su-24s"]),
    equipment("Tu-95 Bear", "A Soviet nuclear-capable bomber mobilized during the self-destructive nuclear plan.", ["Tu-95", "Tu-95 Bear"]),
    equipment("Tu-22M Backfire", "A Soviet bomber used during the failed East Germany invasion.", ["Tu-22M", "Tu-22M bombers"]),
    equipment("Intercontinental Ballistic Missile", "Strategic nuclear missiles central to Soviet threats and final-war exchanges.", ["ICBM", "ICBMs"]),
    equipment("Tactical Nuclear Weapon", "Smaller nuclear weapons referenced in final-war battlefield strikes.", ["tactical nukes", "tactical nuclear weapons"]),
    equipment("Missile Defense Systems", "The radar and interceptor systems developed by the U.S. and NORAD through the crisis.", ["missile defenses", "anti-missile defense"]),
    equipment("Hypersonic Interceptors", "A U.S. research category enabled by the tripled defense budget.", ["hypersonic interceptors"]),
    equipment("Propaganda Aircraft", "Aircraft used by the L.E.T.F. to broadcast Morganist hymns and Bluntz Beats.", links=["Department of Music and Bluntz Beats"]),
    equipment("Fade Tanks", "The L.E.T.F.'s symbolic armored forces, often described as leading mass offensives.", ["Fade Tank"]),
    equipment("Ceremonial Loudspeakers", "Battlefield speaker systems mounted on vehicles and installations for Bluntz Beats.", ["loudspeakers", "speakers"], ["Department of Music and Bluntz Beats"]),
    equipment("Nuclear Silos", "Strategic missile-launch sites central to Soviet collapse and final-war targeting.", ["silos"]),
    equipment("Carrier Strike Group", "U.S. and L.E.T.F.-opposing naval formations used in blockades and amphibious defense.", ["carrier strike groups"]),
    equipment("Amphibious Assault Ship", "Naval platforms used to support invasions of islands, coastlines, and Madagascar.", ["amphibious assault ships"]),
    equipment("Military Drones", "Advanced drone references that become more common in later L.E.T.F. campaigns.", ["drones", "drone squadrons"]),
]


CONCEPTS = [
    concept("Silicon Mining Monopoly", "West Germany's exclusive silicon-mining technology, making it a strategic microelectronics chokepoint.", links=["West Germany and NATO"], group="technology"),
    concept("Tripled Defense Budget", "The United States' opening modifier and the source of many advanced research and deployment advantages.", links=["United States of America"], group="technology"),
    concept("Tax-Free Economy", "Canada's opening modifier before the War Preparedness Tax modifies the system.", links=["Canada"], group="faction"),
    concept("War Preparedness Tax", "The Canadian emergency tax created to fund defense despite the tax-free modifier.", links=["Canada", "February 1981 - Key Developments"], group="cold-war"),
    concept("Maple Tree Defense", "Canada's symbolic and military response to Soviet threats against maple trees.", links=["Canada", "March 1981 - Global Chaos Unfolds"], group="cold-war"),
    concept("Low Taper Fade Symbolism", "The haircut-centered visual language used in Soviet flag changes and later L.E.T.F. state identity.", links=["Lowest Egyptian Taper Fade"], group="ideology"),
    concept("Global Speaker Project", "The Soviet project to broadcast strange phrases across the world.", links=["Soviet Union", "Early Cold War Crisis"], group="cold-war"),
    concept("Cuban Crisis of 1981", "The crisis following Soviet annexation of Cuba and U.S. blockade planning.", links=["Cuba", "Early Cold War Crisis"], group="cold-war"),
    concept("Soviet Fragmentation", "The post-collapse condition of the USSR as rogue regions, failed states, separatists, and unclaimed territory.", links=["Soviet Union", "Former Soviet Territorial Campaigns"], group="cold-war"),
    concept("Unclaimed Territory", "A recurring map status after state collapse or before L.E.T.F. annexation.", links=["Timeline 1981-1989"], group="campaign"),
    concept("Resistance Movements", "Insurgent and guerrilla groups that form in annexed territories across the canon.", links=["Campaign Hub"], group="campaign"),
    concept("International Sanctions", "Sanctions imposed against the USSR, North Korea, L.E.T.F., and the United States at different stages.", ["Sanctions"], ["United Nations"], group="campaign"),
    concept("Free Water Program", "The U.S.-L.E.T.F. effort to bribe Mexican civilians with free and good water during the Mexico invasion.", links=["Mexico", "Americas Campaigns"], group="campaign"),
    concept("Equal Rights Modifier", "Madison/Brazil's country ability and ideological foundation before the Boombayah rebrand.", links=["Boombayah"], group="faction"),
    concept("Classified Coup", "The unidentified-force operation to destabilize Boombayah by funding anarchists.", links=["Boombayah", "Jaime Cuerbo"], group="campaign"),
    concept("Martial Law in Boombayah", "Madison's emergency response to anarchist uprisings and destabilization.", links=["Boombayah"], group="campaign"),
    concept("Morganist Shrines", "Religious installations used to convert annexed spaces into Morganist imperial territory.", links=["Morganism", "Pantheon of Morganism"], group="ideology"),
    concept("Spiritual Protectorate", "The status applied to Newport County under L.E.T.F. control.", links=["Newport County", "Lowest Egyptian Taper Fade"], group="letf-state"),
    concept("Chrono-Fade Life Prolonger", "The fictional life-extension machine used to prolong Hitler's rule in the L.E.T.F.", links=["Adolf Hitler in the Country Game", "Necrocracy"], group="technology"),
    concept("Battlefield Worship", "The L.E.T.F. practice of praying to the Morganist pantheon before combat.", links=["Morganism", "Department of Music and Bluntz Beats"], group="ideology"),
    concept("Fade's Crown", "The renamed or reconstructed capital-symbol site associated with former Kaliningrad and L.E.T.F. endgame capitals.", links=["Kaliningrad", "L.E.T.F. Final Global Conquest"], group="letf-state"),
    concept("Sacred Southern Province", "The L.E.T.F. province name applied to annexed Israel.", links=["Israel", "Middle Eastern Expansion"], group="letf-state"),
    concept("Euphrates Province of the Fade", "The L.E.T.F. province name applied to annexed Iraq.", links=["Iraq", "Operation Euphrates Fade"], group="letf-state"),
    concept("Levantine Province of the Fade", "The L.E.T.F. province name applied to annexed Syria.", links=["Syria", "Operation Crescent Fade"], group="letf-state"),
    concept("Anatolian Province of the Fade", "The L.E.T.F. province name applied to annexed Turkey.", links=["Turkey", "Operation Crescent Fade"], group="letf-state"),
    concept("West African Province of the Fade", "The L.E.T.F. province created from Nigeria and nearby West African campaigns.", links=["Nigeria", "Operation Sahara Fade"], group="letf-state"),
    concept("Great Steppe Province of the Fade", "The L.E.T.F. province name applied to annexed Mongolia.", links=["Mongolia", "Operation Eternal Steppe"], group="letf-state"),
    concept("Northern Province of the Fade", "The L.E.T.F. province name planned for annexed Canada.", links=["Canada", "Operation Maple Fade"], group="letf-state"),
    concept("Eastern European Province of the Fade", "A recurring province designation for L.E.T.F.-occupied Poland, Kaliningrad, and East Germany.", links=["European Campaigns"], group="letf-state"),
    concept("Caribbean Province of the Fade", "The L.E.T.F. province for conquered Caribbean nations.", links=["Operation Island Fade"], group="letf-state"),
    concept("Southern Hemisphere Province of the Fade", "The L.E.T.F. province for much of its 1989 South American conquests.", links=["Operation Andean Fade"], group="letf-state"),
    concept("Greater Middle Eastern Province of the Fade", "The province concept for the 1989 remaining Middle East campaign.", links=["Operation Desert Fade"], group="letf-state"),
    concept("Southern European Province of the Fade", "The province concept used for Italy, Vatican City, Greece, Malta, and Balkan territories.", links=["European Campaigns"], group="letf-state"),
    concept("Northern European Province of the Fade", "The province concept for Finland and Northern Dominion territories.", links=["European Campaigns"], group="letf-state"),
    concept("Iberian Province of the Fade", "The L.E.T.F. province for Spain and Portugal.", links=["Operation Iberian Fade"], group="letf-state"),
    concept("Maghreb Province of the Fade", "The L.E.T.F. province for Algeria and Tunisia.", links=["Operation Maghreb Fade"], group="letf-state"),
    concept("Polar Provinces of the Fade", "The L.E.T.F. province concept for Arctic and Antarctic claims.", links=["Operation Polar Fade"], group="letf-state"),
    concept("African Province of the Fade", "The final unified African province after Operation Eternal Fade.", links=["L.E.T.F. Final Global Conquest"], group="letf-state"),
    concept("Nordic Province of the Fade", "The province name applied to Denmark after Operation Nordic Breakpoint.", links=["Denmark", "Final NATO LETF War"], group="letf-state"),
    concept("Western European Province of the Fade", "The province name applied to France and later West Germany in endgame Europe.", links=["European Campaigns", "Final NATO LETF War"], group="letf-state"),
]


def all_specs() -> list[dict]:
    specs = TERRITORIES + OPERATIONS + PEOPLE + INSTITUTIONS + EQUIPMENT + CONCEPTS
    seen: set[str] = set()
    unique: list[dict] = []
    for item in specs:
        if item["title"] in seen:
            continue
        seen.add(item["title"])
        unique.append(item)
    return unique


def alias_patterns(item: dict) -> list[str]:
    values = [item["title"], *item.get("aliases", [])]
    return [clean_ascii(v) for v in values if clean_ascii(v)]


def mentioned(text: str, item: dict) -> bool:
    hay = clean_ascii(text).lower()
    for alias in alias_patterns(item):
        needle = alias.lower()
        if len(needle) <= 3:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(needle)}(?![A-Za-z0-9])", hay):
                return True
        elif needle in hay:
            return True
    return False


def event_notes() -> list[Path]:
    return sorted((VAULT / "07 Timeline").glob("* Event Articles/*.md"))


def note_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("title: "):
            return line.split(":", 1)[1].strip().strip('"')
    return path.stem


def related_event_links(item: dict, limit: int = 12) -> list[str]:
    matches: list[str] = []
    for path in event_notes():
        if mentioned(path.read_text(encoding="utf-8"), item):
            matches.append(f"- {link(path.stem, note_title(path))}")
    return matches[:limit]


def source_snippets(item: dict, limit: int = 4) -> list[str]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    snippets: list[str] = []
    for idx, raw in enumerate(lines):
        line = clean_ascii(raw)
        if not line or line.startswith("--- PAGE "):
            continue
        if not mentioned(line, item):
            continue
        start = max(0, idx - 1)
        end = min(len(lines), idx + 3)
        chunk = " ".join(clean_ascii(x) for x in lines[start:end] if clean_ascii(x) and not clean_ascii(x).startswith("--- PAGE "))
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if chunk and chunk not in snippets:
            snippets.append(chunk[:420])
        if len(snippets) >= limit:
            break
    return snippets


def node_body(item: dict) -> str:
    related = [x for x in item.get("links", []) if x != item["title"]]
    related_lines = "\n".join(f"- {link(x)}" for x in related) or "- No curated related links"
    event_lines = "\n".join(related_event_links(item)) or "- No direct dated event mention found in generated event pages"
    snippets = source_snippets(item)
    snippet_lines = "\n".join(f"- {snippet}" for snippet in snippets) or "- No direct source snippet found; this node is included for map completeness and graph organization."
    alias_text = ", ".join(clean_ascii(a) for a in item.get("aliases", [])) or "No aliases"
    return f"""
## Lead

{item['title']} is a granular wiki node generated from the Country Game PDF so the Obsidian graph can represent smaller pieces of the canon.

## Canon Role

{item['role']}

## Aliases

{alias_text}

## Related Nodes

{related_lines}

## Mentioned In

{event_lines}

## Source Snippets

{snippet_lines}

## Graph Function

This page is intentionally small and link-heavy. It exists to split a large article into a more navigable graph node and to connect places, operations, people, equipment, institutions, and concepts back to the major wiki articles.
"""


def write_micro_notes(specs: list[dict]) -> None:
    for item in specs:
        write_note(item["folder"], item["title"], item["group"], item["kind"], node_body(item), item.get("aliases", []))


def write_micro_indexes(specs: list[dict]) -> None:
    collections = [
        ("Granular Node Index", "atlas", "All expanded small nodes", specs),
        ("Country and Territory Index", "faction", "Countries, territories, regions, and strategic places", [x for x in specs if x["kind"] == "territory"]),
        ("Operation Index Expanded", "campaign", "Named operation nodes", [x for x in specs if x["kind"] == "operation"]),
        ("People and Leaders Index", "faction", "Player-associated people, leaders, commanders, and sacred figures", [x for x in specs if x["kind"] == "person"]),
        ("Institutions and Alliances Index", "faction", "Organizations, alliances, ministries, and intelligence services", [x for x in specs if x["kind"] == "institution"]),
        ("Technology and Equipment Index Expanded", "technology", "Equipment, vehicles, aircraft, weapons, and research programs", [x for x in specs if x["kind"] == "equipment"]),
        ("Concepts and Provinces Index", "letf-state", "Modifiers, ideas, symbolic systems, and province names", [x for x in specs if x["kind"] == "concept"]),
    ]
    for title, group, lead, items in collections:
        lines = [f"## Lead\n\n{lead}. This index was generated for graph density and navigation.\n", "## Nodes\n"]
        for item in sorted(items, key=lambda x: x["title"]):
            lines.append(f"- {link(item['title'])}")
        write_note("00 Atlas/Expanded Indexes", title, group, "index", "\n".join(lines), aliases=[])


def patch_event_pages(specs: list[dict]) -> None:
    for path in event_notes():
        text = path.read_text(encoding="utf-8")
        matches = [item for item in specs if mentioned(text, item)]
        if not matches:
            continue
        matches = sorted(matches, key=lambda item: (item["kind"], item["title"]))[:60]
        lines = ["## Granular Node Links\n"]
        by_kind: dict[str, list[dict]] = {}
        for item in matches:
            by_kind.setdefault(item["kind"], []).append(item)
        for kind in ["territory", "operation", "person", "institution", "equipment", "concept"]:
            items = by_kind.get(kind, [])
            if not items:
                continue
            label = kind.replace("_", " ").title()
            lines.append(f"### {label}")
            lines.extend(f"- {link(item['title'])}" for item in items)
            lines.append("")
        block = "\n".join(lines).strip() + "\n\n"
        text = re.sub(r"\n## Granular Node Links\n.*?(?=\n## Notes|\Z)", "\n", text, flags=re.S)
        if "\n## Notes" in text:
            text = text.replace("\n## Notes", f"\n{block}## Notes", 1)
        else:
            text = text.rstrip() + "\n\n" + block
        path.write_text(text, encoding="utf-8", newline="\n")


def patch_atlas_links() -> None:
    atlas_path = VAULT / "00 Atlas" / "Country Game 1981-1989 Atlas.md"
    if atlas_path.exists():
        text = atlas_path.read_text(encoding="utf-8")
        if "[[Granular Node Index]]" not in text:
            text = text.replace(
                "- [[Canon Index]] lists the major synthesized articles.",
                "- [[Canon Index]] lists the major synthesized articles.\n- [[Granular Node Index]] lists the expanded small-node layer.",
            )
            atlas_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    specs = all_specs()
    write_micro_notes(specs)
    write_micro_indexes(specs)
    patch_event_pages(specs)
    patch_atlas_links()
    print(f"Wrote {len(specs)} granular node notes")
    print("Patched event pages with granular node links")


if __name__ == "__main__":
    main()
