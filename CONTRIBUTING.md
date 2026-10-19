# Contributing

## Change scope

Use a focused change for one feature, data correction, coverage extension, or documentation improvement. Describe the resulting behavior and its validation. Do not combine an unrelated interface redesign with a narrative-data correction.

## Documentation conventions

- Use US English, UTF-8 text, and LF line endings.
- Use consistent terms: **entity**, **profile snapshot**, **fact**, **event anchor**, **section**, **source**, **spoiler boundary**, and **reveal threshold**.
- Use present tense to describe current behavior and imperative sentences for procedures.
- Define an abbreviation before using it, except for book identifiers listed in the README.
- Put exact identifiers, file paths, API names, and commands in code formatting.
- Distinguish implemented behavior, editorial assumptions, inferred claims, and planned work.
- Include reproducible commands and state the limits of validation.
- Avoid promotional claims, conversational history, unsupported completeness claims, and ambiguous wording.

## Data corrections

For a correction, identify the affected entity key, event ID, or section key. Provide a source URL, a locator, the proposed text, and the earliest permitted spoiler boundary. Preserve historical snapshots when a later book changes the available information.

For inferred claims, retain an explicit uncertainty label. For uncertain chronology, use a relative description and state that the exact alignment is unverified. Do not invent chapter titles, page numbers, map coordinates, or dates.

## Required checks

```sh
npm run build
npm run check
npm test
npm run docs
```

Review generated changes in `dist/data.json`, `validation.json`, `docs/COVERAGE.md`, and `SOURCES.md`. For UI changes, perform a browser review when a browser environment is available and report which flows were checked.

## Attribution

Do not add novel text, official artwork, credentials, personal reading backups, or content without an appropriate basis for publication. Keep narrative-source attribution and software-license scope distinct. See [Notice](NOTICE.md).
