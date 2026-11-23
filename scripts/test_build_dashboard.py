import json
import tempfile
import unittest
from pathlib import Path

import build_dashboard


class DashboardBuildTest(unittest.TestCase):
    def test_build_includes_shared_renderer_and_repository_list(self):
        assets = build_dashboard.ROOT / "mahjong-domain-core" / "scripts" / "ci-site"
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            build_dashboard.build(site, assets)
            self.assertTrue((site / "dashboard" / "metrics.js").is_file())
            self.assertEqual(len(json.loads((site / "dashboard" / "repositories.json").read_text())), 3)
            self.assertTrue((site / "index.html").is_file())

    def test_reserved_dashboard_collision_is_rejected(self):
        assets = build_dashboard.ROOT / "mahjong-domain-core" / "scripts" / "ci-site"
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "dashboard").mkdir()
            with self.assertRaises(FileExistsError):
                build_dashboard.build(site, assets)


if __name__ == "__main__":
    unittest.main()
