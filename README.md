# MindInvest-content

Dynamic pedagogic content for the MindInvest App. Allows the evolution of the app without rebuilding it.

## Content catalogues

- `flashcards/current.json`: existing flashcard catalogue.
- `etf-learning/concepts.json`: stable, language-independent concept identifiers and pedagogical tags.
- `etf-learning/current.json`: ETF summaries and micro-tips extracted from the current Android ETF catalogues.

## ETF learning schema (v1)

Each content item has a stable `id`, a `conceptId`, a content `type`, a `level`, an `appliesToAssetIds` list, localized `translations`, a `status`, and a `version`.

- `ETF_SUMMARY` stores the existing per-ETF learning summary.
- `MICRO_TIP` stores an educational tip. Existing tip IDs are preserved.
- Translations are provided only where source text exists; do not assume a missing translation is available.
- Asset identifiers use the ETF's Yahoo-style symbol, for example `CW8.PA`.

## Migration status

The files under `etf-learning/` establish the external data model for Step 1. The Android app has not yet been switched to consume this catalogue; that integration and removal of the duplicated embedded fields will be handled in a subsequent app change. Until then, the existing embedded catalogue remains the runtime source.

Validate JSON and referenced concept IDs before publishing a new catalogue version.
