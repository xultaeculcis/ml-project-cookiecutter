# 0001. Record architecture decisions

- Status: Accepted
- Date: {% now 'utc', '%Y-%m-%d' %}

## Context

The team makes decisions about the data, the metrics, the models and the infrastructure of this project. Later, team
members and AI agents need to know why a decision was made. The code does not show this.

## Decision

We record each decision that is hard to reverse as an architecture decision record (ADR) in `docs/adr/`. We use the
format in [About ADRs](README.md).

## Consequences

- A reader can find the reason for a decision in the repository.
- Each decision that is hard to reverse needs a short ADR in the same pull request.
- A changed decision gets a new ADR. The old ADR stays, with the status `Superseded`.
