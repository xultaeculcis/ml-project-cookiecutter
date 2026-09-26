# Architecture decision records

An architecture decision record (ADR) records one decision, its context and its consequences. The ADRs tell a future
reader why the project works as it does.

## When to write an ADR

Write an ADR when all of these conditions are true:

1. The decision is hard to reverse.
2. A future reader will not understand the decision without its context.
3. There were real alternatives, and you selected one for specific reasons.

Examples for ML projects:

- The choice of the primary metric.
- The data split policy (for example, split by site or by time, not at random, to prevent leakage).
- A change of a label definition or a class threshold. Update the glossary in the same pull request.
- The choice of a model framework or an experiment tracking server.
- A reproducibility constraint (fixed seeds, pinned data versions).

## Files

- The ADRs are in `docs/adr/`.
- The file name is `NNNN-title.md`: a four-digit number and a short title with hyphens, for example
    `0002-split-data-by-site.md`.
- To get the next number, find the highest number in the directory and add one.
- Do not change the decision of an accepted ADR. To change a decision, write a new ADR and set the status of the old
    ADR to `Superseded by ADR-NNNN`.
- Add each new ADR to the `nav` section of `mkdocs.yml`, under `Architecture decisions`.

## Template

```markdown
# NNNN. Title of the decision

- Status: Proposed | Accepted | Deprecated | Superseded by ADR-NNNN
- Date: YYYY-MM-DD

## Context

The problem and the forces that apply. The alternatives that you considered.

## Decision

The decision, in one or two sentences.

## Consequences

What becomes easier or more difficult because of the decision.
```

## Records

- [0001. Record architecture decisions](0001-record-architecture-decisions.md)
