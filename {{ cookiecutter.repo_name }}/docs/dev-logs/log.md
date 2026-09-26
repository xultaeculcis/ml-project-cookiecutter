# Development logs

The development logs (dev-logs) record the work on this project: experiments, data changes, model results and
decisions. Each entry is a snapshot. Use the entries to repeat a result or to find why something changed.

## Structure

Each entry is a directory in `docs/dev-logs/`:

```text
docs/dev-logs/
└── YYYY-MM-DD-<slug>/
    ├── log.md             # The entry
    └── assets/            # Images, plots, configs and metric reports
        └── make_plots.py  # Optional: the script that makes the plots in assets/
```

- The directory name starts with the date of the entry, then a short slug with hyphens, for example
    `2025-01-25-baseline-model`.
- Put all files that `log.md` uses in `assets/`. Link them with relative paths, for example
    `![Loss](assets/loss.png)`.
- If the entry has plots, put the script that makes them in `assets/make_plots.py`. The script reads the files in
    `assets/` (for example copied MLflow metrics) and writes the plots. Run it with `uv run python assets/make_plots.py`.
    Then anybody can make the plots again.

## Add an entry

1. Create the directory `docs/dev-logs/YYYY-MM-DD-<slug>/` with the `log.md` file and the `assets/` directory.

2. Write the entry in `log.md`. Include:

    - The goal of the work.
    - The MLflow run IDs and the configs that you used.
    - The results, with the metrics.
    - The conclusions and the next steps.

3. Add the entry to the `nav` section of `mkdocs.yml`, under `DEV-LOG`. Use this format:

    ```yaml
    nav:
      - DEV-LOG:
          - Intro: "dev-logs/log.md"
          - Log 2025-01-25 - Baseline model: "dev-logs/2025-01-25-baseline-model/log.md"
    ```

4. Build the documentation and check the entry:

    ```shell
    make docs-serve
    ```

5. Make sure that each link to `assets/` works.
