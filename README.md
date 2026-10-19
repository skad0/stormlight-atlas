# Stormlight Atlas

A static reference application for the published **Stormlight Archive**. The application provides a searchable encyclopedia, event chronology, chapter navigation, schematic maps, relationship views, and a character status ledger.

The dataset contains **494 entities**, **190 event anchors**, **145 explicit relationship records**, and **671 indexed sections**. Its editorial cutoff is **October 16, 2026**. The default spoiler boundary is the end of *Oathbringer*.

**Spoilers:** source files contain material through the end of *Wind and Truth*. The application filters its interface by completed book. Browsing the repository or external source pages bypasses that filtering.

## Scope

| Work | Identifier | Indexed sections | Coverage |
| --- | --- | ---: | --- |
| The Way of Kings | `TWoK` | 87 | Major arcs, entity records, chapter and interlude index |
| Words of Radiance | `WoR` | 105 | Major arcs, entity records, chapter and interlude index |
| Edgedancer | `ED` | 21 | Novella arcs and section index |
| Oathbringer | `OB` | 138 | Major arcs, entity records, chapter and interlude index |
| Dawnshard | `DS` | 21 | Expedition arcs and section index |
| Rhythm of War | `ROW` | 131 | Major arcs, entity records, chapter and interlude index |
| Wind and Truth | `WAT` | 168 | Selected major events, outcomes, and complete section index |
| Elsecaller | `EC` | Whole-story reference | Five event anchors; page and card locators unavailable |
| King Lopen the First of Alethkar | `KL` | Whole-story reference | Six event anchors; page and card locators unavailable |

Indexed sections include numbered chapters and applicable preludes, prologues, interludes, epilogues, and postludes. An index entry does not imply that every scene or entity mention has been annotated. Connected Cosmere works are cataloged for context; they do not have complete plot coverage. Unpublished works and noncanonical drafts are outside the dataset.

See [Coverage](docs/COVERAGE.md) for exact counts and limitations and [Sources](SOURCES.md) for the full source register.

## Features

- Entity views for characters, locations, factions, items, and magic.
- Completed-book spoiler boundaries applied to profiles, search, events, connections, and map routes.
- Book, entity-type, text, relationship-type, and map-realm filters.
- Event ordering by approximate in-world position or book and chapter reveal order.
- Section navigation, linked event anchors, and reading progress.
- Schematic location plots with character route anchors.
- Explicit relationships distinguished from derived profile associations.
- A status ledger showing each character's last recorded status at the selected boundary.
- Browser-local bookmarks, notes, and JSON backup import and export.
- Source provenance, confidence labels, and editorial coverage notes.

## Requirements

| Component | Requirement | Purpose |
| --- | --- | --- |
| Node.js | 22 or later | ES-module validation and application rendering checks |
| Python | 3.10 or later, available as `python3` | Dataset generation, documentation generation, and local HTTP serving |
| Browser | A modern browser with JavaScript modules, Fetch, and Web Storage | Application runtime |

The project has **no third-party runtime or build dependencies**. An `npm install` step is not required. The `private` package field prevents accidental npm package publication; it does not control repository or website visibility.

## Quick start

From the repository root:

```sh
npm run build
npm run check
npm test
npm run dev
```

Open **http://127.0.0.1:8080/**. Stop the local server with `Ctrl+C`.

The application must be served over HTTP. Opening `dist/index.html` through `file://` is unsupported because the application loads ES modules and JSON with Fetch.

Without npm, the equivalent commands are:

```sh
python3 scripts/build-data.py
node --check dist/app.js
node --check dist/model.js
node scripts/validate.mjs
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

## Deployment

Publish the contents of **`dist/`** to a static HTTP host. No application server, database, API key, or environment variable is required. Asset and dataset URLs are relative to the application, so the export can run at a domain root or under a repository subpath.

The host must serve `.js` files as JavaScript and `.json` files as JSON. Navigation uses URL fragments and does not require server-side route rewrites.

This repository does not enable website hosting automatically. Authentication and access restrictions, if required, must be provided by the hosting platform. The export contains no credentials, hosted-site identifiers, or access policy from the original deployment.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `dist/index.html` | Application shell and accessible navigation |
| `dist/style.css` | Responsive presentation and map/graph styling |
| `dist/app.js` | Rendering, URL-fragment routing, interaction handlers, and browser persistence |
| `dist/model.js` | Profile projection, spoiler filtering, search, relationship derivation, and route anchors |
| `dist/data.json` | Generated, checked-in runtime dataset |
| `source-data/` | Preserved reference snapshots, audit corrections, missing section records, and research additions |
| `scripts/build-data.py` | Source reconciliation and runtime dataset generation |
| `scripts/validate.mjs` | Structural, spoiler-boundary, renderer, link, and persistence checks |
| `scripts/generate-reference-docs.py` | Coverage and source-register generation |
| `validation.json` | Most recent validation report generated in this checkout |
| `docs/` | Architecture, data model, spoiler logic, development, and coverage documentation |

HTML, JavaScript, and CSS are maintained directly in `dist/`; only `dist/data.json` is generated. There is no bundler or transpilation step.

## Application logic

The build preserves the earlier *Oathbringer* and *Rhythm of War* reference snapshots, applies audited corrections, and appends sourced *Wind and Truth* and short-story records. Entities use type-qualified keys, such as `character:rysn` and `faction:rysn`, to avoid identifier collisions.

At runtime, the model selects the latest profile snapshot allowed by the completed-book boundary. Dated status facts and event anchors have separate reveal thresholds. Search and connections use the same projected records as the interface. Later snapshots are not substituted into earlier summaries.

The chronology uses approximate editorial positions. It does not calculate canonical Rosharan dates. Map coordinates are schematic; route lines connect recorded event anchors and omit unrecorded travel.

Detailed specifications:

- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Spoiler model](docs/SPOILER_MODEL.md)
- [Development and validation](docs/DEVELOPMENT.md)

## Validation

Run `npm test` after rebuilding the dataset. The validator checks unique identifiers, typed references, source references for event records, section counts, chapter anchors, spoiler transitions, generated links, application templates, bookmarks, and reading progress.

The initial exported baseline passed **1,435 rendered view/detail cases** and **22,256 link checks**. These counters include checks repeated across spoiler boundaries; they are not counts of distinct routes or distinct graph edges.

The renderer is exercised in a minimal DOM harness. This does **not** verify browser layout, accessibility behavior, real navigation events, or end-to-end deployment behavior. A real-browser visual review was unavailable for the initial baseline. Structural validation does not establish complete literary accuracy or prove that every possible spoiler has been excluded.

## Data and source policy

The dataset combines original reference snapshots, original paraphrases, official bibliography and chronology material, publisher-hosted reread commentary, and community reference indexes. Source entries identify their roles. Inherited claims are not represented as newly verified claims.

Source pages may contain unrestricted spoilers. Page availability and content may change after the editorial cutoff. The repository does not include novel text or official map artwork.

See [Sources](SOURCES.md), [Source data](source-data/README.md), and [Notice](NOTICE.md).

## Contributing

See [Contributing](CONTRIBUTING.md) for data-change requirements, documentation conventions, and validation steps. Write documentation, comments, issue descriptions, and commit messages in consistent technical English.

## License

Original software and technical documentation are available under the [MIT License](LICENSE). Narrative reference data and third-party intellectual property are excluded from that license. See [Notice](NOTICE.md) for the scope and attribution statement.
