"""Generate coverage and provenance documentation from local reference inputs."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "dist/data.json").read_text(encoding="utf-8"))


def cell(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_coverage():
    rows = [
        "# Coverage",
        "",
        "Generated from `dist/data.json` by `scripts/generate-reference-docs.py`.",
        "",
        f"Editorial cutoff: **{DATA['meta']['date']}**. This is a curated reference, not a complete scene or mention concordance.",
        "",
        "## Published work coverage",
        "",
        "| Work | ID | Numbered chapters | Interludes | Other sections | Total sections | Sections with event anchors | Direct event anchors |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for book in DATA["books"]:
        chapters = [c for c in DATA["chapters"] if c["book"] == book["abbr"]]
        interludes = sum(bool(re.match(r"^(?:Interlude\b|I-\d)", c["label"])) for c in chapters)
        numbered = sum(c["number"] > 0 and int(c["number"]) == c["number"] and bool(re.match(r"^(?:Chapter|Ch\.)\s*\d", c["label"])) for c in chapters)
        # Earlier snapshots use labels such as "1 · Stormblessed" rather than a uniform prefix.
        if book["abbr"] in {"TWoK", "WoR", "ED", "OB", "DS", "ROW"}:
            expected = {"TWoK": 75, "WoR": 89, "ED": 20, "OB": 122, "DS": 19, "ROW": 117}
            numbered = sum(any(c["number"] == n for c in chapters) for n in range(1, expected[book["abbr"]] + 1))
        others = len(chapters) - numbered - interludes
        anchored = sum(bool(c.get("anchors")) for c in chapters)
        direct = sum(e.get("book") == book["abbr"] for e in DATA["events"])
        rows.append(f"| {cell(book['title'])} | `{book['abbr']}` | {numbered} | {interludes} | {others} | {len(chapters)} | {anchored} | {direct} |")
    for story in DATA["supplements"]:
        rows.append(f"| {cell(story['title'])} | `{story['abbr']}` | — | — | — | Whole-story reference | — | {len(story.get('events', []))} |")
    shared = sum(e.get("book") is None or "/" in str(e.get("book")) for e in DATA["events"])
    rows += [
        "",
        f"There are **{shared} additional historical or composite-book event anchors**. Direct event counts exclude these shared records. A chapter can link to several events, and an event can link to several chapters.",
        "",
        "## Entity and relationship coverage",
        "",
        "| Record type | Count |",
        "| --- | ---: |",
    ]
    for kind, count in Counter(e["type"] for e in DATA["entities"]).items():
        rows.append(f"| {kind.capitalize()} | {count} |")
    rows += [
        f"| Total entities | {len(DATA['entities'])} |",
        f"| Event anchors | {len(DATA['events'])} |",
        f"| Explicit relationships | {len(DATA['relations'])} |",
        f"| Indexed sections | {len(DATA['chapters'])} |",
        f"| Source-register entries | {len(DATA['sources'])} |",
        f"| Unique URLs in the runtime bibliography | {len(set(s['url'] for s in DATA['sources']))} |",
        "",
        "Entity counts include reference notes, group placeholders, spren, and connected-Cosmere records. They are not counts of distinct human characters. Explicit relationships exclude runtime associations generated from profile fields.",
        "",
        "## Reconciliation coverage",
        "",
        "- The original through-Oathbringer and through-Rhythm-of-War profile snapshots are retained separately.",
        "- The audit adds 37 interludes: 9 in TWoK, 14 in WoR, and 14 in OB.",
        "- Selected dates, chapter locators, and entity-type references are corrected during the build.",
        "- Historical generated graph edges are replaced by explicit relationships and derived profile associations in the runtime model.",
        "- The Wind and Truth extension adds 50 curated events, 41 character status updates, 9 relationships, and selected magic, item, and faction updates.",
        "- Elsecaller and King Lopen add 11 curated event anchors in total.",
        "",
        "## Known limitations",
        "",
        "- Complete section indexing does not mean that every section has a scene-specific summary or event anchor.",
        "- Many inherited summaries describe an arc spanning several chapters. They are labeled as context, not exact chapter recaps.",
        "- Wind and Truth uses generic numbered chapter labels where chapter titles were not verified.",
        "- Short-story page numbers and Story Deck card locators were not verified.",
        "- Inherited source attribution does not establish a fresh independent check of every narrative claim.",
        "- Cross-viewpoint chronology, historical placement, and Spiritual Realm time are not a canonical timestamp model.",
        "- Schematic coordinates and route anchors do not provide precise map geometry or complete travel paths.",
        "- Connected Cosmere books have catalog and connection coverage rather than full plot coverage.",
        "- Unpublished works, including Horneater and planned later Stormlight novels, have no invented story data.",
        "- A complete literary fact check, semantic spoiler audit, and real-browser visual review have not been completed.",
        "",
        "See [Sources](../SOURCES.md), [Data Model](DATA_MODEL.md), and [Spoiler Model](SPOILER_MODEL.md).",
        "",
    ]
    (ROOT / "docs/COVERAGE.md").write_text("\n".join(rows), encoding="utf-8")


def collect_urls(value, urls):
    if isinstance(value, dict):
        for child in value.values():
            collect_urls(child, urls)
    elif isinstance(value, list):
        for child in value:
            collect_urls(child, urls)
    elif isinstance(value, str) and re.match(r"^https?://\S+$", value):
        urls.add(value)


def write_sources():
    inherited = json.loads((ROOT / "source-data/rhythm-of-war.json").read_text(encoding="utf-8"))["sources"]
    additions = json.loads((ROOT / "source-data/wind-and-truth.json").read_text(encoding="utf-8"))["sources"]
    inherited_urls = {s["url"] for s in inherited}
    addition_urls = {s["url"] for s in additions}
    grouped = {}
    for source in DATA["sources"]:
        grouped.setdefault(source["url"], []).append(source)
    rows = [
        "# Sources",
        "",
        "Generated from the runtime bibliography and local source-data files. This document contains links whose titles or destinations may reveal later-book information.",
        "",
        f"The runtime bibliography contains **{len(DATA['sources'])} entries referencing {len(grouped)} unique URLs**. Duplicate URLs are grouped below. The editorial cutoff is **{DATA['meta']['date']}**.",
        "",
        "## Source roles",
        "",
        "| Category | Supported use | Limitation |",
        "| --- | --- | --- |",
        "| Official author and publisher pages | Publication scope, official premises, chronology methods, and available primary excerpts | A marketing page does not verify every plot outcome |",
        "| Publisher-hosted reread commentary | Chapter locators and secondary discussion of events | Commentary is distinct from the novel text; hosting does not make every interpretation primary evidence |",
        "| Coppermind community references | Chapter indexes, entity facts, and cross-checks | Community-maintained secondary material can change or contain errors |",
        "| 17th Shard maps and timeline research | Geographic context, interaction references, and inferred chronology | Inferred alignment and schematic coordinates are not official exact dates or map geometry |",
        "| Preserved local reference snapshots | Reconciliation and historical profile versions | Not all inherited claims were independently rechecked |",
        "",
        "A source listed as inherited was retained from the through-Rhythm-of-War reference. An extension source was introduced by the October 16, 2026 research supplement. Presence in this register does not mean the page was fetched again for the public repository export. Dates and quality labels inside the source JSON describe the earlier research snapshot.",
        "",
        "## Runtime bibliography",
        "",
        "| Source | Identifier(s) | Classification | Origin | Recorded purpose |",
        "| --- | --- | --- | --- | --- |",
    ]
    for url, entries in grouped.items():
        first = entries[0]
        ids = ", ".join(f"`{s['id']}`" for s in entries if s.get("id")) or "Legacy entry without stable ID"
        origin = "Inherited + extension" if url in inherited_urls and url in addition_urls else "Extension" if url in addition_urls else "Inherited"
        purposes = list(dict.fromkeys(s.get("use") or s.get("note") or "Supports records in the research supplement; see source IDs in source-data/wind-and-truth.json." for s in entries))
        classification = "; ".join(dict.fromkeys(s.get("type") or s.get("quality") or "Reference" for s in entries))
        rows.append(f"| [{cell(first['title'])}]({url}) | {ids} | {cell(classification)} | {origin} | {cell(' '.join(purposes))} |")
    rows += [
        "",
        "## Additional audit and locator URLs",
        "",
        "The following URLs occur in the preserved source inputs but are not separate entries in the runtime bibliography. They include correction-specific chapter references and index pages.",
        "",
        "| URL | Source input(s) |",
        "| --- | --- |",
    ]
    origins = {}
    for file in sorted((ROOT / "source-data").glob("*.json")):
        urls = set()
        collect_urls(json.loads(file.read_text(encoding="utf-8")), urls)
        for url in urls - set(grouped):
            origins.setdefault(url, []).append(file.name)
    for url, files in sorted(origins.items()):
        rows.append(f"| <{url}> | {', '.join('`' + name + '`' for name in files)} |")
    rows += [
        "",
        "## Claim-level provenance",
        "",
        "- New research records use stable source IDs where supplied. These IDs resolve through the runtime bibliography.",
        "- Selected inherited corrections attach a source URL directly to the corrected event.",
        "- Many inherited records retain chapter or range labels without an independently verified claim-level source link.",
        "- A whole-story or chapter-range locator is not a verified page number or exact scene location.",
        "- Confidence labels and explicit inference qualifiers must remain attached to their claims.",
        "- No book text or official map artwork is reproduced by the source register.",
        "",
        "For data origins, see [Source Data](source-data/README.md). For coverage limitations, see [Coverage](docs/COVERAGE.md). For rights and license scope, see [Notice](NOTICE.md).",
        "",
    ]
    (ROOT / "SOURCES.md").write_text("\n".join(rows), encoding="utf-8")


write_coverage()
write_sources()
print("Generated docs/COVERAGE.md and SOURCES.md.")
