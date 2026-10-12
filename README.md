# MindInvest-content

Dynamic pedagogic content for the MindInvest App. Allows the evolution of the app without rebuilding it.

## Content catalogues

- `flashcards/current.json`: existing flashcard catalogue.
- `etf-learning/concepts.json`: stable, language-independent concept identifiers and pedagogical tags.
- `etf-learning/current.json`: ETF summaries and editorial micro-tips extracted from the current Android ETF catalogues.
- `etf-learning/rules.json`: reusable localized micro-tip templates selected by generic ETF-characteristic conditions.

## ETF learning schema (v1)

Each content item has a stable `id`, a `conceptId`, a content `type`, a `level`, an `appliesToAssetIds` list, localized `translations`, a `status`, and a `version`.

- `ETF_SUMMARY` stores the existing per-ETF learning summary.
- `MICRO_TIP` stores an educational tip. Existing tip IDs are preserved.
- Translations are provided only where source text exists; do not assume a missing translation is available.
- Asset identifiers use the ETF's Yahoo-style symbol, for example `CW8.PA`.

## Migration status

The files under `etf-learning/` establish the external data model for Step 1. The Android app has not yet been switched to consume this catalogue; that integration and removal of the duplicated embedded fields will be handled in a subsequent app change. Until then, the existing embedded catalogue remains the runtime source.

Rule conditions supported by the Android selector: `ALWAYS`, `PEA_SYNTHETIC`, `PEA_PHYSICAL`, `PEA_INELIGIBLE`, `ACCUMULATING`, `DISTRIBUTING`, `CURRENCY_HEDGED`, and `FOREIGN_EXPOSURE_UNHEDGED`. Templates may use declared placeholders such as `{{expenseRatioPercent}}`.

Validate JSON, condition names, placeholders, and referenced concept IDs before publishing a new catalogue version.
