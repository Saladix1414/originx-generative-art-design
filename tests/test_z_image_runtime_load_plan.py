from oxgad.forge.z_image_runtime_load_plan import (
    build_z_image_runtime_load_plan,
)


def test_runtime_load_plan_is_single_candidate_dry_run():
    value = build_z_image_runtime_load_plan()

    assert value["state"] == "DRY_RUN_NOT_AUTHORIZED"
    assert value["limits"]["width"] == 256
    assert value["limits"]["height"] == 256
    assert value["limits"]["steps"] == 1
    assert value["limits"]["candidateCount"] == 1
    assert value["limits"]["diskBackedParameters"] is True
    assert value["limits"]["vaeTiling"] is True


def test_runtime_load_plan_contains_verified_artifacts():
    command = build_z_image_runtime_load_plan()["command"]

    assert "models/z-image/z_image_turbo-Q4_0.gguf" in command
    assert "models/z-image/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" in command
    assert "models/z-image/z_image_vae.safetensors" in command


def test_runtime_load_plan_grants_no_authority():
    governance = build_z_image_runtime_load_plan()["governance"]

    assert governance["runtimeInvocationAllowed"] is False
    assert governance["imageGenerationAllowed"] is False
    assert governance["canonicalizationAllowed"] is False
    assert governance["batchGenerationAllowed"] is False
