from pathlib import Path


PLAN = Path("docs/architecture/phase48-art-spec-expansion-plan.md")


def test_art_spec_expansion_plan_recenters_generativity():
    text = PLAN.read_text().lower()

    assert "recenters the roadmap on generative art design" in text
    assert "visual grammar" in text
    assert "trait families" in text


def test_art_spec_expansion_plan_defines_trait_families():
    text = PLAN.read_text().lower()

    for item in [
        "palette",
        "geometry",
        "material",
        "lighting",
        "depth",
        "motion",
        "symbolic motif",
        "environment",
        "distortion",
        "finish",
    ]:
        assert item in text


def test_art_spec_expansion_plan_defines_rarity_and_composition():
    text = PLAN.read_text().lower()

    for item in [
        "common",
        "uncommon",
        "rare",
        "epic",
        "legendary",
        "centered icon",
        "radial field",
        "layered landscape",
        "architectural stack",
        "orbital system",
        "fragmented relic",
        "signal map",
        "synthetic organism",
    ]:
        assert item in text


def test_art_spec_expansion_plan_preserves_boundaries():
    text = PLAN.read_text().lower()

    assert "planning only" in text
    assert "does not generate images" in text
    assert "execute models" in text
    assert "call network services" in text
    assert "move generated artifacts" in text
