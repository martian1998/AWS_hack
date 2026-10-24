from pathlib import Path
import yaml


def test_infrastructure_has_no_active_stub_consumers_and_safe_queue_bounds():
    template = yaml.safe_load((Path(__file__).resolve().parents[1] / "infra/template.yaml").read_text())
    resources = template["Resources"]
    timeout = template["Globals"]["Function"]["Timeout"]
    for lane in ("Triage", "Outreach", "Urgent"):
        queue = resources[lane + "Queue"]["Properties"]
        source = resources[lane + "Function"]["Properties"]["Events"]["Queue"]["Properties"]
        assert source["Enabled"] is False
        assert source["FunctionResponseTypes"] == ["ReportBatchItemFailures"]
        assert queue["VisibilityTimeout"] >= 6 * timeout + source["MaximumBatchingWindowInSeconds"]
        assert queue["RedrivePolicy"]["maxReceiveCount"] >= 5
        assert queue["SqsManagedSseEnabled"] is True
    for name in ("Records", "Escalations", "Audit", "Work", "Control"):
        assert resources[name + "Table"]["DeletionPolicy"] == "Retain"
    assert resources["WorkTable"]["Properties"]["GlobalSecondaryIndexes"][0]["IndexName"] == "GSI1"
