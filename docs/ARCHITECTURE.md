# Architecture

## System boundary

Stormlight Atlas is a static browser application with an offline data-generation pipeline. The application does not call external APIs, use a database, or synchronize user state to a server. External source links open the referenced websites.

| Layer | Implementation | Inputs | Outputs |
| --- | --- | --- | --- |
| Reference inputs | JSON files in `source-data/` | Preserved snapshots, audit corrections, research additions | Editorial records |
| Build pipeline | Python standard library | Editorial records | `dist/data.json` |
| Domain model | Browser-compatible JavaScript module | Dataset and selected spoiler boundary | Projected profiles, events, search results, connections, route anchors |
| Presentation | HTML, CSS, JavaScript templates | Model projections and UI state | Application views and detail panels |
| Persistence | Browser `localStorage` | User changes | Stored boundary, read sections, bookmarks, notes |
| Validation | Node.js standard library and minimal DOM harness | Runtime dataset and actual application modules | Assertions and `validation.json` |

## Build pipeline

`scripts/build-data.py` performs the following operations in order:

1. Load the original *Oathbringer* and *Rhythm of War* snapshots.
2. Apply selected audit corrections to source records in memory.
3. Convert source collections into type-qualified entity records and retain profile versions at scopes `4` and `6`.
4. Convert inherited status positions into reveal thresholds. Historical negative positions use the snapshot scope.
5. Copy event anchors and explicit relationships, assigning reveal thresholds and provenance labels.
6. Copy chapter records, add 37 missing early-book interludes, and apply selected anchor corrections.
7. Append *Wind and Truth* entities, facts, relationships, event anchors, and section records.
8. Append *Elsecaller* and *King Lopen* references at the `WoR` boundary.
9. Construct source metadata and normalize selected event references to their correct entity collection.
10. Write the runtime dataset and print its aggregate counts.

The pipeline does not rewrite the preserved source snapshots. It does not fetch sources during a build. A build requires no network access.

`npm test` subsequently writes validation metadata into `dist/data.json` and writes the detailed report to `validation.json`. Build and validation therefore form the complete preparation sequence.

## Domain model

`createModel(data, gate)` in `dist/model.js` initializes lookup maps for entities, events, and chapters. Profile and connection projections are cached by the current model instance. Assigning a new `model.gate` clears both caches.

| Method | Responsibility |
| --- | --- |
| `profile(key)` | Select a permitted profile snapshot, filter facts, determine visibility, and project display fields |
| `list(type, query, book)` | Filter and sort visible entity projections |
| `events()` | Return events whose reveal threshold does not exceed the active boundary |
| `search(query)` | Search permitted entity fields, visible events, and permitted chapter context |
| `resolve(id, type)` | Prefer an explicit type; otherwise resolve using the documented type order |
| `connections(key)` | Combine explicit relationships with forward and reverse profile associations |
| `routePoints(id, plane)` | Select nonhistorical event locations and collapse consecutive repeated locations |

The resolver falls back in this order: `character`, `location`, `faction`, `item`, `magic`. References should provide an explicit type whenever possible. A fallback resolution is an implementation convenience, not proof that an untyped reference is unambiguous.

## Relationship derivation

Explicit relationship records are filtered by reveal threshold. The model also derives associations from `factions`, `members`, `locations`, `owners`, `users`, and `related` fields of permitted full profiles. Reverse associations are included.

Each connection is deduplicated by target key, relationship kind, and label. The generated view distinguishes explicit book-scoped relationships from profile associations. A profile association does not establish a current allegiance, current ownership, or an exact temporal interval. Legacy relationship `from`, `to`, and `status` metadata are retained where present but are not used as an active-at-date query engine.

## Routing

The application uses URL-fragment routing:

| Route | Result |
| --- | --- |
| `#/home` | Overview |
| `#/explore` | Encyclopedia |
| `#/timeline` | Chronology |
| `#/chapters` | Book and section navigator |
| `#/map` | Location schematic and route anchors |
| `#/connections` | Relationship view |
| `#/status` | Character status ledger |
| `#/saved` | Reading desk |
| `#/sources` | Coverage and source register |
| `#/entity/<type>/<id>` | Entity or event detail panel |
| `#/chapter/<book>/<number>` | Section detail panel |

The encyclopedia accepts a `type` query parameter. The chapter view accepts a `book` query parameter. Other filter state is held in memory rather than serialized into the URL. Detail panels preserve an underlying base view. Selecting a chapter does not change the spoiler boundary.

## Browser persistence

All persistent keys use the `stormlight.v3.` prefix:

| Suffix | Stored value |
| --- | --- |
| `gate` | Completed-book boundary |
| `read` | Array of section keys |
| `saved` | Array of type-qualified entity keys |
| `notes` | Object mapping entity keys to note strings |

Persistence is specific to the browser origin and browser profile. It is not an account-level storage service. The application handles storage errors and supports manual JSON backup export and import.

Imported backups must use schema identifier `stormlight-reading-v3`. Import rejects files larger than 2,000,000 bytes, filters unknown section and entity keys, and limits imported notes to 20,000 characters per entry. Import preserves the current spoiler boundary rather than adopting the exported boundary.

## Chronology and geography

The `sort` field is an editorial anchor position. It is not a canonical timestamp. The in-world view groups historical material first; ordering within uncertain or parallel sequences remains approximate. Reveal-order sorting uses book rank and a chapter locator when it can be parsed.

The map plots inherited schematic coordinates. Route segments connect recorded anchors and do not model actual distance, travel duration, intermediate stops, or geographic obstacles. Nongeographic Spiritual Realm records have no coordinates.

## Hosting and access

The exported application contains no authentication implementation. Repository visibility and deployment visibility are independent. A public repository does not change access to any existing deployment. Any new deployment's access policy belongs to its host.

## Architectural limits

- Editorial reference data is curated rather than generated from complete book text.
- Spoiler filtering uses completed-book boundaries and selected overrides, not chapter-level semantic classification.
- Status records describe the last available editorial update, not a simulated world state.
- Relationship associations are not a temporal graph query engine.
- Validation uses a DOM harness and does not substitute for browser testing.
- The application loads the entire dataset before rendering its first view.
