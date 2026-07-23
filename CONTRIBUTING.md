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
