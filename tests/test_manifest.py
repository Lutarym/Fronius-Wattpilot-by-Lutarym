import json
from pathlib import Path

def test_manifest():
    data = json.loads(
        (Path(__file__).parents[1] / "custom_components/fronius_wattpilot_lutarym/manifest.json").read_text()
    )
    assert data["domain"] == "fronius_wattpilot_lutarym"
    assert data["version"] == "1.0.0"
    assert data["config_flow"] is True
