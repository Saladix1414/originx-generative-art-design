from oxgad.genesis.planning import (
    MODEL_HASH,
    build_genesis_art_spec,
    build_genesis_batch_plans,
    build_genesis_render_binding,
    validate_genesis_render_binding,
)
from oxgad.render.validator import validate_render_plan
from oxgad.structure.validator import validate_art_spec


def test_genesis_art_specs_are_valid_and_legendary():
    values = build_genesis_batch_plans()

    assert len(values) == 10

    for value in values:
        validate_art_spec(value["artSpec"])
        assert value["artSpec"]["identity"]["tier"] == "LEGENDARY"
        assert value["artSpec"]["renderIntent"][
            "targetResolution"
        ] == {"width": 512, "height": 512}


def test_genesis_art_specs_and_render_plans_are_unique():
    values = build_genesis_batch_plans()

    assert len({item["artSpecHash"] for item in values}) == 10
    assert len({item["renderPlanHash"] for item in values}) == 10


def test_render_plans_remain_canonical_and_unexecuted():
    values = build_genesis_batch_plans()

    for value in values:
        validate_render_plan(value["renderPlan"])
        assert value["renderPlan"]["executionPolicy"][
            "executionAllowed"
        ] is False


def test_runtime_binding_is_exact_and_unexecuted():
    value = build_genesis_render_binding(1)

    validate_genesis_render_binding(value)
    assert value["model"]["modelId"] == "OX-MODEL-002"
    assert value["model"]["modelHash"] == MODEL_HASH
    assert value["resolution"] == {
        "width": 512,
        "height": 512,
    }
    assert value["sampling"]["steps"] == 12
    assert value["authority"]["executionAllowed"] is False
    assert value["authority"]["candidateIsCanonical"] is False


def test_planning_is_deterministic():
    assert build_genesis_art_spec(1) == (
        build_genesis_art_spec(1)
    )
    assert build_genesis_batch_plans() == (
        build_genesis_batch_plans()
    )
