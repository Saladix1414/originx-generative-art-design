from oxgad.forge import (
    build_candidate_dry_run,
    candidate_dry_run_hash,
)


def _forge_contract():
    return {
        "forgeVersion": "OX-LOCAL-FORGE-1",
        "source": {
            "renderPlanVersion": "OX-RENDER-1",
            "renderPlanHash": "sha256:" + "a" * 64,
        },
        "hardware": {
            "profileVersion": "OX-HARDWARE-PROFILE-1",
            "requestedTarget": "LOCAL_CPP",
            "capability": "UNKNOWN",
        },
        "model": {
            "bindingState": "UNBOUND",
        },
        "execution": {
            "policy": "LOCAL_FIRST",
            "mode": "PREPARE_ONLY",
            "authorizationState": "BLOCKED",
            "executionAllowed": False,
        },
        "output": {
            "mediaGenerationAllowed": False,
            "canonicalArtworkAllowed": False,
        },
    }


def _dry_run():
    return build_candidate_dry_run(
        candidate_id="candidate-token-0001-local-001",
        media_path="output/candidates/token-0001/candidate-001.png",
        render_plan_hash="sha256:" + "a" * 64,
        forge_contract=_forge_contract(),
        model_binding_hash=None,
    )


def test_candidate_dry_run_builds_complete_prepare_only_chain():
    dry_run = _dry_run()

    assert dry_run["dryRunVersion"] == "OX-CANDIDATE-DRY-RUN-1"
    assert dry_run["candidateId"] == "candidate-token-0001-local-001"
    assert dry_run["state"] == "PREPARE_ONLY"

    assert dry_run["executionDecision"]["decision"] == "DENY"
    assert dry_run["candidateOutput"]["state"] == "CANDIDATE_UNAPPROVED"
    assert dry_run["candidateManifest"]["state"] == "CANDIDATE_MANIFEST_PREPARED"
    assert dry_run["candidateProvenanceHook"]["state"] == "PROVENANCE_PREPARED"


def test_candidate_dry_run_preserves_no_execution_authority():
    dry_run = _dry_run()

    assert dry_run["authority"] == {
        "backendInvocationAllowed": False,
        "mediaGenerated": False,
        "candidateIsCanonical": False,
        "manualApprovalRequired": True,
        "aiOutputIsCanonical": False,
    }

    assert dry_run["candidateOutput"]["media"]["mediaHash"] is None
    assert dry_run["candidateProvenanceHook"]["media"]["mediaGenerated"] is False


def test_candidate_dry_run_hashes_all_links():
    dry_run = _dry_run()

    hashes = dry_run["hashes"]

    assert set(hashes) == {
        "executionDecisionHash",
        "candidateOutputHash",
        "candidateManifestHash",
        "candidateProvenanceHookHash",
    }

    for digest in hashes.values():
        assert digest.startswith("sha256:")
        assert len(digest) == 71


def test_candidate_dry_run_hash_is_stable():
    first = _dry_run()
    second = _dry_run()

    assert candidate_dry_run_hash(first) == candidate_dry_run_hash(second)
