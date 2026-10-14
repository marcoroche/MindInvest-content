# Learning notions catalog validation

The learning-notions catalog is validated automatically on pull requests and pushes to `main` whenever the catalog or its validator/workflow changes.

Run the same checks locally from the repository root:

```sh
python scripts/validate_learning_notions.py
```

The validator checks JSON parsing, schema version, supported/default languages, unique non-empty IDs, categories, allowed statuses, and non-empty titles and explanations for every supported language on active notions.

Stable IDs are persisted by the Android app to track completed notions. On pull requests, the workflow compares the catalog with the target branch and rejects removing an existing ID. Retire a notion by keeping its ID and setting `status` to `inactive`; do not rename an ID, because that is equivalent to removing the old one and adding a new one.

The validator uses only Python's standard library.
