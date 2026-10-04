from pathlib import Path
import ast


CONTRACT = Path(__file__).parents[1] / "contracts" / "web_claim_verifier.py"


def test_contract_is_valid_python():
    source = CONTRACT.read_text(encoding="utf-8")
    ast.parse(source)


def test_contract_has_required_public_methods():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "def verify(" in source
    assert "def get_result(" in source
    assert "@gl.public.write" in source
    assert "@gl.public.view" in source


def test_nondeterministic_operations_are_present():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "gl.nondet.web.get" in source
    assert "gl.nondet.exec_prompt" in source
    assert "gl.vm.run_nondet_unsafe" in source


def test_storage_is_updated_after_consensus():
    source = CONTRACT.read_text(encoding="utf-8")
    consensus_pos = source.index("result = gl.vm.run_nondet_unsafe")
    storage_pos = source.index("self.verdict = result")
    assert consensus_pos < storage_pos
