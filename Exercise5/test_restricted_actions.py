"""Check that the devops-demo profile blocks and allows the right actions.

Two checks run inside a container that is started with
`--security-opt apparmor=devops-demo`:

  1. reading /etc/shadow must be denied;
  2. writing /tmp/apparmor-demo/notes.txt must succeed.

Run this on a Linux host, or on WSL2 with a Linux Docker engine, after
`python apply_apparmor.py` and `docker build -t apparmor-demo:latest .`.
Windows Docker Desktop cannot apply AppArmor profiles.

Exit codes:
  0 - every check passed
  1 - at least one check failed
  2 - the environment cannot run the checks at all
"""

import shutil
import subprocess
import sys

IMAGE = "apparmor-demo:latest"
PROFILE = "devops-demo"

READ_SECRET = "open('/etc/shadow').read()"
WRITE_NOTES = (
    "import os;"
    "os.makedirs('/tmp/apparmor-demo', exist_ok=True);"
    "open('/tmp/apparmor-demo/notes.txt', 'w').write('ok\\n');"
    "print('written')"
)

CHECKS = [
    ("read /etc/shadow is denied", READ_SECRET, False, "PermissionError"),
    ("write /tmp/apparmor-demo/notes.txt succeeds", WRITE_NOTES, True, "written"),
]


def run_in_container(script):
    command = [
        "docker",
        "run",
        "--rm",
        "--security-opt",
        f"apparmor={PROFILE}",
        IMAGE,
        "python",
        "-c",
        script,
    ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def main():
    print(f"image: {IMAGE}")
    print(f"profile: {PROFILE}")

    if shutil.which("docker") is None:
        print("error: the docker CLI was not found on PATH")
        print("run this on a Linux host, or on WSL2 with a Linux Docker engine")
        return 2

    failures = 0
    for description, script, expect_success, marker in CHECKS:
        result = run_in_container(script)
        combined = f"{result.stdout}\n{result.stderr}"
        succeeded = result.returncode == 0
        marker_seen = marker in combined
        passed = (succeeded == expect_success) and marker_seen

        print(f"--- {description}")
        print(f"    exit code: {result.returncode}")
        print(f"    output: {combined.strip() or '(empty)'}")
        if passed:
            print("    PASS")
        else:
            print("    FAIL")
            if succeeded != expect_success:
                expected = "success" if expect_success else "failure"
                print(f"    expected {expected} but the command did the opposite")
            if not marker_seen:
                print(f"    expected the text {marker!r} in the output")
            failures += 1

    print("result:", "FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
