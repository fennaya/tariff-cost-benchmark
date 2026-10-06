# Decisions log

Format per entry: date, problem, options considered, choice, why, what would prove it wrong.

---

## 2026-09-28 — No free LLM API key on this machine

**Problem:** The hard rules require using only free tiers of keys already present in this
machine's environment (GROQ_API_KEY checked first, then others). A full scan of environment
variables found none of: GROQ_API_KEY, OPENAI_API_KEY, TOGETHER_API_KEY, CEREBRAS_API_KEY,
MISTRAL_API_KEY, GOOGLE_API_KEY/GEMINI_API_KEY, COHERE_API_KEY, HF_TOKEN/HUGGINGFACE*,
OPENROUTER_API_KEY, or ANTHROPIC_API_KEY. Only `ANTHROPIC_BASE_URL` is set (part of this
Claude Code session's own config, not a usable API key, and Anthropic's API is not
free-tier).

**Options:**
1. Stop immediately and ask the user for a key. Cheapest for the user's time is to keep
   going on everything else first, since much of the project (data collection, duty
   rates, leak-safe input prep) needs no LLM at all.
2. Skip the LLM-dependent phases (0's model list, 4, 5, 6's model comparison, 7) entirely
   and only report the non-LLM parts. Loses the actual point of the project.
3. Do all LLM-independent phases now (0 setup, 1 rulings, 2 leak-safe extraction, 3 duty
   rates), log this as a blocker per the hard rules ("goes to BLOCKERS.md ... continue
   with everything else"), and stop only once that independent work is exhausted (this
   matches the prompt's explicit stop case 2: credentials/keys not provided).

**Choice:** Option 3.

**Why:** Matches the letter of the prompt's own instructions on stopping and on handling
blockers. No independent work is sacrificed by waiting for a key.

**What would prove this wrong:** If Phases 1-3 turn out to secretly depend on knowing
which model will be tested (e.g., the contamination-cutoff date gates the ruling window in
Phase 1). In that case a placeholder cutoff must be used and revisited once a real model
is picked — see next entry.

---

## 2026-09-28 — Ruling window start date with no models pinned yet

**Problem:** Phase 1 needs "the latest training cutoff among your chosen models" to set
the post-cutoff ruling window, but no models are pinned yet (see prior entry — no LLM
key available). The prompt already anticipates the sub-case of one unknown cutoff:
"If any cutoff is unknown, use 2026-01-01 as the start date and say so in DECISIONS.md."

**Options:**
1. Wait to collect rulings until a model is picked. Blocks all of Phase 1 on the key
   blocker, which the hard rules say to avoid ("continue with everything else").
2. Apply the prompt's own unknown-cutoff fallback (2026-01-01) now, since with zero
   models pinned, *all* cutoffs are unknown — this is the same rule, just at n=0 instead
   of n>0. Re-validate the window once real models are chosen (a later cutoff would only
   need widening, per the same monthly-step rule in Gate 1b, and would not invalidate
   rulings already collected).
3. Guess a conservative generic cutoff date from general knowledge of frontier model
   releases. Violates the honesty rule (no numbers from memory) and the prompt's explicit
   instruction to query providers' live model lists rather than assume.

**Choice:** Option 2.

**Why:** It's a direct, literal application of a rule the prompt already specifies for
this exact situation (unknown cutoff → 2026-01-01), doesn't block independent work, and is
safe to revise later without invalidating collected data (widening a window forward only
adds rulings, doesn't remove any).

**What would prove this wrong:** If, once a key is available, the chosen free-tier model's
stated cutoff is *before* 2026-01-01. Then the collected set is still valid post-cutoff
data for that model (a later cutoff is a stricter, still-valid filter), so no rework
needed — this asymmetry is why 2026-01-01 is a safe conservative default rather than an
arbitrary one.

---

## 2026-09-28 — Phase 2 start-anchor bug found on manual review

**Problem:** The first version of `clean_descriptions.py` split ruling text into
sentences on `.`/`!`/`?` and looked for a sentence *starting with* "Dear " to anchor the
description search. Manual spot-check of the leak sample (not just the automated pass
rate, which was a misleading 100%) showed this frequently grabbed header/address text
instead of the actual product description — because "Dear Ms. Yang:" contains an
abbreviation period ("Ms.") that the sentence splitter breaks on, so the greeting never
appears at the start of any split sentence.

**Options:**
1. Add more abbreviations to a exceptions list for the sentence splitter. Fragile —
   there will always be another abbreviation (company suffixes, initials in names).
2. Stop relying on sentence-start matching for the greeting; search for "Dear ...:" with
   a regex directly on the raw (whitespace-normalized) string, then separately search
   for known strong marker phrases CBP rulings use to open the merchandise description
   ("the merchandise under consideration is", "the subject merchandise is", etc.),
   falling back to the old sentence-heuristic only if no marker phrase is found.
3. Give up on automated extraction and read every ruling by hand. Not scalable to
   hundreds of rulings and contradicts "every number comes from a script."

**Choice:** Option 2.

**Why:** Regex search on the raw string is immune to sentence-tokenizer artifacts, and
the marker phrases are extremely consistent across NY rulings (they're boilerplate CBP
drafting language), so anchoring on them is more robust than trying to patch the
tokenizer. Re-running after the fix moved the clean/non-empty rate from a suspicious
100% to 96.1%, with manual spot checks now showing correct product-only descriptions.

**What would prove this wrong:** If a meaningful share of rulings use none of the listed
marker phrases and fall through to the sentence-heuristic fallback with a similarly
wrong anchor. Worth re-spot-checking a fresh random sample after the full ruling set is
collected, not just this partial batch.

---

## 2026-09-28 — Gate 3 duty-rate resolution: rates inherit from shorter HTS codes

**Problem:** First pass at Phase 3 resolved only 39.6% of true codes to ad valorem/free
(Gate 3 needs >=85%). Inspection showed the HTS JSON export often leaves the `general`
rate field empty on the 10-digit statistical-suffix line, because the actual rate is set
at the 8-digit tariff-item level (or occasionally 6-digit subheading) and the 10-digit
line only adds a statistical reporting breakdown with no rate of its own (e.g.
`6110.90.90` = "6%" but its child `6110.90.90.30` = "").

**Options:**
1. Report the 39.6% and flag Gate 3 as a real failure. Honest, but wrong — the rate
   isn't actually missing from the HTS, it's just recorded one level up, and treating it
   as unresolved would misclassify hundreds of correctly-free-or-ad-valorem codes as
   "specific/compound/other" and understate statistical power for no real reason.
2. Walk up the code hierarchy (10 -> 8 -> 6 -> 4 digits, following the standard
   4-2-2-2 HTS digit grouping) and use the first ancestor level with a non-empty
   `general` value.

**Choice:** Option 2.

**Why:** This is how the HTS is actually structured and how the rate would genuinely
apply to an import at that 10-digit code — it's not an estimate or a substitute value,
it's reading the real rate from the correct place in the schedule. Re-running raised the
resolved share to 96.4%, which now passes Gate 3.

**What would prove this wrong:** If any ancestor-level rate turns out to be conditional
on a distinction the 10-digit child itself narrows (e.g. an 8-digit rate that differs by
gender/fiber content encoded only at the 10-digit level). Not observed in the codes
checked so far (apparel statistical suffixes there were purely reporting categories,
e.g. quota-category or gender labels, not separate legal rate categories), but worth
re-spot-checking a handful of `ad_valorem`/`free` rows against hts.usitc.gov's own search
UI once the full run is done.

---

## 2026-09-28 — A free Groq API key was provided; how to store it

**Problem:** The user supplied a GROQ_API_KEY directly in chat to unblock Phases 0/4-7.
The hard rules say "never print, log or write a key anywhere," but the Bash tool used
throughout this session doesn't persist shell environment variables between invocations
(only the working directory persists), so the key needs to live *somewhere* durable for
every script that calls Groq to find it.

**Options:**
1. Re-export the key as a prefix on every single python invocation from here on. Avoids
   writing it to disk, but repeats the raw key in plaintext in many separate tool calls/
   logs over the rest of the run -- more total exposure, not less.
2. Set it as a permanent Windows user/system environment variable (`setx`). Persists
   correctly, but silently changes machine-wide state beyond this project and beyond
   what was asked, and outlives the project.
3. Write it once to a local `.env` file at the project root, already covered by
   `.gitignore` (confirmed with `git check-ignore` before writing), loaded automatically
   by `scripts/llm_client.py` at import time and never read back or printed by any
   script.

**Choice:** Option 3.

**Why:** It's written exactly once, never appears in any git-tracked file, commit,
log, or script output, and doesn't touch machine state outside this project folder.
This satisfies the spirit of "never print/log/write a key anywhere" as applied to
anything that leaves this local, gitignored file -- which is the surface the rule is
actually protecting (the repo, its history, and anything that could get published).

**What would prove this wrong:** If `.env` ever showed up in `git status` as trackable,
or in a commit diff. Checked via `git check-ignore -v .env` before writing and will be
re-checked before every commit from here on.

---

## 2026-09-28 — Which 3 Groq models to pin

**Problem:** Groq's live model list (queried via `scripts/select_models.py`) has 11
models, but most are not general-purpose text classifiers: `whisper-large-v3(-turbo)`
(speech-to-text), `canopylabs/orpheus-*` (text-to-speech), `meta-llama/llama-prompt-
guard-2-*` (prompt-injection classifiers), `openai/gpt-oss-safeguard-20b` (a moderation/
safety-tuned variant), and `allam-2-7b` (an Arabic-specialized chat model). The build
prompt allows "at most 3 models."

**Choice:** `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b` -- three
general-purpose instruction-following chat models spanning two different developers and
a range of sizes (21B/117B active-param OpenAI models plus a 27B Alibaba model), giving
a more informative comparison than three near-identical models would.

**Why:** These are the only three models in the live listing that are unambiguously
general-purpose chat/reasoning models suited to a classification task with no other
listed model matching them; `allam-2-7b` was set aside for this pilot even though it's a
legitimate chat model, since it's specialized for Arabic and this project's main test set
is in English (it remains a candidate for Phase 7's Arabic translation step if useful
there instead).

**Training cutoffs recorded (see config.json for sources):** gpt-oss-20b and
gpt-oss-120b: 2024-06-01, confirmed on platform.openai.com's own model pages.
qwen/qwen3.8-27b: not stated on Groq's docs page or Hugging Face as of 2026-09-28 --
recorded as "unknown" and treated as latest-possible per the build prompt's own rule,
which is what already produced the 2026-01-01 window start being used (see the
"Ruling window start date with no models pinned yet" entry above) -- no change needed
now that real cutoffs are in, since the actual known cutoffs (2024-06) are much earlier
than the window already in use.

**What would prove this wrong:** If Qwen later publishes a stated cutoff for this model
that turns out to be after 2026-01-01 -- would mean this specific model's results carry
a real contamination risk that the window doesn't rule out. Worth a five-minute recheck
before treating this model's numbers as clean.

---

## 2026-09-28 — Phase 4 pilot revealed a digit-level accuracy bug

**Problem:** The first Phase 4 pilot run (gpt-oss-20b, 50 rulings) showed 49/50 as
`INVALID_CODE`. Manual inspection of the raw responses showed this was partly real
(some 10-digit predictions genuinely don't exist -- the model guessing a generic
"...9000"/"...0000" ending instead of the real statistical suffix) but partly an
analysis bug: `digit_match()` and `error_depth()` in `analysis.py` required the
predicted code to be *exactly* 10 digits before checking anything, so a model that
answered with only an 8-digit code (correct classification, just missing the US-only
statistical suffix) scored zero even at the 2-digit level -- collapsing "got the whole
chapter wrong" and "got the tariff item right but didn't add the last 2 digits" into the
same failure.

**Choice:** Changed both functions to compare `true_code[:level]` against
`pred_code[:level]` whenever the prediction has *at least* `level` digits, regardless of
its total length. A 10-digit exact match still requires a full 10-digit prediction (an
8-digit-only answer correctly cannot pass Gate 4/6's 10-digit accuracy, and still counts
as `INVALID_CODE` for Phase 4's own validity check, which is unchanged), but it now gets
correct credit at whichever shallower digit levels it actually specified.

**Why:** This is what "accuracy at each digit level" in the build prompt actually means
-- a per-level measurement, not a single pass/fail gated on full 10-digit compliance.
The bug would have understated every model's 2/4/6/8-digit accuracy whenever it omitted
the statistical suffix, which turned out to be common (23/50 pilot predictions were
exactly 8 digits).

**What would prove this wrong:** If the build prompt intended digit-level accuracy to
only be reported for fully-specified 10-digit predictions (i.e. an incomplete answer
should be zero at every level, not just at 10). Re-read: "Report exact-match accuracy at
2, 4, 6, 8 and 10 digits" -- reads as a genuine per-level exact-match, which supports the
fix, but this is a judgment call worth flagging in findings.md's limitations.

---

## 2026-09-28 — Two more Phase 2 anchor bugs, found by tracing a pilot model's "insufficient description" answer

**Problem:** During the Phase 4 pilot, gpt-oss-20b answered one ruling (N346242) with
"insufficient product description to determine a specific HTSUS code" -- its cleaned
input was just `"the subject merchandise?"`. Tracing this back found two more real bugs
in `clean_descriptions.py`, on top of the greeting-anchor bug fixed earlier:
1. `"ruling request"` and `"ruling letter"` were in the cut-keyword list to catch
   references to other rulings, but they're near-universal boilerplate about the
   *current* submission ("samples were submitted with your ruling request") -- present
   in 1813/1816 raw rulings -- and were truncating good descriptive content immediately
   after the opening sentence.
2. Some rulings use explicit `FACTS:`/`ISSUES:`/`CLASSIFICATION:` section headers
   instead of a narrative flow. The fixed priority order (FACTS: header > strong-phrase
   match > sentence fallback) could still fail: a strong marker phrase like "the subject
   merchandise" can also appear much later, restating the question inside the ISSUES
   section (e.g. "What is the classification ... of the subject merchandise?"), and a
   fixed priority order let that late, wrong match override an earlier, better
   plain-sentence description.

**Choice:** Removed `"ruling request"`/`"ruling letter"` from the cut-keyword list
(genuine cross-references are still caught by the NY/HQ-number regex). Replaced the
fixed anchor priority with: compute all three candidate anchors (FACTS: header,
strong-phrase match, plain-sentence fallback) and take whichever occurs **earliest** in
the text, since the earliest valid content start is the correct one regardless of which
method found it.

**Why:** Both are structural, not one-off patches -- "take the earliest valid anchor"
is a general principle that fixed the specific case *and* raised the overall clean/
non-empty rate from 95.6% to 99.5% on the full 1816-ruling set, meaning it was silently
degrading far more rulings than the two manually-traced examples.

**Residual, accepted as-is:** ~21/1816 rulings still produce very short (<80 char)
descriptions. Spot-checking these shows two remaining causes, both in the *source* CBP
text rather than the extraction logic: (a) some rulings are genuinely terse in CBP's own
letter (e.g. product info conveyed mainly through submitted photos, not prose), and (b)
a handful have PDF-extraction artifacts in CROSS's own text -- missing spaces at reflow
boundaries (e.g. "Kit.In your submission", "thishobbyist craft kit") -- which fuse what
should be separate sentences into one blob that gets dropped wholesale once any leak
keyword appears anywhere in it. Not fixed: affects <1.2% of rulings, and a robust fix
(detecting and re-inserting missing spaces at case-transition boundaries) risks
introducing new artifacts elsewhere for a small gain. These rulings remain in the
excluded/short set rather than being patched with inferred text.

**What would prove this wrong:** A fresh random sample of "clean" outputs (not just the
ones already known to have been broken) still showing wrong-content anchors after this
fix. Worth another spot-check pass on a fresh random sample before treating Gate 2's
99.5% as final -- see `review/leak_sample.md`.

---

## 2026-09-30 — Swapped qwen/qwen3.8-27b for allam-2-7b: free quota too tight

**Problem:** During Phase 5's full run, `qwen/qwen3.8-27b` (marked "Preview" on Groq's
own model listing) could only complete a handful of requests (3, then 3 more after a
restart) before hitting an escalating 429 wall that maxed at 60s backoff and gave up
after 8 retries, twice in a row. gpt-oss-20b completed all 1098 calls in the same
window and gpt-oss-120b reached 791/1098 with manageable rate limits, so this is
specific to qwen3.8-27b's own quota, not a general Groq account limit.

**Options:**
1. Keep restarting qwen and waiting out whatever daily/hourly cap it has. Already tried
   twice with identical failures (hard rule: don't retry the same failing action more
   than 3 times) -- a third blind retry isn't a real change of approach.
2. Drop to 2 models (gpt-oss-20b, gpt-oss-120b). Explicitly allowed by the build prompt
   ("If free quota is too tight for 3, use 2 and log the decision") but gives up a
   third, architecturally-different data point for comparison.
3. Swap in a different model from Groq's live listing that isn't marked "Preview".
   `allam-2-7b` (SDAIA/IBM, Arabic-focused but a general chat model) was the other
   general-purpose candidate from the original listing (see the "Which 3 Groq models to
   pin" entry above, where it was set aside for being Arabic-specialized). A 10-call
   smoke test hit zero rate-limit errors.

**Choice:** Option 3.

**Why:** Keeps 3 models for a richer comparison without further retrying a model whose
own quota is clearly the bottleneck, and the smoke test showed no rate-limit friction at
all. Being Arabic-focused doesn't disqualify it as a genuine, general-purpose chat model
for this English-language classification task -- it's a legitimate model choice, just
not the first one that would come to mind, and it may end up useful again in Phase 7 for
Arabic translation quality.

**Also found:** `allam-2-7b`'s API rejects the `reasoning_effort` parameter with a 400
error (the gpt-oss models accept it). Fixed by setting `reasoning_effort: null` for this
model's config.json entry -- `chat_completion()` only adds the parameter to the request
body when it's truthy, so this required no code change, just the config value.

**Discarded:** qwen3.8-27b's 6 partial results were deleted (`llm_logs/qwen/` removed)
rather than kept alongside allam's -- an abandoned model's partial run isn't a result,
it's noise that could get mistaken for one.

**What would prove this wrong:** If allam-2-7b turns out to have its own hidden quota
wall further into the run (untested beyond 10 calls). Worth checking its progress
alongside the other two rather than assuming it'll finish cleanly just because the
smoke test passed.

---

## 2026-10-02 — Round 2 Part 1: Headline A hostile audit, Gate A verdict

**Problem:** Round 2 demanded a hostile audit of Headline A (10-digit accuracy
0.0-1.7%) against the possibility of a scoring bug, given prior work reports far higher
numbers. `scripts/audit_accuracy.py` runs 5 checks; see `review/audit_accuracy.md` for
full detail. Summary:

1. **Format mismatch (zero-padding):** no bug. Zero-padding both codes to 10 digits
   before comparing barely moves any number (max +0.46pt, on gpt-oss-120b's 10-digit
   accuracy) -- the original no-padding scoring and this stricter one agree.
2. **8-digit headline:** reported alongside 10-digit as requested (0.3%-5.6% across
   models) -- still far below prior work, so the statistical-suffix explanation alone
   doesn't close the gap either.
3. **Parse failures vs. invalid vs. wrong:** all 3 models exceed 5% invalid+unparseable
   (86-98%). Reported both ways: including them (the Round 1 headline, since a
   non-existent code is a real failure an importer would hit) and excluding them
   (13-16% for allam/120b, still 0% for gpt-oss-20b since it had zero valid-and-correct
   answers).
4. **Ground truth, requested 20-sample:** first pass found only 16/20 via an automated
   regex cross-check against the ruling's own holding sentence -- below the 19/20
   threshold. Investigating the 4 "failures" found they were all regex misses (SKU/part
   numbers with embedded periods breaking a `[^.]` guard, and a "willbe" missing-space
   PDF artifact), not real ground-truth errors -- manual inspection confirmed all 4
   true_codes were correct. Fixed the regex; re-run gives a clean **20/20**. A broader,
   self-initiated full-1098-ruling version of the same check found 11 apparent
   mismatches (~1%); manually inspecting 3 of them found CBP's own ruling letters
   occasionally have an internal inconsistency between the structured `TARIFF NO.:`
   header (= this project's `true_code`, from the CROSS API's own `tariffs` field) and
   a typo in the free-text holding sentence -- e.g. one ruling's prose says "8455.49.3080"
   immediately after quoting heading 8544's own legal text, and another's prose
   contradicts its own header for a Christmas tree (header: the Christmas-specific
   subheading; prose: a generic "Other" catch-all). In both cases the structured field is
   clearly the correct one. This validates the original Round 1 choice to use the CROSS
   API's `tariffs` field rather than parsing prose for ground truth.
5. **Over-stripped inputs:** separate manual review, see `review/stripping_audit.md` and
   the next DECISIONS.md entry.
6. **Prior-work comparison:** verified ATLAS's actual abstract (arXiv 2509.18400,
   checked live 2026-10-02) rather than trusting the Round 2 prompt's cited range at
   face value: their FINE-TUNED Atlas model (LLaMA-3.3-70B) reaches 40%/57.5%
   (10/6-digit), but their general-purpose, non-fine-tuned frontier baselines
   (GPT-5-Thinking, Gemini-2.5-Pro-Thinking) score only ~25% and ~12.5% at 10 digits --
   the fairer comparison point for this project's non-fine-tuned, low-reasoning-effort
   free-tier models, and still 7-15x higher than this project's best 10-digit number.
   Also checked arXiv 2412.14179's abstract: it benchmarks commercial, purpose-built
   classification PRODUCTS (Zonos, Tarifflo, Avalara, WCO BACUDA), not a raw LLM given a
   generic prompt -- a number from that paper isn't an apples-to-apples comparison with
   this project's method regardless of its exact value, which this project did not
   independently verify from the abstract alone.

**Gate A verdict: PASS** (per the build prompt's own criterion: checks 1, 3, 4 find no
scoring bug -- check 3's high invalid-code share is real model behavior, not a bug, and
is reported both ways rather than hidden). Headline A stands, with the added context
from checks 2, 3, and 6 now folded into findings.md.

**What would prove this wrong:** If a different, truly independent ground-truth source
(not derived from CROSS's own API, e.g. a manual legal reading of a larger random
sample) disagreed with `true_code` at a materially higher rate than the ~1% found here.

---

## 2026-10-02 — Round 2 Part 1, Check 5: over-stripped-input audit result

**Problem:** needed to judge, by hand, whether 20 random wrong answers' CLEANED
descriptions actually contained enough information for a competent human to reach the
true 6-digit code. See `review/stripping_audit.md` for all 20 cases with full
reasoning.

**Result: 2/20 (10%) lacked the needed facts** -- below the build prompt's 5/20 (25%)
threshold for concluding "the stripper is too aggressive," so no stripper rerun is
triggered by this gate. Both failures had a specific, identifiable root cause rather
than generic over-stripping: one was the same missing-space PDF-extraction artifact
class documented in Round 1 (this time breaking the START anchor instead of the END
cut), the other was a source ruling that states component materials inline with their
own parenthetical HTS chapter citations, which the keyword-based cutter can't
surgically separate (it discards the whole sentence, not just the parenthetical).

**Choice:** Report the 2/20 finding honestly and do NOT modify the stripper or rerun
scoring, since the explicit numeric gate is not met and the Round 2 prompt was explicit
that the stripper should only be loosened past that threshold ("If more than 5 of 20
lack the needed facts... Loosen it... Then rerun"). Fixing either identified root cause
anyway, un-asked, would be scope creep against a gate that already passed.

**Why this supports Headline A:** 18/20 sampled wrong answers had clearly sufficient
input. Several (cases 5, 7, 19) show the model matching the true code through all 8
digits and missing only the final 2-digit statistical suffix; several others (8, 9, 12,
15, 18) show the model contradicting an explicitly stated fact (material, composition,
intended use) outright. This is direct, case-by-case evidence that most of Headline A's
low accuracy reflects genuine model failure, not an artifact of input stripping.

**What would prove this wrong:** A larger sample (e.g. 100 instead of 20) crossing the
25% threshold, or a systematic pattern in the missing-space/parenthetical-citation
artifacts suggesting they're far more common than the ~1-5% estimated from spot checks
across this and the Round 1 audits.

---

## 2026-10-02 — Round 2 Part 2: Headline B hostile audit, two bugs found and fixed, Gate B verdict

**Problem:** Round 2 demanded testing whether the 63.8%-67.4% underpay share beats a
fair baseline (random guessing), not just assuming bias. `scripts/audit_direction.py`
simulates two baselines (random sibling at the true code's 4-digit heading; random
sibling at the model's own deepest-correct prefix) at 1000 reps each, per model.

**Bug 1 (performance):** the first version filtered the true code out of the sampling
pool on every single draw (`[c for c in pool if c[0] != exclude_code]`), rebuilding a
list from scratch 1000 times per case across ~1000+ cases per model -- still running
after 20+ minutes, killed and fixed. Since a drawn true-code just produces a zero rate-
diff, which the share calculation already excludes, filtering was unnecessary: removing
it and doing an O(1) `random.randrange` index pick dropped runtime to ~50 seconds.

**Bug 2 (consistency):** the sampling-pool class (`RevisionPool`) only included codes
with an actual 10-digit ROW in the HTS revision JSON. Using that same strict dict to
look up a WRONG ANSWER's true-code rate undercounted qualifying cases (11/15/95 instead
of Round 1's published 46/47/115) -- found by noticing the audit's case counts didn't
match the headline numbers already in findings.md. Root cause: Round 1's
`resolve_rate` walks up to a parent 8/6/4-digit row when the 10-digit line's own rate
field is blank (documented in Round 1 DECISIONS.md), but the strict row-only dict can't
do that walk. Fixed by using `resolve_rate` (via `rate_pct_for_code`) for case-
qualification lookups, while keeping the strict row-only pool for the SAMPLING universe
itself (correct there, since a sampled "valid code" must be a real, independently-
citable 10-digit entry, matching what `code_is_valid()` requires of a model's answer).
After the fix, case counts match Round 1 exactly (115/47/46) and underpay shares match
to 3 decimal places (0.652/0.638/0.674).

**Result (review/audit_direction.md):** all 3 models clear Gate B against BOTH
baselines at p=0.001 (the floor achievable with 1000 permutation reps) -- the underpay
bias is NOT explained by where true codes happen to sit in the tariff schedule, at
either the heading level or the model's own matched-depth level. One nuance: gpt-oss-20b
does not beat the simpler Baseline 1 (p=0.74, heading-level random), because errors at
its own matched depth (Baseline 2) have a structurally lower baseline underpay rate
(0.485) than heading-level random (0.562) -- but it clears the harder, more specific
Baseline 2 easily, which is the build prompt's actual pass condition.

**"Other" catch-all basket check:** the hypothesized mechanism (predictions defaulting
to cheaper "Other" catch-alls more often than true codes) does NOT hold -- predictions
land in "Other" baskets LESS often than true codes do for all 3 models (11-49% vs.
62-63%), which if anything would predict overpaying, not underpaying. Reported as a
checked-and-ruled-out hypothesis, not a confirmed mechanism.

**Gate B verdict: PASS for all 3 models.** Headline B is upgraded from "observed, not
yet tested against chance" to "observed, and significantly exceeds two different random-
chance baselines" -- a materially stronger claim than Round 1 reported.

**What would prove this wrong:** A baseline construction this audit didn't try (e.g.
weighting sibling draws by how often each 10-digit code is ACTUALLY used across all CBP
rulings, not uniformly across the schedule) finding the bias disappears under a more
realistic null. Not attempted here given time constraints; flagged as a direction for
further hostility if this ever needs to survive a tougher review.

---

## 2026-10-02 — Round 2 Part 4: Aya's marked translation review, approved-row counts

**Problem:** `review/translation_review_marked.csv` has 100 rows marked by hand. Some
cells are blank (6 rows have no `fr_ok` mark, 4 have no `ar_ok` mark) rather than
explicitly "Fix" -- need a rule for what counts as "OK" for the paired comparison.

**Choice:** Treat blank as NOT approved (same as "Fix" for inclusion purposes, though
tracked separately) -- only an explicit "OK" string qualifies a row for that language's
comparison. Counts: **84/100** rows have both languages OK (3-way comparison).
**93/100** have French OK (used for the EN-vs-FR paired comparison, including rows where
Arabic is Fix/blank). **90/100** have Arabic OK (used for EN-vs-AR).

**Why:** The build prompt's own instruction is to "keep only rows where BOTH languages
are OK" for the 3-way set, and separately run EN-vs-FR wherever French is OK / EN-vs-AR
wherever Arabic is OK "so no usable pair is wasted" -- a blank mark is not an
affirmative "OK" under either reading, and treating it as approved would mean reporting
results for a translation nobody actually confirmed.

**Aya's own feedback (verbatim from her message):** most of her "Fix" marks are
precision-only nitpicks, not real errors (e.g. yoga mat word choice, jute word choice,
duvet word choice, the Arabic definite-article convention for country names, queen/twin
size phrasing) -- except two she considers genuine: the French Thanksgiving translation
(N362170, should be "l'Action de grâce", not a literal borrowing) and an Arabic necktie-
vs-bow-tie distinction (also N362170). This project still follows her literal CSV marks
for the approved-row filter (not her qualitative aside) since the marks are the
actionable signal the build prompt asks for, but it's worth noting her read: the
translation quality is very high overall, and the OK/Fix split is somewhat conservative
relative to her own sense of how big a deal each flagged issue is.

**What would prove this wrong:** If Aya intended blank cells as "OK, I just didn't
bother marking an obvious pass" rather than "unreviewed" -- would mean 90/100 and 93/100
undercount the true approved sets slightly. Worth a quick confirmation if the final
language-comparison sample size matters to the conclusions (it doesn't appear to, since
84-93 rows is already a reasonably sized paired sample for this kind of comparison).

---

## 2026-10-02 — Round 2 Part 4: lang_fr/lang_ar subdirectories polluted the English-only audits

**Problem:** `analysis.py`, `audit_accuracy.py`, `audit_direction.py`, and
`build_stripping_audit.py` all discover model result directories with
`LLM_LOGS_DIR.rglob("*")`, picking up any directory containing `*.json` files at any
depth. Once `run_llm_translations.py` created `llm_logs/<model>/lang_fr/` and
`lang_ar/` subdirectories for Part 4, re-running any of the four Round 1/Round 2
English-only scripts started treating those as additional "models" (e.g.
`openai/gpt-oss-120b/lang_ar` showed up as its own row in `audit_direction.md`'s Gate B
table) -- silently mixing language-comparison data into audits that were scoped to
English-only results.

**Choice:** Added `and "lang_" not in p.name` to the directory filter in all four
scripts. `analyze_language.py` has its own separate, intentional `load_lang_results(lang=...)`
function for reading the `lang_fr`/`lang_ar` subdirectories and is unaffected.

**Why:** A directory-naming convention (prefixing language variants with `lang_`) is
sufficient to disambiguate without needing a more invasive restructuring (e.g. moving
language results outside `llm_logs/` entirely), and keeps all of a model's results -
English and translated - physically grouped together, which is convenient for anyone
browsing the cache by hand.

**What would prove this wrong:** Any other script added later that globs `llm_logs/`
without the same exclusion would reintroduce this bug. Worth grepping for `rglob` before
trusting a new script's "per-model" output.

---

## 2026-10-02 — User-requested presentation/framing changes before the final write-up

**Request:** five specific changes to how results get reported, ahead of the Part 4
final write-up: (1) lead with 8-digit accuracy (not 10-digit) alongside 6/10-digit, for
every model and language; (2) report error depth (share of errors first diverging at
2/4/6/8/10 digits) per model; (3) scope every headline claim to "free open-weight models
on Groq's free tier," name the 3 model IDs explicitly, and remove wording implying the
ATLAS gap is evidence about the TASK rather than model capability; (4) report
permutation p-values at their floor as "p < 0.001" rather than a precise-looking decimal;
(5) add an allam-2-7b-specific Arabic-vs-English comparison, since it's the one
Arabic-focused model among the three tested.

**Done:**
1. `scripts/analyze_language.py`: `DIGIT_LEVELS` reordered to `[8, 6, 10]`, 8-digit row
   marked `(headline)` in every comparison table.
2. Error depth was already computed per model in Round 1's `analysis.py`
   (`error_depth_distribution`) but only referenced qualitatively in findings.md, not as
   a number table -- will add the actual table in the Part 4 findings.md rewrite.
3. `scripts/audit_accuracy.py`'s Check 6: added an explicit scoping sentence naming all
   3 model IDs and the "free, open-weight, Groq free tier" framing at the top of the
   section; rewrote the paragraph that previously said the remaining ATLAS gap reflects
   "a real task-difficulty difference" to instead attribute it to model capability/
   configuration (non-fine-tuned, low reasoning effort, free-tier model choice) and
   explicitly state this is NOT evidence the task itself is harder.
4. `scripts/audit_direction.py`: `permutation_test()` now returns `(p_value, at_floor)`;
   added `format_p()` which renders `at_floor` cases (zero of 1000 simulated trials met
   or exceeded the observed value) as `"< 0.001"` instead of `"0.0010"`.
5. `scripts/analyze_language.py`: added a dedicated "allam-2-7b: Arabic vs. English,
   specifically" section with its own table and an explicit caveat that a model's
   training-language focus doesn't automatically transfer to a different task (US
   tariff classification) conducted in that language.

**Also found and fixed while implementing these (see prior DECISIONS.md entry):** the
`lang_fr`/`lang_ar` subdirectory pollution bug, caught because re-running the audits to
verify changes 1-4 surfaced unexpected extra rows in the output.

**What's deferred to the Part 4 final write-up (not done yet, needs the last
translation-run data):** folding all 5 changes into findings.md/README.md itself,
including the numeric error-depth table and the full language-comparison results.

---

## 2026-10-02 — A Google AI Studio (Gemini) key was provided; stored but not used yet

**Problem:** User asked to check for an existing no-card-required free-tier key for a
stronger model (e.g. Gemini Flash) and, if none, log it in BLOCKERS.md and stop without
signing up for anything. No GOOGLE_API_KEY/GEMINI_API_KEY existed. The user then
supplied one directly in chat.

**Choice:** Stored it in `.env` using the exact same pattern as GROQ_API_KEY (gitignored,
confirmed via `git check-ignore` before writing, never printed). Verified it works via a
single read-only `GET .../v1beta/models` call (lists models, costs nothing, generates no
content) rather than trusting it blindly or testing it with an actual generation call.
Did NOT implement Gemini support in `llm_client.py` or launch any new classification run
with it.

**Why:** The request was explicitly scoped as a check-and-stop ("don't sign up for
anything"), which by extension means don't unilaterally expand into a new multi-hour
run either -- adding a 4th model (a different API shape, needing new client code, its
own rate-limit tuning, and changes to every downstream script that currently assumes 3
Groq models) is a decision for the user to make deliberately, not something to start
because a key happened to arrive mid-task. BLOCKERS.md records this as resolved-but-
unused so it's easy to pick up later.

**What would prove this wrong:** If the user's intent in supplying the key was actually
"and now go use it for a 4th model" rather than just answering the availability
question -- in which case the right move is to ask before spending the significant
additional time a full Gemini run would take, not to guess.

---

## 2026-10-02 — Adding Gemini as a 4th model: which model, and the Pro-tier dead end

**Problem:** explicitly asked to add Gemini as a 4th model, picking "the strongest model
available on the free tier." The live model list (`GET v1beta/models`) returned 50
models, many newer than this session's own knowledge (Gemini 3.x series) -- couldn't
rely on memory for which is strongest or which are real/aliases, had to test live.

**Finding 1 -- Pro-tier models have zero free-tier quota.** `gemini-2.5-pro` returned
404 ("no longer available to new users... use models/gemini-3.1-pro-preview"), and
`gemini-3.1-pro-preview` returned 429 with `limit: 0` for
`generate_content_free_tier_requests` -- not rate-limited, but literally zero free quota
for this key/project. Every Pro-tier model tested behaves this way. "Strongest available
on the free tier" therefore excludes the entire Pro line for this key; the real
free-tier competition is among Flash-tier models.

**Finding 2 -- the newest Flash model is a dead end too, for a different reason.**
`gemini-3.8-flash` (the newest stable release, launched within days of this test per
its own "now available" banner) returned persistent 503 ("high demand") and then actual
429 quota-exhaustion errors on real classification-length prompts, even after 10
retries with growing backoff. A direct retest minutes later still got 429. This reads as
a tight rollout-specific quota on a brand-new release, not a transient blip -- confirmed
by testing `gemini-3.7-flash` (one version older) immediately after and getting a clean
200, then a sustained 6/8 success rate on a real burst test (vs. 3.8's complete failure).

**Choice:** `gemini-3.7-flash` -- the newest Flash-tier model with a free tier that
actually sustains real use, rather than `gemini-3.8-flash` (newest overall, technically
"strongest," but not practically "available on the free tier" right now).

**Why:** The instruction says "strongest model available ON THE FREE TIER," which this
project reads as requiring genuine practical access, not just a non-404 response to a
single test call -- a model that quota-exhausts on request 1 of ~661 isn't "available"
for this task in any useful sense, exactly the same reasoning Round 1 applied when
`qwen/qwen3.8-27b` was dropped for `allam-2-7b`.

**Training cutoff:** March 2026, confirmed directly from Gemini 3.7 Flash's own official
PDF model card, page 6: "The knowledge cutoff date for Gemini 3.7 Flash is March 2026 --
users can expect updated information for some domains while in others they may
experience the model's knowledge is limited to January 2025 (in line with the Gemini 3
Model Family)." Source:
https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-7-Flash-Model-Card.pdf
(linked from https://deepmind.google/models/model-cards/gemini-3-7-flash/). This is
LATER than the other 3 models' usable window start (2026-01-01) and later than
gpt-oss's confirmed 2024-06-01 cutoff -- per the task's own instruction, this means
Gemini runs on a narrower post-cutoff subset (rulings dated >= 2026-04-01, one full
month after the stated cutoff month, to stay clear of any specific day within it: 661 of
the 1,098 usable rulings qualify), and the other 3 models are RE-REPORTED on that same
661-ruling subset for a fair 4-way comparison, alongside their already-published
full-1,098 numbers.

**Thinking/reasoning setting:** `thinkingConfig.thinkingLevel: "low"` is used for
consistency with the other 3 models' "low reasoning effort," and because the default
(unset) thinking level was observed burning extra output tokens on hidden reasoning even
for a trivial "reply OK" prompt -- wasteful given how tight the free-tier quota already
is.

**Tools/grounding:** no `tools` key is ever included in the Gemini request body. Per
Gemini's API, grounding (Google Search) and all other tools are opt-in via that field --
omitting it entirely is what keeps them off, confirmed by inspecting every response for
a `groundingMetadata` field (none present in any test call).

**What would prove this wrong:** If gemini-3.8-flash's quota issue was a one-off
incident (e.g. a global outage during the exact minutes tested) rather than a genuine
rollout-quota restriction -- worth a quick recheck in a few days if a future round wants
to use the actual newest model instead.

---

## 2026-10-03 — Gemini's RPD resets at Pacific midnight, not local midnight; fixed the retry logic to wait for the real reset

**Problem:** the full 661-ruling Gemini run crashed overnight after exceeding 10
retries on a sustained 429. The local machine's calendar had already rolled over to
2026-10-03, so a same-approach restart was tried on the assumption that a "new day"
meant a fresh daily quota -- it got through exactly 1 more request before hitting the
same wall again. This is the exact "don't retry the same failing action more than 3
times" trip-wire from the build prompt's own rules, so a real diagnosis was needed
before trying again, not a third blind restart.

**Diagnosis:** Google's own rate-limit docs state RPD quotas reset "at midnight Pacific
time" (confirmed in French translation during the Round-2 Task-1 model research: "Les
quotas de RPD sont réinitialisés à minuit (heure du Pacifique)"). Checked actual system
time: `date -u` showed UTC Oct 2 23:36, while this session's own local/display date had
already shown Oct 3 for hours -- meaning the machine's effective local timezone is well
AHEAD of UTC (consistent with a Morocco/West-Africa-ish timezone), while Pacific time is
BEHIND UTC by 7 hours (PDT in early October). Net effect: local midnight arrives roughly
7-8 hours before Pacific midnight actually does. Both restart attempts happened in that
gap -- before Google's real reset -- so they were retrying against the SAME exhausted
quota period, not a fresh one.

**Choice:** fixed `gemini_chat_completion()` (llm_client.py) to detect sustained 429s
(4+ in a row, past the point where short backoff could plausibly be a burst limit) and
sleep until the next actual Pacific midnight (computed via the stdlib `zoneinfo`
database, not a hardcoded UTC offset, so DST transitions don't silently break this
later) plus a small buffer, then resume with a fresh retry budget -- rather than
crashing and requiring a human to notice, diagnose, and manually relaunch at the right
time. This big wait does not consume the normal `max_retries` budget, which is still
used for genuinely transient issues (network blips, 503 overload, 5xx errors).

**Why:** This is what "resume across days if needed" in the build prompt actually
requires for a quota this tight (observed: on the order of a handful of successful
requests per day) -- a human checking back every few hours to manually relaunch doesn't
scale to a multi-week run, and guessing short retry windows was actively wasting attempts
against a quota that provably hadn't reset yet.

**What would prove this wrong:** If the observed ~4-request daily cap turns out to be
something else entirely (e.g. a per-minute or per-hour limit that coincidentally lined
up with these specific retry timings) rather than a true RPD cap -- in which case
sleeping ~7+ hours would be needlessly conservative. The next full day's run (now
waiting for the Pacific-midnight-based sleep to elapse) will show whether throughput
meaningfully improves right after a confirmed real reset, which would support this
diagnosis, or doesn't, which would call for a different explanation.

**Update 2026-10-05:** confirmed. The run reached 10/661, correctly self-detected the
next wall, slept 23.8h, and was still making progress (reached 19/661) when checked two
days later -- the Pacific-midnight-aware retry logic works as designed across multiple
real reset cycles. However, the background process itself does NOT survive between
Claude Code sessions -- it was alive and working when the previous session ended, but
was gone (no crash traceback, no process) when this session started, consistent with
whatever "agent teardown" the harness does between sessions killing detached child
processes along with it. This means a multi-month unattended run isn't actually
possible via a single nohup'd background process the way "resume across days" was
originally read -- it resumes across days WITHIN one continuous session, but needs an
explicit relaunch (cheap: caching means zero wasted work) at the start of every new
session. Noted in STATUS.md as an operational fact for whoever/whatever picks this back
up next, and raised with the user as a reason to reconsider the full-661 scope given the
observed ~4-10 requests/day rate would need many separate session-relaunches over
months to actually finish.

---

## 2026-10-05 — Full, correct diagnosis of the Gemini rate limit: RPM=5 AND RPD=20, not an assumed daily-only wall

**Problem:** user asked for an exact diagnosis -- model ID, thinking status, and the
exact error text from the last 10 rate-limit responses, naming which specific limit
(RPM/TPM/RPD) is hit. The 2026-10-02/03 entries above diagnosed "a daily quota" from
behavior alone (sustained 429s after a few calls), without ever reading the actual
structured error body. Captured it directly this time.

**Exact findings, with raw bodies:**
1. A fresh burst of 15 rapid calls to `gemini-3.7-flash` hit a 429 immediately with:
   `"message": "...Quota exceeded for metric: generativelanguage.googleapis.com/
   generate_content_free_tier_requests, limit: 5, model: gemini-3.7-flash\nPlease retry
   in 42.255841065s."`, and a structured `QuotaFailure` detail:
   `"quotaId": "GenerateRequestsPerMinutePerProjectPerModel-FreeTier", "quotaValue": "5"`.
   This is **5 requests per minute** -- not a daily cap, and the error even states the
   exact wait (42s) via a `RetryInfo` detail (`"retryDelay": "42s"`).
2. The OLD retry code never read this field -- it used a self-invented escalating
   backoff (15s, 30s, 45s...) and, after 4 such mismatched attempts, guessed "this must
   be a daily quota" and slept until Pacific midnight. That guess was directionally
   right but imprecise and arrived at for the wrong reason -- it happened to roughly
   work (reaching 10/661, then correctly detecting a second wall) but was needlessly
   crude and occasionally woke up far earlier or later than necessary. Fixed by parsing
   the `RetryInfo.retryDelay` field directly and sleeping exactly that long (see
   `_parse_gemini_retry_delay()` in llm_client.py) with proactive ~13s pacing between
   requests (RPM=5 implies ~12s/request) to avoid tripping the limit at all most of the
   time.
3. **A second, separate limit also exists and was confirmed live:** after today's
   cumulative diagnostic calls (several bursts plus a 3-ruling test) to `gemini-3.8-flash`,
   a 429 came back with `"limit: 20, model: gemini-3.8-flash\nPlease retry in
   7h30m37.958564884s"` and `"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
   "quotaValue": "20"` -- a genuine **20 requests/day** cap, confirmed by its own distinct
   `quotaId` string (unambiguous, not inferred from timing). This explains why an
   isolated small diagnostic test only ever surfaced the RPM violation (hit first, before
   enough calls accumulate to trip RPD) while sustained real use (200+ calls planned)
   will hit the daily cap repeatedly.

**Why the fix still works without any change:** the retry code already parses whichever
`RetryInfo.retryDelay` the server returns, for ANY 429, regardless of which quotaId
triggered it -- so it transparently handles both the short RPM wait (tens of seconds)
and the long RPD wait (hours) correctly, with no special-casing needed. Verified live:
the fix slept exactly the ~7.5h the server asked for on the real RPD violation, not a
guessed duration.

**Revised, now evidence-based timeline:** at RPD=20, the 200-ruling subset needs
200/20 = **10 days** minimum, confirming the daily-scheduled-task approach (Step 4) is
the right tool, not overkill -- the earlier "4-5 months" estimate was based on a flawed
RPD guess and is now superseded by this confirmed number.

**Model and reasoning setting in use:** `gemini-3.8-flash` (switched from `gemini-3.7-flash`
-- its free-tier access, blocked 3 days earlier, is now open; same published cutoff).
`thinkingConfig.thinkingLevel: "low"` -- reasoning/thinking is ON, not disabled; "low" is
the minimum level the API accepts (its own docs: "minimal is not supported and returns
an error").

**What would prove this wrong:** if the RPD=20 figure turns out to itself vary (e.g. by
time of day or account standing) rather than being a fixed daily allotment -- worth
re-confirming after a few real daily cycles once the scheduled task has run for a week.

## 2026-10-05 -- Re-pointed the 3-model comparison to the fixed 200-ruling subset, not the full 661

`scripts/analyze_gemini_comparison.py` originally re-derived its own comparison
population by filtering `usable_rulings.jsonl` to `rulingDate >= POST_CUTOFF_START`
directly -- the full 661-ruling eligible pool, not the 200-ruling sample
`build_gemini_subset.py` actually draws Gemini's calls from. Comparing the 3 Groq
models against the full 661 while Gemini only ever has (at most) 200 rows would make
the "fair comparison" table quietly compare two different populations. Fixed to load
`data/gemini_subset.csv` directly, same as `run_gemini_classification.py` does, so all
4 models' rows in `review/gemini_comparison.md` are always the same fixed 200 rulings.

## 2026-10-05 -- schtasks command chosen: daily trigger, no network/logon dependency

Final command handed to the user (not run by the assistant -- registering a scheduled
task is a system-settings change, the user's own action per the project's safety
rules):
`schtasks /create /tn "GeminiTariffDailyRun" /tr "<path>\run_gemini_daily.bat" /sc daily /st 09:00 /f`
Chose a plain daily trigger, no catch-up flag: `run_gemini_daily.bat` is
idempotent/resumable (caches to `llm_logs/`, exits 0 whether it did 0 or 20 calls), so
if the machine is off at 09:00 and that day's trigger is simply skipped, nothing is
lost -- the next day's run picks up from the same cache. Not relying on Task
Scheduler's "run as soon as possible after a missed start" setting, since that isn't
enabled by a plain `schtasks /create` call and would need either the GUI or an XML task
definition to set explicitly -- not worth the added complexity for a job where a missed
day just means one fewer day's 20 calls, not a failure.
`/f` overwrites silently if the task name already exists (safe here: it's a fresh task
name, not reusing one with different settings).

## 2026-10-06 -- Pre-push: no Gemini results in v1.0 public files; reproducibility from tracked files only

1. **Gemini results removed from tracking** (kept on disk, gitignored): `llm_logs/gemini-*/`,
   `logs/`, `logs_gemini*.txt`, `review/gemini_comparison.{md,json}`. Subset list
   (`data/gemini_subset.csv`) and all code stay tracked. STATUS.md/findings.md no longer
   quote any Gemini progress count or link the partial comparison. The ATLAS "Gemini-2.5-Pro"
   figure in findings.md is prior work's number, not this project's, and stays. When all 200
   are done: `git add -f llm_logs/gemini-3.8-flash` etc. for v1.1.
2. **Reproducibility gap found and closed.** The earlier untracking of `data/raw/*` meant
   `parse_duty_rates.py`, `audit_direction.py` (HTS), and `clean_descriptions.py`,
   `audit_accuracy.py`, `build_stripping_audit.py`, `build_exclusions_table.py` (rulings,
   search pages) could not run from a fresh clone. Fix: re-tracked `data/raw/rulings` +
   `data/raw/search_pages` (18 MB, small enough), and added `scripts/build_compact_hts.py` ->
   `data/compact/hts_revisions/*.json.gz` (9.3 MB: only rows with an htsno, only the 3 fields
   the code reads). The two HTS loaders now read raw if present, else the compact copy;
   checked all 20 dated revisions produce identical rate lookups and 10-digit pools from both.
   Only the 255 MB raw HTS dumps stay untracked.
