# Pre-publish sweep (report only — nothing published or changed)

Run 2026-10-02. Every check below was run against the actual repo state at that time;
none of these findings have been acted on (no fixes applied, no commits made for them,
no config changed) — this is a report for the user to act on, per the task's own
instruction ("report findings only, publish nothing").

## 1. API keys and personal email — search of all tracked files, full git history, and local working directory

**Patterns searched:** `gsk_` (Groq), `AIza` (common Google API key prefix), `sk-`
(OpenAI-style), `AQ.Ab8` (the actual prefix of the Google AI Studio key in use), and
`<personal-email-local-part>`, case-insensitive where relevant.

**Scope:** (a) the current working tree, tracked and untracked files, (b) the full git
history across all commits (`git log --all -p -S <pattern>`), (c) all cached LLM logs
(`llm_logs/`, which is tracked and was included in (a) and (b)).

**Result: clean.**
- `gsk_`: zero matches anywhere (tracked files, history, untracked files).
- `AIza`: zero matches anywhere.
- `sk-`: 3 history hits, all false positives — ordinary English words split across a
  line wrap (`task-difficulty`, `Desk-top`), not a key fragment.
- `<personal-email-local-part>`: zero matches anywhere (tracked files, history, untracked files).
- `AQ.Ab8...` (the real current key): found in exactly one place — `.env`, which is
  listed in `.gitignore` and confirmed via `git check-ignore -v .env` before it was ever
  written (see DECISIONS.md, 2026-09-29 and 2026-10-02 entries). `.env` itself has never
  been committed (`git log --all --oneline -- .env` returns nothing).

**No fix needed.** The key-handling approach used throughout this project (write once to
a gitignored `.env`, never print, never commit) held up under a full-history search.

## 2. Commit author email

**Finding:** every commit so far (`git log --format='%an <%ae>'`) uses
`fennaya <fennaya@users.noreply.github.com>` — already correct, because every commit in
this project was made with an explicit `-c user.name=... -c user.email=...` override on
the `git commit` command itself.

**A real latent risk, not yet triggered:** this repo's **local** git config has no
`user.name`/`user.email` set at all (`git config --local user.email` returns empty). The
machine's **global** git config does have one set: `user.email = <personal-email>`
(the real personal email). This means: if anyone (including a future session of this
assistant, or the user themselves) runs a plain `git commit` in this repo *without*
remembering to pass the `-c` override, git will silently fall back to the global config
and the commit will be authored as `<personal-email>` instead of the
noreply-GitHub-handle address used everywhere so far.

**Proposed fix (not applied):** set this repo's *local* config explicitly, so it no
longer depends on every future commit remembering the override:
```bash
git config user.name "fennaya"
git config user.email "fennaya@users.noreply.github.com"
```
This only touches `.git/config` inside this one repo (not `--global`), is fully
reversible, and makes the correct identity the default for this repo from now on.

## 3. Repo size

| Item | Size |
|---|---|
| Total working directory (excluding `.venv`, which is gitignored and not part of the repo) | 593 MB |
| `.git/` (the actual git history/object store) | 31 MB |
| `data/` (raw + processed) | 277 MB |
| `data/raw/hts_revisions/` (20 full USITC HTS schedule dumps, one per revision) | 255 MB |
| `data/raw/rulings/` (1,816 cached CBP ruling JSON files) | 17 MB |
| `llm_logs/` (all model responses, English + translations) | 17 MB |
| `figures/`, `review/`, `scripts/` | <1 MB each |

**No single file exceeds 50 MB.** The largest individual files are the 20
`data/raw/hts_revisions/*.json` dumps, ~13 MB each.

**Proposed git-vs-Zenodo split (not applied):**
- **Keep in git:** all code (`scripts/`, `analysis.py`), all markdown docs, `figures/`,
  `review/` (small CSVs/markdown + the one HTML page), `data/processed/` (4.8 MB —
  the actual derived datasets the analysis runs on), and `llm_logs/` (17 MB — the actual
  experimental results; this is the evidence behind every reported number and belongs
  in git for reproducibility and version history).
- **Archive on Zenodo only, not in git:** `data/raw/hts_revisions/` (255 MB) and
  `data/raw/rulings/` (17 MB) — these are bulk, mechanically-fetched caches of public
  third-party government data, each individually regenerable by re-running
  `scripts/fetch_hts.py` / `scripts/fetch_rulings.py` against the live CBP/USITC APIs
  (documented in README's Reproduce section). Keeping 272 MB of easily-refetched raw
  cache in git bloats every future clone for no reproducibility benefit a Zenodo-hosted
  snapshot wouldn't equally provide, and a `.zenodo.json`/release note can point to
  exactly which revision IDs and date range were used.
- Net effect: git repo shrinks from ~300 MB of tracked data to about 22 MB
  (`data/processed/` + `llm_logs/`), a repo size appropriate for GitHub.

## 4. CBP/USITC data license

**Finding: both are confirmed US government works, not subject to copyright.**
- Direct statutory basis: **17 U.S.C. § 105** — "Copyright protection under this title
  is not available for any work of the United States Government." Verified against the
  U.S. Code text itself: https://www.law.cornell.edu/uscode/text/17/105
- CBP's own site states this explicitly for its own content: "information on the U.S.
  Customs and Border Protection website is in the public domain and may be reproduced,
  published or otherwise used without the permission of the CBP. We request only that
  the CBP be cited as the source of the information." Source:
  https://www.cbp.gov/site-policy-notices/copyright-notice
- USITC did not have an equally explicit standalone copyright-notice page found during
  this check, but as a U.S. federal agency, its official publications (including the
  Harmonized Tariff Schedule) are works of the United States Government under the same
  17 U.S.C. § 105 rule.

**Proposed addition to README.md (not applied):** a short "Data license" section citing
both sources above, noting that the CBP ruling text and USITC tariff schedule data used
in this project are U.S. Government works in the public domain, while the project's own
code (MIT) and analysis/findings (CC BY 4.0) retain the licensing already stated in
`CITATION.cff`.

## Summary of proposed changes (none applied — user's call)

1. Set this repo's local git config (`user.name`/`user.email`) so future commits can't
   silently fall back to the personal gmail address in global config.
2. Move `data/raw/hts_revisions/` and `data/raw/rulings/` out of git, into a Zenodo-only
   archive, keeping a reproduction path via the existing fetch scripts.
3. Add a short "Data license" section to README.md citing 17 U.S.C. § 105 and CBP's
   public-domain notice.

No API keys or the personal email were found anywhere they shouldn't be — that part of
the sweep is clean with no action needed.
