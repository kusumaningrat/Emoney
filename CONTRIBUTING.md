# Contributing

## PR titles

The PR title becomes a line in the auto-generated release notes — write it for
that audience, not just for reviewers.

**Format:** `<type>(<scope>): <summary> [TICKET-ID]`

- `type` — one of `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`
- `scope` — the affected service, e.g. `emoney-core`, `emoney-account`, `ci`
- `summary` — what changed, in plain language a non-engineer could read in a
  changelog
- `TICKET-ID` — the GSCRUM/BEE ticket, if one exists

**Bad** (these actually shipped in v0.1.0 and are meaningless in a changelog):
- `Dev`
- `Staging`
- `workflow init`
- `Add required key`

**Good:**
- `feat(emoney-account): add liability extraction endpoint [BEE-301]`
- `fix(emoney-core): correct integer overflow on account id [BEE-277]`
- `chore(ci): stabilize staging deploy workflow`

## PR labels

Every PR must carry exactly one of these before merge — they drive the
categorized sections in GitHub Releases (see `.github/release.yml`):

| Label           | Category in release notes | Use for                                  |
|-----------------|---------------------------|-------------------------------------------|
| `feature`       | Features                  | New user-facing capability                 |
| `enhancement`   | Features                  | Improvement to existing capability         |
| `bug`           | Fixes                     | Bug report turned into a fix               |
| `fix`           | Fixes                     | Any other correction                       |
| `chore`         | Chores                    | Tooling, refactors, non-functional cleanup |
| `dependencies`  | Chores                    | Dependency bumps                           |
| `documentation` | Chores                    | Docs-only changes                          |
| `ignore-for-release` | *(excluded entirely)* | Merge commits, WIP branches, internal-only changes not worth surfacing to release notes |

PRs with none of these labels still appear in the notes, under **Other
Changes** — but that bucket should stay empty. If you're not sure which label
fits, ask in review rather than leaving it unlabeled.

## Full example

A PR that adds a liability extraction endpoint to `emoney-account`, tracked as
`BEE-301`:

- **Title:** `feat(emoney-account): add liability extraction endpoint [BEE-301]`
- **Label:** `feature`
- **Description** (using `.github/PULL_REQUEST_TEMPLATE.md`):

  ```markdown
  ## Summary

  Adds a `/liabilities/extract` endpoint that pulls liability records from a
  linked account and normalizes them into our schema. Needed so the financial
  planning service can include liabilities in net worth calculations.

  ## Checklist
  - [x] PR title follows `<type>(<scope>): <summary> [TICKET-ID]`
  - [x] A changelog label is applied: `feature`
  ```

This is what turns into a release note reader sees:

> **Features**
> - feat(emoney-account): add liability extraction endpoint [BEE-301] (#42)

Compare that to a PR titled `Add required key` with no label — it would land
under **Other Changes** with no indication of what it actually did.

## Versioning is per service, not per repo

This repo has 7 independently-deployed services. Each ships on its own
version number and tag prefix — a release of one does not bump, or even
touch, the others:

| Service | Tag prefix | Example |
|---|---|---|
| EMoney Identity | `identity-v` | `identity-v0.1.0` |
| EMoney Account | `account-v` | *(not wired up yet — see below)* |
| EMoney Client | `client-v` | *(not wired up yet)* |
| EMoney Core | `core-v` | *(not wired up yet)* |
| EMoney Financial Planning | `financial-planning-v` | *(not wired up yet)* |
| EMoney Master | `master-v` | *(not wired up yet)* |
| EMoney Advisor Mock Server | `mock-server-v` | *(not wired up yet)* |

**Only `identity-v*` is live today.** EMoney Identity is the only one of
these 7 services with a real staging/prod promotion split
(`workflow_dispatch` with `environment: staging|prod` in
`emoney-identity.yml`) — the other 6 build and deploy straight to one
environment on every push to `main`, with no staging gate to hang
auto-tagging off of. Each of those 6 needs that staging/prod split added to
its CI workflow before it can get the same automatic tagging and release
notes; until then, they simply don't produce a tagged release or a
changelog entry.

## When release notes are generated

Merging a PR into `main` does **not** by itself create a release note —
titles and labels only set up the content, they don't trigger publishing.
For `identity-v*`, tagging is not a manual step either — **a release is cut
automatically the moment EMoney Identity is promoted to staging**.

The flow, end to end:

1. PRs merge into `main` all week, each with a correct title and label,
   scoped to `eMoney-identity/`.
2. Someone promotes EMoney Identity to staging the normal way —
   `workflow_dispatch` on `emoney-identity.yml` with `environment: staging`.
3. Once that `deploy-staging` job succeeds, a `tag-release` job (calling
   `.github/workflows/_reusable-tag-release.yml`) runs automatically. It
   finds the most recent prior `identity-v*` tag, collects every PR merged
   since then that touched `eMoney-identity/`, decides the version bump
   from those PRs' labels (`feature`/`enhancement` → minor, otherwise →
   patch; major only via an explicit `major_bump` dispatch input), and
   pushes the resulting tag — or pushes nothing if nothing changed since
   the last tag.
4. That tag push triggers `.github/workflows/release.yml`, which builds the
   categorized, path-filtered release note and publishes the GitHub
   Release.
5. Later, promoting that same commit to prod (`environment: prod` + `sha`)
   redeploys the already-tagged staging artifact — it does **not** cut a
   new version or fire `tag-release` again. Prod promotion is instead the
   trigger for the manual step below: writing the customer-facing external
   notes for the version that's now live.

## Two release notes per service: internal vs. external

Each service produces **two separate documents per release, not one** —
different audiences, different content rules, different authors.

|                  | Internal changelog                            | External release notes                            |
|------------------|------------------------------------------------|----------------------------------------------------|
| **Where**        | The GitHub Release body, generated by `.github/workflows/release.yml` | A hand-written doc per service once this goes live |
| **Triggered by** | Automatic, on **staging** promotion (`deploy-staging` success) | Manual — written once the version is promoted to **prod** |
| **Audience**     | Engineers, on-call, anyone debugging a deploy   | Customers / sales — non-technical readers          |
| **How it's made**| **Fully automatic.** Built from merged PR titles + labels, per the process above. No one writes it. | **Fully manual.** A human reads the internal changelog and hand-writes a short, benefit-language description of what changed. |
| **Who owns it**  | Nobody — it's a mechanical byproduct of following the title/label conventions in this doc | Not the engineer who wrote the PR. Someone doing product/release-notes work |
| **Contains**     | PR titles verbatim, ticket IDs, PR numbers      | Plain-English capability descriptions — **no ticket IDs, PR numbers, or internal system names, ever** |

**What this means for you as an engineer:** your job stops at writing a
good PR title, applying the correct label, and scoping the PR to
`eMoney-identity/`. That's the only input either document needs from you.
