import copy

from oxgad.genesis import (
    build_genesis_batch_lore,
    build_genesis_lore,
    verify_akashic_chain,
)


def test_resonance_signatures_are_unique():
    values = build_genesis_batch_lore()

    signatures = {
        item["resonance"]["resonanceSignature"]
        for item in values
    }

    assert len(values) == 10
    assert len(signatures) == 10


def test_resonance_is_artistic_not_scientific_claim():
    resonance = build_genesis_lore(1)["resonance"]

    assert "artistic" in resonance["interpretation"]
    assert "not a claim" in resonance["interpretation"]


def test_glyphs_are_unique_and_not_watermarks():
    values = build_genesis_batch_lore()

    assert len({
        item["glyph"]["svgHash"]
        for item in values
    }) == 10

    assert all(
        item["glyph"]["watermarkRequired"] is False
        for item in values
    )


def test_initial_akashic_events_are_ordered():
    akashic = build_genesis_lore(1)["akashic"]

    assert [
        event["eventType"]
        for event in akashic["events"]
    ] == [
        "DNA_FORGED",
        "NAME_ASSIGNED",
        "RESONANCE_CREATED",
        "RESONANCE_GLYPH_MANIFESTED",
    ]
    assert verify_akashic_chain(akashic)


def test_akashic_tampering_is_detected():
    akashic = copy.deepcopy(
        build_genesis_lore(1)["akashic"]
    )
    akashic["events"][1]["payload"]["title"] = "TAMPERED"

    assert verify_akashic_chain(akashic) is False


def test_lore_is_deterministic():
    assert build_genesis_batch_lore() == (
        build_genesis_batch_lore()
    )
