import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class SmokeTest:

    def __init__(self):
        self.results = []

    def check(self, name, passed, detail):
        self.results.append((name, passed, detail))

    def path(self, relative):
        return ROOT / relative

    def folder_exists(self, relative):
        path = self.path(relative)
        self.check(
            f"folder: {relative}",
            path.is_dir(),
            "exists" if path.is_dir() else "missing"
        )

    def files_exist(self, name, relative, pattern):
        path = self.path(relative)
        files = list(path.glob(pattern)) if path.is_dir() else []
        self.check(
            name,
            bool(files),
            f"{len(files)} file(s): {', '.join(p.name for p in files[:5])}"
            if files
            else f"no files matching {relative}/{pattern}"
        )
        return files

    def non_empty_json_list(self, name, relative):
        path = self.path(relative)
        if not path.exists():
            self.check(name, False, f"missing {relative}")
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.check(name, False, f"invalid JSON: {exc}")
            return []

        passed = isinstance(data, list) and len(data) > 0
        self.check(
            name,
            passed,
            f"{len(data)} event(s)" if isinstance(data, list) else "not a list"
        )
        return data if isinstance(data, list) else []

    def valid_analytics(self, relative):
        path = self.path(relative)
        if not path.exists():
            self.check(f"analytics schema: {relative}", False, "missing")
            return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.check(f"analytics schema: {relative}", False, f"invalid JSON: {exc}")
            return

        zone_records = [
            values for key, values in data.items()
            if (
                not key.startswith("_")
                and isinstance(values, dict)
                and "visitors" in values
                and "total_dwell_time" in values
            )
        ]
        self.check(
            f"analytics schema: {relative}",
            bool(zone_records),
            f"{len(zone_records)} zone record(s)"
        )

    def api_files_present(self):
        required = [
            "app/main.py",
            "app/health.py",
            "app/metrics.py",
            "app/funnel.py",
            "app/heatmap.py",
            "app/recommendation.py",
            "app/kpis.py",
            "app/insights.py"
        ]
        missing = [
            relative for relative in required
            if not self.path(relative).exists()
        ]
        self.check(
            "API files present",
            not missing,
            "all required API files present"
            if not missing
            else f"missing: {', '.join(missing)}"
        )

    def dashboard_present(self):
        dashboard = self.path("dashboard/streamlit_app.py")
        self.check(
            "dashboard file present",
            dashboard.exists(),
            "dashboard/streamlit_app.py exists"
            if dashboard.exists()
            else "dashboard/streamlit_app.py missing"
        )

    def run(self):
        for folder in [
            "app",
            "dashboard",
            "data/pipeline",
            "data/outputs",
            "data/outputs/detection",
            "data/outputs/tracking",
            "data/outputs/events",
            "data/outputs/analytics",
            "data/outputs/heatmaps"
        ]:
            self.folder_exists(folder)

        self.files_exist(
            "detection outputs generated",
            "data/outputs/detection",
            "*_detected.mp4"
        )
        self.files_exist(
            "tracked videos generated",
            "data/outputs/tracking",
            "*_tracked.mp4"
        )
        self.files_exist(
            "tracking JSON generated",
            "data/outputs/tracking",
            "*_tracks.json"
        )
        analytics_files = self.files_exist(
            "analytics files present",
            "data/outputs/analytics",
            "*_summary.json"
        )
        self.files_exist(
            "heatmaps generated",
            "data/outputs/heatmaps",
            "*_heatmap.jpg"
        )
        self.files_exist(
            "event files present",
            "data/outputs/events",
            "events.*"
        )

        self.non_empty_json_list(
            "events contain records",
            "data/outputs/events/events.json"
        )

        for analytics_file in analytics_files:
            self.valid_analytics(
                str(analytics_file.relative_to(ROOT))
            )

        self.api_files_present()
        self.dashboard_present()

        return self.results

    def print_summary(self):
        passed_count = sum(1 for _, passed, _ in self.results if passed)
        failed_count = len(self.results) - passed_count

        print("\nSTORE INTELLIGENCE SMOKE TEST")
        print("=" * 36)
        for name, passed, detail in self.results:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name} - {detail}")

        print("=" * 36)
        print(f"PASS: {passed_count}")
        print(f"FAIL: {failed_count}")
        print("RESULT:", "PASS" if failed_count == 0 else "FAIL")

        return failed_count == 0


def main():
    smoke_test = SmokeTest()
    smoke_test.run()
    passed = smoke_test.print_summary()
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
