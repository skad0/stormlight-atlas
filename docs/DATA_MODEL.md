# Data Model

## Runtime document

`dist/data.json` is the runtime document. The build emits the following top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `meta` | Object | Editorial cutoff, version, scope, reconciliation policy, and limitations |
| `books` | Array | Main novel and novella catalog with spoiler gates and section counts |
| `entities` | Array | Type-qualified reference records with versioned profile data |
| `events` | Array | Curated story anchors with reveal thresholds and related entity IDs |
| `relations` | Array | Explicit relationship records |
| `chapters` | Array | Navigable section records |
| `sources` | Array | Bibliographic and source-provenance records |
| `supplements` | Array | Short-story catalog entries and event references |
| `cosmereBooks` | Array | Connected-work catalog; not complete plot coverage |
| `validation` | Object, added by validation | Validation summary and browser-review limitation |

Optional fields may be absent. Source snapshots retain additional historical fields that the runtime does not use.

## Identifiers

Entity identity is the pair `(type, id)`, serialized as `<type>:<id>`. Supported types are `character`, `location`, `faction`, `item`, and `magic`.

A bare identifier is not globally unique. For example, `character:rysn` and `faction:rysn` are different records. Event IDs and section keys have separate namespaces. Runtime chapter keys use `<book>:<number>`.

Identifiers are stable references. Display names can change between profile versions. Do not derive identity from a display name or merge records solely because their names match.

## Entity record

| Field | Type | Meaning |
| --- | --- | --- |
| `key` | String | Type-qualified key |
| `id` | String | Identifier within the entity type |
| `type` | String | Entity type |
| `versions` | Array | Stored profile snapshots in editorial order |
| `versions[].scope` | Integer | Minimum boundary for the complete snapshot |
| `versions[].data` | Object | Profile fields, associations, facts, and source references |

Common profile fields are `id`, `name`, `summary`, `books`, `kind` or `category`, `tags`, and `facts`. Type-specific fields include:

| Entity type | Common additional fields |
| --- | --- |
| Character | `aliases`, `roles`, `factions`, `locations`, `first`, `last` |
| Faction | `members`, `goals` |
| Location | `region`, `plane`, `scale`, `x`, `y`, `aliases` |
| Item | `owners`, `locations`, `related` |
| Magic | `users`, `limits`, `related`, `examples` |

`watSummary` is a historical extension field used for an additional researched summary. Its field name does not define an independent reveal rule; the containing version's scope controls its display.

## Fact record

| Field | Type | Meaning |
| --- | --- | --- |
| `text` | String | Original paraphrased fact or status statement |
| `reveal` | Integer | Minimum completed-book boundary |
| `locator` | String, optional | Book/chapter locator or explicit verification limitation |
| `position` | Number, optional | Preserved inherited editorial position |
| `certainty` | String, optional | Claim qualification, such as `confirmed` or `strong inference` |
| `sources` | Array, optional | Source identifiers or source references |

Facts are stored in editorial sequence. The status projection uses the last permitted fact, not the greatest canonical timestamp. A status statement therefore means "last recorded in this reference," not "known unchanged at every subsequent story moment."

## Event record

| Field | Type | Meaning |
| --- | --- | --- |
| `id`, `key`, `title` | Strings | Identity and display title |
| `book` | String or null | Primary or inherited composite book identifier; null for some history anchors |
| `chapter` | String or number, optional | Text locator; may identify a range or special section |
| `summary`, `explanation` | Strings | Curated original paraphrase and optional context |
| `reveal` | Integer | Display threshold |
| `sort` | Number | Editorial ordering position; not a date |
| `dateLabel`, `chronology` | Strings | Human-readable temporal context and uncertainty |
| `history` | Boolean, optional | Historical/flashback grouping flag |
| `confidence` | String | Editorial confidence label |
| `characters`, `locations`, `factions` | Arrays of strings | IDs in the named entity collections |
| `sources` | Array | Source identifiers, HTTPS URLs, or source objects |
| `provenance` | String, optional | Inherited or newly researched origin |

Additional research fields, including `timeKind`, `timeLabel`, and `chronologyNote`, may be retained. Confidence in an event is separate from confidence in an exact date.

## Relationship record

Explicit relationships contain `source`, `target`, `kind`, `label`, `summary`, `books`, `chapter`, and `reveal` where applicable. Source and target values are historically bare IDs, resolved by the runtime's resolver. The dataset also retains optional `from`, `to`, `status`, `confidence`, and source-provenance fields.

Runtime profile associations are generated from entity fields. They are not stored as a second complete edge list in the runtime document. The original snapshots' `graphNodes` and `graphEdges` remain available as historical source material but do not define the active graph.

## Section record

| Field | Type | Meaning |
| --- | --- | --- |
| `key` | String | `<book>:<number>` |
| `book` | String | Book identifier |
| `number` | Number | Navigation ordering value |
| `label` | String | Verified title or generic section label |
| `reveal` | Integer | Completed-book threshold |
| `arc`, `arcRange`, `arcSummary` | Strings, optional | Context that can span several sections |
| `anchors` | Array of strings | Event IDs associated with the section |
| `coverage` | String | Index-only or curated-anchor classification |
| `source` or `sourceUrl` | String, optional | External reference URL |
| `interludeNumber` | Integer, optional | Explicit interlude identity |

`number` is a navigation key rather than a uniform canonical chapter number. Earlier source conventions are preserved. For example, fractional values place interludes between numbered chapters; some special sections use zero or negative values. *Wind and Truth* uses `-1` for the prologue, `1000` for the epilogue, and `1001` for the postlude. Code should use `label`, `interludeNumber`, and verified metadata when displaying a section type instead of guessing from the numeric value.

The *Edgedancer* prologue reuses the earlier Lift interlude. Its shared event anchor is an explicit cross-book exception in validation.

## Source record

Source records contain a title, HTTPS URL, type or quality classification, and an optional stable source `id`. Some include `use`, `note`, `verifiedAt`, or an attribution limit retained from the research process. `reveal` controls whether the source's title appears in the application bibliography.

Legacy source records do not all have stable IDs. New research references can use IDs that resolve through the source register. The generated [source register](../SOURCES.md) provides document-level origin, purpose, and claim-linkage information.

The bibliography is not a claim that every entry was retrieved again for the public export. A retained `verifiedAt` value records the source snapshot's research date.

## Source-to-runtime transformation

| Input | Runtime use |
| --- | --- |
| `source-data/oathbringer.json` | Scope-4 profile snapshots |
| `source-data/rhythm-of-war.json` | Scope-6 profiles, inherited events, relationships, chapters, and bibliography |
| `source-data/reference-audit.json` | Selected corrections and chapter-anchor changes |
| `source-data/missing-chapters.json` | 37 missing early-book interlude records |
| `source-data/wind-and-truth.json` | Later facts, entities, events, relationships, bibliography, and short stories |

Runtime data should be regenerated from these inputs. Do not edit `dist/data.json` directly.
