"""Check constructor results with the real standard library and strict CLI."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from mypy.test.helpers import Suite


def _check_constructor_new_result(
    name: str,
    error_count: int,
    semantic_codes: tuple[str, ...],
    tmp_path: Path,
    program: Path | None = None,
    incremental: bool = False,
    require_cached_provider: bool = False,
) -> None:
    source = Path(__file__).resolve().parents[2]
    if program is None:
        program = source / "test-data" / "constructor-new-result" / (name + ".py")
    config = tmp_path / "mypy.ini"
    config.write_text("[mypy]\nstrict = True\npython_version = 3.15\nwarn_unreachable = True\n")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "mypy",
            "--config-file",
            str(config),
            *([] if incremental else ["--no-incremental"]),
            *(["--verbose"] if require_cached_provider else []),
            "--cache-dir",
            str(tmp_path / "cache"),
            str(program),
        ],
        cwd=source,
        text=True,
        capture_output=True,
        check=False,
    )
    if require_cached_provider:
        assert "Metadata fresh for overloaded_cls_provider:" in result.stderr, result.stderr
    else:
        assert result.stderr == ""
    assert result.returncode == (1 if error_count else 0), result.stdout
    errors = [line for line in result.stdout.splitlines() if ": error:" in line]
    assert len(errors) == error_count, result.stdout
    bad_lines = [
        number
        for number, line in enumerate(program.read_text().splitlines(), 1)
        if "# genuine-negative" in line
    ]
    assert len(bad_lines) == len(semantic_codes)
    actual: dict[int, set[str]] = {}
    for error in errors:
        match = re.search(r"\.py:(\d+): error: .*\[([^]]+)\]$", error)
        assert match is not None, error
        actual.setdefault(int(match.group(1)), set()).add(match.group(2))
    assert set(actual) == set(bad_lines), result.stdout
    for number, code in zip(bad_lines, semantic_codes):
        assert code in actual[number], result.stdout


class ConstructorNewResultSuite(Suite):
    def check_program(self, name: str, error_count: int, codes: tuple[str, ...]) -> None:
        with TemporaryDirectory(prefix="mypy-constructor-result-") as temporary:
            _check_constructor_new_result(name, error_count, codes, Path(temporary))

    def test_primary_positive(self) -> None:
        self.check_program("primary_positive", 0, ())

    def test_primary_negative(self) -> None:
        self.check_program(
            "primary_negative", 5, ("arg-type", "call-arg", "arg-type", "arg-type", "return-value")
        )

    def test_standard_positive(self) -> None:
        self.check_program("standard_positive", 0, ())

    def test_standard_negative(self) -> None:
        self.check_program(
            "standard_negative",
            9,
            (
                "arg-type",
                "misc",
                "type-var",
                "arg-type",
                "abstract",
                "return-value",
                "arg-type",
                "call-overload",
            ),
        )

    def test_selected_overload_cls(self) -> None:
        self.check_program("overloaded_cls", 2, ("misc", "misc"))

    def test_cached_selected_overload_cls(self) -> None:
        source = Path(__file__).resolve().parents[2]
        original = (source / "test-data/constructor-new-result/overloaded_cls.py").read_text()
        split = original.index("assert_type(Restricted")
        with TemporaryDirectory(prefix="mypy-constructor-cache-") as temporary:
            directory = Path(temporary)
            (directory / "overloaded_cls_provider.py").write_text(original[:split])
            consumer = directory / "consumer.py"
            consumer.write_text(
                "from typing import assert_type\nfrom overloaded_cls_provider import Restricted\n\n"
                + original[split:]
            )
            for warm in (False, True):
                _check_constructor_new_result(
                    "cached_overload",
                    2,
                    ("misc", "misc"),
                    directory,
                    consumer,
                    incremental=True,
                    require_cached_provider=warm,
                )
