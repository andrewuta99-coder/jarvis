"""Unit tests for bin/jarvis-orchestrate's pure helpers.

The end-to-end test runs the real orchestrator against a temp dir + the
fixture constellation.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

JARVIS_ROOT = Path(__file__).resolve().parents[1]
ORCH = JARVIS_ROOT / "bin" / "jarvis-orchestrate"

_loader = SourceFileLoader("jarvis_orchestrate", str(ORCH))
_spec = importlib.util.spec_from_loader("jarvis_orchestrate", _loader)
orchestrate = importlib.util.module_from_spec(_spec)
sys.modules["jarvis_orchestrate"] = orchestrate
_loader.exec_module(orchestrate)


class TestValidateRequirements(unittest.TestCase):
    def test_no_requirements_passes(self):
        constellation = {
            "phases": [
                {"agents": [{"agent": "networking"}, {"agent": "infra"}]},
            ]
        }
        errors = orchestrate.validate_requirements(constellation, JARVIS_ROOT)
        self.assertEqual(errors, [])

    def test_rag_langchain_requires_ai(self):
        # rag-langchain has `requires_feature: ai` in its manifest.
        constellation_without = {
            "phases": [{"agents": [{"agent": "rag-langchain"}]}]
        }
        errors = orchestrate.validate_requirements(constellation_without, JARVIS_ROOT)
        self.assertTrue(any("requires 'ai'" in e for e in errors),
                        f"expected requires_ai error, got {errors}")

    def test_rag_langchain_with_ai_passes(self):
        constellation_with = {
            "phases": [{"agents": [{"agent": "ai"}, {"agent": "rag-langchain"}]}]
        }
        errors = orchestrate.validate_requirements(constellation_with, JARVIS_ROOT)
        self.assertEqual(errors, [])


class TestMergeOutputs(unittest.TestCase):
    def test_merge_uppercases_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            outputs_dir = Path(tmp) / ".jarvis" / "agent-outputs"
            outputs_dir.mkdir(parents=True)
            (outputs_dir / "networking.json").write_text(json.dumps({
                "vpc_id": "vpc-test",
                "private_subnet_ids": ["s1", "s2"],
            }))
            ctx = {"APP_NAME": "test"}
            merged = orchestrate.merge_outputs(Path(tmp), ctx)
            self.assertEqual(merged["VPC_ID"], "vpc-test")
            self.assertEqual(merged["PRIVATE_SUBNET_IDS"], ["s1", "s2"])
            self.assertEqual(merged["APP_NAME"], "test")  # preserved


if __name__ == "__main__":
    unittest.main()
