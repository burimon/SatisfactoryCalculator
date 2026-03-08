import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from SatisfactoryCalculator.webapp.workflow_store import (
    list_workflows_payload,
    load_workflow_payload,
    save_workflow_payload,
    workflows_directory,
)


class WorkflowStoreTests(unittest.TestCase):
    def test_workflows_directory_uses_platformdirs_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "SatisfactoryCalculator.webapp.workflow_store.platformdirs_user_data_dir",
                return_value=str(Path(temp_dir) / "Burimon" / "SatisfactoryCalculator"),
            ):
                path = workflows_directory()
                self.assertEqual(
                    path,
                    Path(temp_dir) / "Burimon" / "SatisfactoryCalculator" / "workflows",
                )
                self.assertTrue(path.is_dir())

    def test_save_and_load_workflow_payload_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "SatisfactoryCalculator.webapp.workflow_store.workflows_directory",
                return_value=Path(temp_dir),
            ):
                result = save_workflow_payload(
                    {
                        "version": 1,
                        "name": "Iron Starter",
                        "defaultBeltCapacity": 60,
                        "nodes": [],
                        "edges": [],
                    }
                )
                self.assertEqual(result["filename"], "iron-starter.json")
                loaded = load_workflow_payload("iron-starter.json")
                self.assertEqual(loaded["name"], "Iron Starter")
                self.assertEqual(loaded["defaultBeltCapacity"], 60)

    def test_list_workflows_payload_reports_directory_and_saved_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow_dir = Path(temp_dir)
            (workflow_dir / "starter.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "name": "Starter",
                        "defaultBeltCapacity": 60,
                        "nodes": [],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "SatisfactoryCalculator.webapp.workflow_store.workflows_directory",
                return_value=workflow_dir,
            ):
                payload = list_workflows_payload()
                self.assertEqual(payload["directory"], str(workflow_dir))
                self.assertEqual(
                    payload["files"],
                    [{"filename": "starter.json", "name": "Starter"}],
                )


if __name__ == "__main__":
    unittest.main()
