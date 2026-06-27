import os
import subprocess
import sys


def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(repo_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    report_path = os.path.join(reports_dir, "report.html")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    completed = subprocess.run(cmd, cwd=repo_root)
    if completed.returncode != 0:
        print(f"Pytest exited with code {completed.returncode}; report may still be generated.")

    if os.path.exists(report_path):
        print(f"HTML report generated: file:///{report_path.replace(os.sep, '/')} ")
    else:
        print("HTML report was not generated.")

    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()

