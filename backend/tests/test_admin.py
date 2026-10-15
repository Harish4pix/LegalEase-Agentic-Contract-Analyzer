import tempfile
import unittest
from pathlib import Path

from backend.app.services.admin import AdminService


class AdminServiceTests(unittest.TestCase):
    def test_login_issues_and_verifies_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = AdminService(root / "admin.json", root / "analyses", "admin@example.com", "StrongPass1", "test-secret")
            token = service.login("admin@example.com", "StrongPass1")
            self.assertTrue(token)
            self.assertTrue(service.verify(token))
            self.assertIsNone(service.login("admin@example.com", "wrong-password"))

    def test_empty_dashboard_has_stable_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = AdminService(root / "admin.json", root / "analyses", "admin@example.com", "StrongPass1", "test-secret")
            dashboard = service.dashboard()
            self.assertEqual(dashboard["total"], 0)
            self.assertEqual(dashboard["average_risk"], 0)
            self.assertEqual(dashboard["risks"], {"high": 0, "medium": 0, "low": 0})


if __name__ == "__main__":
    unittest.main()
