# Contributing

Open an issue describing the problem or proposed improvement before making a large change.
For a pull request, create a branch, keep changes focused, and describe the behavior and validation.

## Local validation

```bash
python -m compileall -q app.py run_dashboard.py run_streamlit.py utils pages dashboard
python scripts/validate_project.py
```

Run the relevant dashboard after changing its behavior. Keep credentials and local environments out of commits.
Preserve raw source data; document transformations in notebooks and reports. When updating data, regenerate
related analysis tables and verify the bundled SQLite database remains consistent.

## Data and third-party materials

Identify the source and applicable terms before contributing new datasets or third-party assets.
Do not assume repository access grants rights to redistribute source datasets.
