import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_manifest_is_hacs_compatible():
    manifest = json.loads((ROOT / "custom_components/prayzone/manifest.json").read_text())
    assert manifest["domain"] == "prayzone"
    assert manifest["config_flow"] is True
    assert manifest["version"] == "0.1.0"


def test_attribution_is_present_in_readme():
    readme = (ROOT / "README.md").read_text()
    assert "https://pray.zone/" in readme
