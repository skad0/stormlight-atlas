# Spoiler Model

## Purpose

The spoiler model limits what the application displays according to the latest completed book. It is a reading aid. It is not an authentication mechanism or a confidentiality boundary: the browser downloads the complete static dataset.

## Boundary values

| Value | Completed work |
| ---: | --- |
| 0 | No completed books |
| 1 | The Way of Kings |
| 2 | Words of Radiance |
| 3 | Edgedancer |
| 4 | Oathbringer |
| 5 | Dawnshard |
| 6 | Rhythm of War |
| 7 | Wind and Truth |

`EC` and `KL` use threshold `2`. They do not introduce additional values in the boundary selector. The initial boundary is `4`; a browser's stored selection overrides it.

## Profile projection

For each type-qualified entity key, `profile(key)` follows this procedure:

1. Select the last stored profile version whose `scope` is less than or equal to the active boundary.
2. If no version qualifies, use the earliest version as the candidate record while withholding its full profile fields.
3. Read facts from the latest stored version and retain only facts whose `reveal` threshold is permitted. This allows independently dated novella facts to appear before the later snapshot containing them becomes fully available.
4. Gather related events that pass their own reveal thresholds.
5. Determine the earliest recognized book threshold in the candidate record. If it has no recognized book identifier, use that version's scope.
6. Require a permitted full version, at least one permitted fact, or at least one permitted related event. Also require the introduction threshold and any explicit identity override to be permitted.
7. Use the candidate summary only when its entire snapshot scope is permitted. Otherwise use the latest permitted fact or a permitted event summary.
8. Withhold aliases, roles, profile associations, and other full-profile fields until the candidate snapshot is permitted.

The implementation contains selected identity overrides and earlier display-name substitutions. These are explicit editorial safeguards, not a complete entity-introduction classifier. A profile object can retain a raw candidate record internally; presentation and search must use its permitted projection.

## Inherited fact thresholds

The earlier snapshots use numeric editorial positions. The build maps those positions to completed-book boundaries:

| Position | Assigned boundary |
| --- | ---: |
| Negative | Source snapshot scope |
| 0–80 | 1 |
| Greater than 80 through 200 | 2 |
| Greater than 200 through 232 | 3 |
| Greater than 232 through 450 | 4 |
| Greater than 450 through 520 | 5 |
| Greater than 520 through 850 | 6 |
| Greater than 850 | 7 |

These numbers are migration rules, not story dates. New facts should use an explicit reveal threshold and a source locator rather than infer a threshold from a newly invented editorial position.

## Events and relationships

Events are visible when `event.reveal <= model.gate`. Recognized inherited book identifiers determine the threshold. An unrecognized or composite inherited book identifier defaults to `4`; it is not automatically split into an earlier reveal threshold.

Explicit relationships use the latest recognized book threshold among their listed books, defaulting to `4` when no listed identifier is recognized. New *Wind and Truth* relationships use threshold `7`.

A connection requires a visible focus record and a visible target record. Derived associations require the source full profile to be permitted. Changing the boundary invalidates the profile and connection caches.

## Search and secondary views

Search uses permitted profile names, projected summaries, status facts, and permitted aliases and roles. It also searches events and section context that pass their own thresholds. It does not search arbitrary raw JSON.

The status ledger uses permitted facts. Map routes use permitted nonhistorical event anchors. Source-register entries have reveal thresholds because their titles can contain later-book terminology. Book catalog titles remain visible before their plots are unlocked.

The section navigator uses completed-book gates. It does not offer chapter-specific spoiler protection. Arc context can describe later events within the same completed book.

## Limitations

- The repository, downloaded data, technical documentation, and external websites can contain unrestricted spoilers.
- The model does not parse prose to detect every possible future revelation.
- Inherited facts were migrated using editorial positions and selected corrections. Their reveal thresholds have not all received an independent semantic audit.
- Identity overrides cover selected known cases and require maintenance when data changes.
- Supplemental stories unlock with *Words of Radiance*, regardless of whether the reader has read those stories separately.
- Browser-local notes are associated with records; they do not have independent per-sentence spoiler metadata.
- Test assertions cover boundary invariants and selected regressions. Passing them is not proof of complete spoiler isolation.

## Change requirements

When adding or editing a record:

1. Set the reveal threshold to the first supported textual revelation, not the event's in-world date.
2. Keep later revelations out of earlier snapshot summaries, names, aliases, and relationships.
3. Mark inferred claims explicitly.
4. Add a source reference and the narrowest verified locator available.
5. Add regression assertions for changes to identity, status, or cross-book visibility.
6. Check search, direct links, connections, status, map routes, and source titles at the preceding boundary.
