# Source Data

This directory contains the editorial inputs used to build `dist/data.json`. The source files contain unrestricted narrative spoilers.

| File | Origin | Role |
| --- | --- | --- |
| `oathbringer.json` | Earlier reference snapshot dated August 21, 2026 | Preserves the original through-*Oathbringer* profile state |
| `rhythm-of-war.json` | Expanded reference snapshot dated October 5, 2026 | Provides through-*Rhythm of War* profiles, inherited anchors, relationships, and chapter records |
| `reference-audit.json` | Bounded structural and selected factual audit dated October 16, 2026 | Records corrections, duplicate-edge findings, ID collisions, and chronology limitations |
| `missing-chapters.json` | Interlude-index extension from the audit | Adds 9 `TWoK`, 14 `WoR`, and 14 `OB` interludes |
| `wind-and-truth.json` | Research supplement dated October 16, 2026 | Adds selected *Wind and Truth* outcomes and both Story Deck short stories |

The original HTML references were converted to JSON before the application was exported. These JSON snapshots are sufficient to rebuild the runtime dataset; the original HTML files are not required.

The original snapshots include historical metadata and generated graph arrays. The build retains profile snapshots but derives runtime associations from typed entity fields instead of copying every historical generated edge.

The audit is not a complete factual review of the novels. Preserved provenance describes when a source was used; it does not imply that every inherited claim was independently verified during the export. See the [source register](../SOURCES.md) and [coverage report](../docs/COVERAGE.md).

Edit source files with UTF-8 encoding and valid JSON. Add explicit sources, locators, reveal thresholds, and uncertainty qualifications for new claims. Regenerate runtime data and reference documentation after editing.
