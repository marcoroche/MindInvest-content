#!/usr/bin/env python3
"""Validate the MindInvest replay coach content catalogues."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {"fr", "en", "de", "es"}
CATALOGS = {
    "events": ("replay-coach/events.json", "events", {"name", "dateLabel", "teaser", "outcome", "challengeText", "holdLabel", "sellLabel"}),
    "observations": ("replay-coach/observations.json", "observations", {"title", "explanation", "advice", "reflectionQuestion"}),
    "examples": ("replay-coach/examples.json", "examples", {"title", "body", "takeaway"}),
    "exercises": ("replay-coach/exercises.json", "exercises", {"prompt", "explanation"}),
}

def main():
    errors = []
    ids_by_catalog = {}
    for name, (relative_path, collection, required_fields) in CATALOGS.items():
        path = ROOT / relative_path
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_path}: cannot read valid JSON: {exc}")
            continue
        if not isinstance(data, dict) or data.get("schemaVersion") != 1:
            errors.append(f"{relative_path}: root must be an object with schemaVersion 1")
            continue
        languages = data.get("supportedLanguages")
        if not isinstance(languages, list) or not LANGUAGES.issubset(set(languages)):
            errors.append(f"{relative_path}: supportedLanguages must include fr, en, de, es")
        if data.get("defaultLanguage") not in (languages or []):
            errors.append(f"{relative_path}: defaultLanguage must be supported")
        items = data.get(collection)
        if not isinstance(items, list) or not items:
            errors.append(f"{relative_path}: {collection} must be a non-empty list")
            continue
        seen = set()
        ids_by_catalog[name] = set()
        for index, item in enumerate(items):
            where = f"{relative_path}:{collection}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{where} must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                errors.append(f"{where}.id must be a non-empty string")
            elif item_id in seen:
                errors.append(f"{where}: duplicate id {item_id!r}")
            else:
                seen.add(item_id)
                ids_by_catalog[name].add(item_id)
            if item.get("status") not in {"active", "inactive", "draft"}:
                errors.append(f"{where}.status must be active, inactive or draft")
            if not isinstance(item.get("version"), int) or item["version"] < 1:
                errors.append(f"{where}.version must be a positive integer")
            translations = item.get("translations")
            if not isinstance(translations, dict):
                errors.append(f"{where}.translations must be an object")
                continue
            if item.get("status") == "active":
                for lang in ("fr", "en", "de", "es"):
                    translation = translations.get(lang)
                    if not isinstance(translation, dict):
                        errors.append(f"{where}: active item missing translation for {lang}")
                        continue
                    for field in required_fields:
                        value = translation.get(field)
                        if not isinstance(value, str) or not value.strip():
                            errors.append(f"{where}: active translation {lang}.{field} must be a non-empty string")
            if name == "events":
                try:
                    from datetime import date
                    date.fromisoformat(item.get("startDate", ""))
                except (TypeError, ValueError):
                    errors.append(f"{where}.startDate must be YYYY-MM-DD")
                if not isinstance(item.get("xp"), int) or item["xp"] < 0:
                    errors.append(f"{where}.xp must be a non-negative integer")
                offset = item.get("challengeDayOffset")
                if offset is not None and (not isinstance(offset, int) or offset < 0):
                    errors.append(f"{where}.challengeDayOffset must be null or a non-negative integer")
            for field in ("relatedNotions",):
                if field in item and (not isinstance(item[field], list) or not all(isinstance(x, str) and x for x in item[field])):
                    errors.append(f"{where}.{field} must be a list of non-empty strings")
            if name == "examples" and (not isinstance(item.get("notionId"), str) or not item["notionId"]):
                errors.append(f"{where}.notionId must be a non-empty string")
            if name == "exercises" and item.get("type") not in {"reflection", "quiz"}:
                errors.append(f"{where}.type must be reflection or quiz")
            if name == "exercises" and item.get("type") == "quiz":
                for lang in ("fr", "en", "de", "es"):
                    tr = translations.get(lang, {})
                    options = tr.get("options")
                    index_value = tr.get("correctIndex")
                    if not isinstance(options, list) or len(options) < 2:
                        errors.append(f"{where}: quiz options for {lang} must contain at least two choices")
                    elif not isinstance(index_value, int) or not 0 <= index_value < len(options):
                        errors.append(f"{where}: quiz correctIndex for {lang} must index an option")
    known_notion_ids = {
        "market-volatility", "market-diversification", "portfolio-dca",
        "portfolio-horizon", "psychology-panic", "portfolio-rebalancing",
    }
    for name in ("observations", "examples", "exercises"):
        for item_id in ids_by_catalog.get(name, set()):
            pass
    for relative_path, collection in [
        ("replay-coach/observations.json", "observations"),
        ("replay-coach/examples.json", "examples"),
        ("replay-coach/exercises.json", "exercises"),
    ]:
        try:
            data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
            for index, item in enumerate(data.get(collection, [])):
                refs = item.get("relatedNotions", [])
                if collection in {"examples", "exercises"}:
                    refs = [item.get("notionId")]
                for ref in refs:
                    if ref not in known_notion_ids:
                        errors.append(f"{relative_path}:{collection}[{index}] references unknown learning notion {ref!r}")
        except (OSError, json.JSONDecodeError):
            pass
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        print(f"Replay coach validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Replay coach validation passed: events, observations, examples and exercises.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
