"""Master prompt compiler support for OX-GAD."""

from oxgad.master_prompt.binding import build_master_prompt_from_art_spec
from oxgad.master_prompt.builder import build_master_prompt_payload
from oxgad.master_prompt.canonical import (
    canonical_master_prompt_json,
    master_prompt_hash,
)
from oxgad.master_prompt.catalog import (
    load_master_prompt_catalog,
    master_prompt_catalog_summary,
)
from oxgad.master_prompt.evidence import (
    PROMPT_EVIDENCE_CHAIN_VERSION,
    build_prompt_evidence_chain,
    verify_prompt_evidence_chain,
)
from oxgad.master_prompt.gates import evaluate_master_prompt_gates
from oxgad.master_prompt.provenance import (
    PROMPT_PROVENANCE_HOOK_VERSION,
    build_prompt_provenance_hook,
    stable_prompt_hash,
)
from oxgad.master_prompt.quality import evaluate_master_prompt_quality
from oxgad.master_prompt.render_binding import (
    build_render_bound_master_prompt,
    render_plan_hash,
)

__all__ = [
    "PROMPT_EVIDENCE_CHAIN_VERSION",
    "PROMPT_PROVENANCE_HOOK_VERSION",
    "build_master_prompt_from_art_spec",
    "build_master_prompt_payload",
    "build_prompt_evidence_chain",
    "build_prompt_provenance_hook",
    "build_render_bound_master_prompt",
    "canonical_master_prompt_json",
    "evaluate_master_prompt_gates",
    "evaluate_master_prompt_quality",
    "load_master_prompt_catalog",
    "master_prompt_catalog_summary",
    "master_prompt_hash",
    "render_plan_hash",
    "stable_prompt_hash",
    "verify_prompt_evidence_chain",
]
