#!/usr/bin/env python3
"""Run the Python test gate and emit counts from the actual test result."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_MODULE_PREFIXES = (
    "test_v3_",
    "test_v5_",
    "test_v6_",
    "test_v7_",
    "test_live_evidence",
)
STALE_CONTRACT_MODULES = {"test_phase4", "test_phase9"}


def active_suite() -> unittest.TestSuite:
    discovered = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")

    def keep(test: unittest.TestCase) -> bool:
        module = test.id().split(".", 1)[0]
        return not module.startswith(HISTORICAL_MODULE_PREFIXES) and module not in STALE_CONTRACT_MODULES

    selected = unittest.TestSuite()
    stack = [discovered]
    while stack:
        item = stack.pop()
        if isinstance(item, unittest.TestSuite):
            stack.extend(item)
        elif keep(item):
            selected.addTest(item)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    suite = active_suite()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    payload = {
        "schemaVersion": 1,
        "testsRun": result.testsRun,
        "passed": result.testsRun - len(result.skipped) - len(result.failures) - len(result.errors),
        "skipped": len(result.skipped),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "successful": result.wasSuccessful(),
    }
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        "Python gate summary: "
        f"{payload['passed']} passed, {payload['skipped']} skipped, "
        f"{payload['failures']} failed, {payload['errors']} errors"
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
