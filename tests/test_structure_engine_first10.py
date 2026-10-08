"""OX-GAD PHASE 2E — first 10 Art Spec tests."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from oxgad.structure.canonical import (
    canonical_json,
    canonical_sha256,
)
from oxgad.structure.first10 import (
    FIRST10_COUNT,
    FIRST10_MANIFEST_VERSION,
    build_manifest,
    first_10_packages,
    generate_first_10,
    write_first_10,
)
from oxgad.structure.validator import (
    is_valid_art_spec,
)


class First10InputTests(
    unittest.TestCase
):
    def test_exactly_ten_inputs_exist(self):
        packages = first_10_packages()

        self.assertEqual(
            len(packages),
            FIRST10_COUNT,
        )

        self.assertEqual(
            FIRST10_COUNT,
            10,
        )

    def test_ids_and_serials_are_sequential(self):
        packages = first_10_packages()

        self.assertEqual(
            [
                item["tokenId"]
                for item in packages
            ],
            list(range(1, 11)),
        )

        self.assertEqual(
            [
                item["serial"]
                for item in packages
            ],
            [
                f"#{value:04d}"
                for value in range(1, 11)
            ],
        )

    def test_all_first_ten_are_rare_primitive(self):
        for package in first_10_packages():
            self.assertEqual(
                package["tier"],
                "RARE",
            )

            self.assertEqual(
                package[
                    "generationTheme"
                ],
                "Primitive Origin",
            )

    def test_dna_hash_matches_actual_dna(self):
        for package in first_10_packages():
            self.assertEqual(
                package["dnaHash"],
                canonical_sha256(
                    package["dna"]
                ),
            )


class First10GenerationTests(
    unittest.TestCase
):
    def test_all_generated_specs_are_valid(self):
        results = generate_first_10()

        self.assertEqual(
            len(results),
            10,
        )

        for result in results:
            self.assertTrue(
                is_valid_art_spec(
                    result.art_spec
                )
            )

    def test_all_art_specs_are_unique(self):
        results = generate_first_10()

        serialized = {
            canonical_json(
                result.art_spec
            )
            for result in results
        }

        self.assertEqual(
            len(serialized),
            10,
        )

    def test_all_art_spec_hashes_are_unique(self):
        results = generate_first_10()

        hashes = {
            result.art_spec_hash
            for result in results
        }

        self.assertEqual(
            len(hashes),
            10,
        )

    def test_determinism_across_repeated_generation(self):
        first = generate_first_10()
        second = generate_first_10()

        self.assertEqual(
            [
                item.art_spec_hash
                for item in first
            ],
            [
                item.art_spec_hash
                for item in second
            ],
        )

        self.assertEqual(
            [
                canonical_json(
                    item.art_spec
                )
                for item in first
            ],
            [
                canonical_json(
                    item.art_spec
                )
                for item in second
            ],
        )

    def test_identity_traits_are_preserved(self):
        packages = first_10_packages()
        results = generate_first_10()

        for package, result in zip(
            packages,
            results,
            strict=True,
        ):
            identity = result.art_spec[
                "identity"
            ]

            self.assertEqual(
                identity["tokenId"],
                package["tokenId"],
            )

            self.assertEqual(
                identity["serial"],
                package["serial"],
            )

            self.assertEqual(
                identity[
                    "canonicalName"
                ],
                package[
                    "canonicalName"
                ],
            )

            self.assertEqual(
                identity["dna"],
                package["dna"],
            )

            self.assertEqual(
                identity["dnaHash"],
                package["dnaHash"],
            )

            self.assertEqual(
                result.art_spec[
                    "camera"
                ][
                    "focalTarget"
                ],
                package[
                    "canonicalName"
                ],
            )

    def test_cross_token_objects_are_isolated(self):
        results = list(
            generate_first_10()
        )

        second_before = copy.deepcopy(
            results[1].art_spec
        )

        results[0].art_spec[
            "identity"
        ][
            "canonicalName"
        ] = "MUTATED-ONLY-TOKEN-1"

        self.assertEqual(
            results[1].art_spec,
            second_before,
        )


class First10ManifestTests(
    unittest.TestCase
):
    def test_manifest_contract(self):
        manifest = build_manifest(
            generate_first_10()
        )

        self.assertEqual(
            manifest[
                "manifestVersion"
            ],
            FIRST10_MANIFEST_VERSION,
        )

        self.assertEqual(
            manifest["count"],
            10,
        )

        self.assertEqual(
            manifest["tier"],
            "RARE",
        )

        self.assertEqual(
            manifest["era"],
            "Primitive Origin",
        )

        self.assertEqual(
            len(
                manifest["entries"]
            ),
            10,
        )

    def test_manifest_hashes_are_unique(self):
        manifest = build_manifest(
            generate_first_10()
        )

        art_hashes = {
            item["artSpecHash"]
            for item in manifest[
                "entries"
            ]
        }

        dna_hashes = {
            item["dnaHash"]
            for item in manifest[
                "entries"
            ]
        }

        self.assertEqual(
            len(art_hashes),
            10,
        )

        self.assertEqual(
            len(dna_hashes),
            10,
        )


class First10FilesystemTests(
    unittest.TestCase
):
    def test_written_files_match_canonical_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)

            manifest = write_first_10(
                output
            )

            for entry in manifest[
                "entries"
            ]:
                path = (
                    output
                    / entry["file"]
                )

                self.assertTrue(
                    path.is_file()
                )

                raw = path.read_bytes()

                digest = (
                    "sha256:"
                    + hashlib.sha256(
                        raw
                    ).hexdigest()
                )

                self.assertEqual(
                    digest,
                    entry[
                        "artSpecHash"
                    ],
                )

                parsed = json.loads(
                    raw.decode(
                        "utf-8"
                    )
                )

                self.assertEqual(
                    raw.decode(
                        "utf-8"
                    ),
                    canonical_json(
                        parsed
                    ),
                )

    def test_two_output_runs_are_byte_identical(self):
        with (
            tempfile.TemporaryDirectory()
            as first_tmp,
            tempfile.TemporaryDirectory()
            as second_tmp,
        ):
            first_dir = Path(
                first_tmp
            )
            second_dir = Path(
                second_tmp
            )

            write_first_10(
                first_dir
            )

            write_first_10(
                second_dir
            )

            first_files = sorted(
                path.name
                for path
                in first_dir.iterdir()
            )

            second_files = sorted(
                path.name
                for path
                in second_dir.iterdir()
            )

            self.assertEqual(
                first_files,
                second_files,
            )

            for name in first_files:
                self.assertEqual(
                    (
                        first_dir
                        / name
                    ).read_bytes(),
                    (
                        second_dir
                        / name
                    ).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
