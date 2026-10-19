# Development and Validation

## Toolchain

Use Node.js 22 or later and Python 3.10 or later. The repository uses only their standard libraries. It has no package-installation, bundling, or dependency-lockfile requirement.

## Edit workflow

1. Edit `dist/app.js`, `dist/model.js`, `dist/index.html`, or `dist/style.css` for application changes.
2. Edit the applicable `source-data/` JSON file for editorial changes.
3. Run `npm run build` to regenerate `dist/data.json`.
4. Run `npm run check` to check JavaScript syntax.
5. Run `npm test` to validate data and application rendering.
6. Run `npm run docs` to regenerate the coverage report and source register.
7. Review the diff, including generated data and documentation.

Builds use local source files and require no network access. Rebuilding removes the previous generated validation summary; running the validator restores it. Validation also updates `validation.json`.

## Local runtime

`npm run dev` serves `dist/` at `http://127.0.0.1:8080/`. This is a local development command, not a production service configuration. No history fallback is required because routes use fragments.

Asset references are application-relative. Dataset loading resolves `data.json` against `import.meta.url`, preserving compatibility with domain-root and subpath deployment.

## Validation layers

| Layer | Checks |
| --- | --- |
| Identifier integrity | Unique entity keys, event IDs, and section keys |
| Typed references | Event participants resolve in the correct entity collections |
| Event provenance | Event source references resolve or provide HTTPS URLs |
| Section integrity | Expected numbered chapters and interlude counts are present |
| Anchor integrity | Chapter event anchors resolve and match their book or an explicit shared-section exception |
| Relationship integrity | Explicit relationship endpoints resolve |
| Spoiler projection | Permitted profiles and facts satisfy boundary invariants; selected future revelations remain hidden |
| Rendering | Actual view, entity, event, and chapter templates execute in a minimal DOM harness |
| Navigation links | Generated entity and section links resolve |
| Persistence | Actual delegated click handlers update reading progress and bookmarks |
| Portable assets | Application asset URLs are relative and dataset loading uses the module-relative URL |

The initial baseline includes 1,435 rendered view/detail cases and 22,256 repeated link checks. These values can change when coverage or validation changes.

## Validation limits

The harness implements only the DOM interfaces required to execute templates and selected handlers. It does not perform real browser rendering, CSS layout, keyboard focus evaluation, screen-reader evaluation, network execution, or a complete import/export interaction test. It also does not exercise every combination of filters.

Validation does not verify every narrative statement, every reveal threshold, or the factual correctness of every inherited chapter locator. Retain the explicit coverage and provenance limitations in documentation.

For a browser review, verify at least the following:

- Desktop and mobile navigation.
- Boundary changes while visiting each major view.
- Search before and after unlocking a later book.
- Entity, event, and section deep links; browser Back and Forward.
- Modal close behavior, keyboard focus, and Escape handling.
- Book, entity-type, relationship-type, and map filters.
- Bookmark and reading-progress persistence after reload.
- Backup export, valid import, invalid import, and unknown-key filtering.
- Deployment under a nonroot URL path.

## Editorial changes

Use source IDs for new sources where possible. Supply the narrowest verified locator: a chapter, a section, a range, or an explicit statement that a precise locator is unavailable. Do not substitute an inferred date for an unknown date or present an inference as a confirmed fact.

Preserve earlier snapshots when adding a later revelation. Add a later profile version or a separately gated fact instead of changing an earlier summary to incorporate future information.

## Adding another book

Book support is currently explicit rather than plugin-based. Review all of the following:

| Location | Required review |
| --- | --- |
| `scripts/build-data.py` | Book catalog, `ORDER`, source loading, section generation, fact thresholds, and provenance |
| `dist/model.js` | `GATES`, introduction logic, selected identity overrides, and display substitutions |
| `dist/app.js` | Boundary selector, maximum boundary, supplemental-story handling, labels, and chronology parsing |
| `scripts/validate.mjs` | Expected section counts, source/link integrity, and spoiler regression assertions |
| `scripts/generate-reference-docs.py` | Any new source-origin classification or coverage assumptions |
| Documentation | Scope, coverage, source register, data model, and known limitations |

Do not extend the numeric boundary range without updating the UI's current `0..7` assumptions. Do not treat a new book's publication date as its in-world chronology position.

## Continuous integration

The `Validate` GitHub Actions workflow uses Node.js 22 and Python 3.12. It rebuilds the dataset, checks JavaScript syntax, runs validation, regenerates reference documentation, and checks that generated documentation matches the committed files.

The workflow has read-only repository-content permissions. It does not deploy the application or modify repository visibility.
