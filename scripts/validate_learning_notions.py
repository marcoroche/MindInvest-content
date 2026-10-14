#!/usr/bin/env python3
"""Validate the MindInvest learning-notions catalog using only Python's standard library."""

import argparse
import json
import sys
from pathlib import Path

ALLOWED_STATUSES = {"active", "inactive"}
REQUIRED_LANGUAGES = {"fr", "en", "de", "es"}


def load_json(path):
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid JSON from {path}: {exc}") from exc


def validate_catalog(catalog, label="catalog"):
    errors = []
    if not isinstance(catalog, dict):
        return [f"{label}: root must be a JSON object"]

    if catalog.get("schemaVersion") != 1:
        errors.append(f"{label}: schemaVersion must be 1")

    languages = catalog.get("supportedLanguages")
    if not isinstance(languages, list) or not languages or not all(
        isinstance(lang, str) and lang.strip() for lang in languages
    ):
        errors.append(f"{label}: supportedLanguages must be a non-empty list of language codes")
        languages = []
    elif len(languages) != len(set(languages)):
        errors.append(f"{label}: supportedLanguages contains duplicates")

    if not REQUIRED_LANGUAGES.issubset(set(languages)):
        missing = sorted(REQUIRED_LANGUAGES - set(languages))
        errors.append(f"{label}: supportedLanguages is missing required languages: {', '.join(missing)}")

    default_language = catalog.get("defaultLanguage")
    if default_language not in languages:
        errors.append(f"{label}: defaultLanguage must be included in supportedLanguages")

    notions = catalog.get("notions")
    if not isinstance(notions, list):
        errors.append(f"{label}: notions must be a list")
        return errors

    seen_ids = set()
    for index, notion in enumerate(notions):
        where = f"{label}: notions[{index}]"
        if not isinstance(notion, dict):
            errors.append(f"{where} must be an object")
            continue

        notion_id = notion.get("id")
        if not isinstance(notion_id, str) or not notion_id.strip():
            errors.append(f"{where}.id must be a non-empty string")
        elif notion_id in seen_ids:
            errors.append(f"{where}: duplicate notion id '{notion_id}'")
        else:
            seen_ids.add(notion_id)

        if not isinstance(notion.get("category"), str) or not notion["category"].strip():
            errors.append(f"{where}.category must be a non-empty string")

        status = notion.get("status")
        if not isinstance(status, str) or status not in ALLOWED_STATUSES:
            errors.append(f"{where}.status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")

        translations = notion.get("translations")
        if not isinstance(translations, dict):
            errors.append(f"{where}.translations must be an object")
            continue

        if status == "active":
            for language in languages:
                translation = translations.get(language)
                if not isinstance(translation, dict):
                    errors.append(f"{where}: active notion '{notion_id}' has no translation object for '{language}'")
                    continue
                for field in ("title", "explanation"):
                    value = translation.get(field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"{where}: active notion '{notion_id}' needs a non-empty "
                            f"'{field}' for language '{language}'"
                        )

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="learning-notions/catalog.json")
    parser.add_argument(
        "--baseline",
        help="Optional previous catalog JSON; IDs present there may not be removed.",
    )
    args = parser.parse_args()

    try:
        catalog = load_json(args.catalog)
        errors = validate_catalog(catalog)
        if args.baseline:
            baseline = load_json(args.baseline)
            if isinstance(baseline, dict) and isinstance(catalog, dict):
                old_notions = baseline.get("notions", [])
                new_notions = catalog.get("notions", [])
                if isinstance(old_notions, list) and isinstance(new_notions, list):
                    old_ids = {
                        item.get("id") for item in old_notions
                        if isinstance(item, dict) and isinstance(item.get("id"), str)
                    }
                    new_ids = {
                        item.get("id") for item in new_notions
                        if isinstance(item, dict) and isinstance(item.get("id"), str)
                    }
                    for removed_id in sorted(old_ids - new_ids):
                        errors.append(
                            f"catalog: stable notion id '{removed_id}' was removed; "
                            "keep it and set status to 'inactive' instead"
                        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Catalog validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Catalog validation passed: {len(catalog['notions'])} notions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
