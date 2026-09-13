import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tools import TOOLS_SCHEMA, dispatch_tool_call


class ToolBackendTests(unittest.TestCase):
    def test_tool_registry_contains_four_scholarship_tools(self):
        self.assertEqual(
            {tool["name"] for tool in TOOLS_SCHEMA},
            {
                "profile_query",
                "scholarship_search",
                "scholarship_details",
                "study_plan_save",
            },
        )

    def test_profile_query_success_and_not_found(self):
        success = json.loads(
            dispatch_tool_call("profile_query", {"student_id": "SV2026001"})
        )
        missing = json.loads(
            dispatch_tool_call("profile_query", {"student_id": "SV9999999"})
        )

        self.assertEqual(success["status"], "SUCCESS")
        self.assertIn("gpa_scale", success["data"])
        self.assertEqual(missing["status"], "NOT_FOUND")

    def test_search_details_and_plan_save(self):
        search = json.loads(
            dispatch_tool_call(
                "scholarship_search",
                {
                    "degree_level": "Thạc sĩ",
                    "major": "Công nghệ thông tin",
                    "regions": ["Việt Nam", "Quốc tế"],
                    "intake": "2027",
                    "funding_need": "Hỗ trợ học phí",
                },
            )
        )
        details = json.loads(
            dispatch_tool_call(
                "scholarship_details",
                {"scholarship_id": "HB_TEST_01", "intake": "2027"},
            )
        )
        saved = json.loads(
            dispatch_tool_call(
                "study_plan_save",
                {
                    "student_id": "SV2026001",
                    "scholarship_id": "HB_TEST_01",
                    "tasks": [
                        {
                            "title": "Thi IELTS",
                            "due_date": "2026-11-30",
                            "priority": "high",
                        }
                    ],
                },
            )
        )

        self.assertEqual(search["status"], "SUCCESS")
        self.assertGreaterEqual(len(search["data"]), 1)
        self.assertEqual(details["status"], "SUCCESS")
        self.assertEqual(saved["status"], "SUCCESS")

    def test_plan_save_rejects_invalid_tasks(self):
        empty_tasks = json.loads(
            dispatch_tool_call(
                "study_plan_save",
                {
                    "student_id": "SV2026001",
                    "scholarship_id": "HB_TEST_01",
                    "tasks": [],
                },
            )
        )
        invalid_priority = json.loads(
            dispatch_tool_call(
                "study_plan_save",
                {
                    "student_id": "SV2026001",
                    "scholarship_id": "HB_TEST_01",
                    "tasks": [
                        {
                            "title": "Chuẩn bị CV",
                            "due_date": "2026-12-01",
                            "priority": "urgent",
                        }
                    ],
                },
            )
        )

        self.assertEqual(empty_tasks["status"], "INVALID_ARGUMENTS")
        self.assertEqual(invalid_priority["status"], "INVALID_ARGUMENTS")


if __name__ == "__main__":
    unittest.main()
