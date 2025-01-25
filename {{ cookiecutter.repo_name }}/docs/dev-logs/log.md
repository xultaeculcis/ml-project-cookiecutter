## Intro

Welcome to the Development Logs for this ML project! Here, we keep concise, day-to-day records of our progress—from
experiment design and data processing to model tuning and final results. These logs help track changes,
document learnings, and ensure reproducibility.

Below is the recommended structure for each development log directory:

```
yyyy-mm-dd-<concise-name>/
  ├─ log.md        # Main log documentation
  └─ assets/       # Directory for images, plots, artifacts, etc.
```

Each log entry in the dev-logs directory captures a snapshot of our iterative process, making it easy to revisit
decisions or troubleshoot issues. Refer to the individual log pages for detailed insights into our ongoing development.

## Adding New Log Entries

1. **Create a new directory**:

    - Follow the naming convention: `yyyy-mm-dd-<concise-name>`.
    - Include the files:

    ```text
    yyyy-mm-dd-<concise-name>/
      ├─ log.md
      └─ assets/
    ```

2. **Document your work**

    - Write a concise, meaningful entry in `log.md` to capture key tasks, experiments, findings, and any relevant notes.

3. **Update the `mkdocs.yml`**

    - Open the `mkdocs.yml` file.
    - Locate the navigation (nav) section for DEV Logs.
    - Add a reference to your new directory and `log.md` so it appears in the navigation panel. For example:

    ```yaml
    nav:
      - Home: index.md
      - DEV-LOG:
        - Intro: "dev-logs/log.md"
        - Log 2025-01-25 - My Experiment: "dev-logs/2025-01-25-my-experiment/log.md"
        # Add more logs here...
    ```

    - Save the file.

4. **Preview and confirm**

    - Run `mkdocs serve` to preview your documentation.
    - Ensure your new log entry is visible and correctly linked in the navigation panel.

With these steps, each new development log will be properly documented and easily accessible through your MkDocs setup.
