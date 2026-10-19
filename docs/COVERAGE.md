# Coverage

Generated from `dist/data.json` by `scripts/generate-reference-docs.py`.

Editorial cutoff: **2026-10-16**. This is a curated reference, not a complete scene or mention concordance.

## Published work coverage

| Work | ID | Numbered chapters | Interludes | Other sections | Total sections | Sections with event anchors | Direct event anchors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| The Way of Kings | `TWoK` | 75 | 9 | 3 | 87 | 49 | 22 |
| Words of Radiance | `WoR` | 89 | 14 | 2 | 105 | 62 | 18 |
| Edgedancer | `ED` | 20 | 0 | 1 | 21 | 21 | 4 |
| Oathbringer | `OB` | 122 | 14 | 2 | 138 | 96 | 40 |
| Dawnshard | `DS` | 19 | 0 | 2 | 21 | 17 | 9 |
| Rhythm of War | `ROW` | 117 | 12 | 2 | 131 | 33 | 30 |
| Wind and Truth | `WAT` | 147 | 18 | 3 | 168 | 41 | 50 |
| Elsecaller | `EC` | — | — | — | Whole-story reference | — | 5 |
| King Lopen the First of Alethkar | `KL` | — | — | — | Whole-story reference | — | 6 |

There are **6 additional historical or composite-book event anchors**. Direct event counts exclude these shared records. A chapter can link to several events, and an event can link to several chapters.

## Entity and relationship coverage

| Record type | Count |
| --- | ---: |
| Character | 209 |
| Faction | 91 |
| Location | 69 |
| Magic | 72 |
| Item | 53 |
| Total entities | 494 |
| Event anchors | 190 |
| Explicit relationships | 145 |
| Indexed sections | 671 |
| Source-register entries | 58 |
| Unique URLs in the runtime bibliography | 57 |

Entity counts include reference notes, group placeholders, spren, and connected-Cosmere records. They are not counts of distinct human characters. Explicit relationships exclude runtime associations generated from profile fields.

## Reconciliation coverage

- The original through-Oathbringer and through-Rhythm-of-War profile snapshots are retained separately.
- The audit adds 37 interludes: 9 in TWoK, 14 in WoR, and 14 in OB.
- Selected dates, chapter locators, and entity-type references are corrected during the build.
- Historical generated graph edges are replaced by explicit relationships and derived profile associations in the runtime model.
- The Wind and Truth extension adds 50 curated events, 41 character status updates, 9 relationships, and selected magic, item, and faction updates.
- Elsecaller and King Lopen add 11 curated event anchors in total.

## Known limitations

- Complete section indexing does not mean that every section has a scene-specific summary or event anchor.
- Many inherited summaries describe an arc spanning several chapters. They are labeled as context, not exact chapter recaps.
- Wind and Truth uses generic numbered chapter labels where chapter titles were not verified.
- Short-story page numbers and Story Deck card locators were not verified.
- Inherited source attribution does not establish a fresh independent check of every narrative claim.
- Cross-viewpoint chronology, historical placement, and Spiritual Realm time are not a canonical timestamp model.
- Schematic coordinates and route anchors do not provide precise map geometry or complete travel paths.
- Connected Cosmere books have catalog and connection coverage rather than full plot coverage.
- Unpublished works, including Horneater and planned later Stormlight novels, have no invented story data.
- A complete literary fact check, semantic spoiler audit, and real-browser visual review have not been completed.

See [Sources](../SOURCES.md), [Data Model](DATA_MODEL.md), and [Spoiler Model](SPOILER_MODEL.md).
