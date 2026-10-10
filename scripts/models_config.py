"""
Single source for the model list. Every analysis script reads its models from
config.json through this module, so no model name is hardcoded elsewhere.

A model entry in config.json has: provider, model_id, training_cutoff(+source), and for
v1.1 models also: cohort ("v1.0" | "v1.1"), sample ("all" = the 1,098 usable rulings, or
"subset200" = data/gemini_subset.csv), extra_params (request fields for the chosen
reasoning level), prices per 1M tokens, and optionally `dir_name`.

Responses are cached in llm_logs/<dir_name>/<rulingNumber>.json. dir_name defaults to
model_id with ":" replaced by "_" (":" is not allowed in Windows folder names).
"""
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
LLM_LOGS_DIR = ROOT / "llm_logs"
SUBSET_PATH = ROOT / "data" / "gemini_subset.csv"
USABLE_PATH = ROOT / "data" / "processed" / "usable_rulings.jsonl"


def load():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["models"]


def dir_name(model):
    return model.get("dir_name") or model["model_id"].replace(":", "_")


def model_dir(model):
    return LLM_LOGS_DIR / dir_name(model)


def sample_ids(model):
    """Ruling numbers this model is supposed to cover, or None for all usable rulings."""
    if model.get("sample", "all") == "subset200":
        with SUBSET_PATH.open(encoding="utf-8") as f:
            return [row["rulingNumber"] for row in csv.DictReader(f)]
    return None


def expected_n(model):
    ids = sample_ids(model)
    if ids is not None:
        return len(ids)
    return sum(1 for _ in USABLE_PATH.open(encoding="utf-8"))


def cached_n(model):
    d = model_dir(model)
    return len(list(d.glob("*.json"))) if d.exists() else 0


def analysis_models(cohort=None, include_partial=None, include_replication=False):
    """Models to analyse. A model whose cache is smaller than its sample is skipped (and
    named on stderr) unless include_partial / TARIFF_INCLUDE_PARTIAL=1, so incomplete
    runs never reach a published table by accident."""
    import sys
    if include_partial is None:
        include_partial = os.environ.get("TARIFF_INCLUDE_PARTIAL") == "1"
    out = []
    for m in load():
        if m.get("role") == "replication" and not include_replication:
            continue
        if cohort and m.get("cohort", "v1.0") != cohort:
            continue
        have, need = cached_n(m), expected_n(m)
        if have < need and not include_partial:
            print(f"[models_config] skipping {m['model_id']}: {have}/{need} cached (incomplete)", file=sys.stderr)
            continue
        out.append(m)
    return out


def model_ids(cohort=None, include_partial=None):
    return [m["model_id"] for m in analysis_models(cohort, include_partial)]


def by_id(model_id):
    return next(m for m in load() if m["model_id"] == model_id)


def path_for(model_id):
    return model_dir(by_id(model_id))


def load_results(model_id):
    return [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(path_for(model_id).glob("*.json"))]


def results_by_model(include_partial=None):
    return {m["model_id"]: [json.loads(fp.read_text(encoding="utf-8")) for fp in sorted(model_dir(m).glob("*.json"))]
            for m in analysis_models(include_partial=include_partial)}


def replication_models():
    """Provider-replication runs (PREREG_v1.2.md part C): never in a main table."""
    return [m for m in load() if m.get("role") == "replication"]
