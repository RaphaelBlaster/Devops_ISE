"""Demonstrate what the devops-demo AppArmor profile allows and blocks.

The script is written so that it runs in both worlds:

- inside a container started with `--security-opt apparmor=devops-demo`, where
  the profile is enforced;
- inside a container without the profile, where both steps succeed.

It always exits 0. Deciding whether the outcome is correct is the job of
`test_restricted_actions.py`.
"""

import os
import sys

DEMO_DIR = "/tmp/apparmor-demo"
NOTES_PATH = os.path.join(DEMO_DIR, "notes.txt")
SECRET_PATH = "/etc/shadow"


def write_notes():
    """Write under /tmp/apparmor-demo. The profile allows this path only."""
    print(f"step 1: create {DEMO_DIR} and write {NOTES_PATH}")
    try:
        os.makedirs(DEMO_DIR, exist_ok=True)
        with open(NOTES_PATH, "w", encoding="utf-8") as handle:
            handle.write("written by the apparmor demo\n")
    except OSError as exc:
        print(f"step 1 outcome: BLOCKED by {exc.__class__.__name__}: {exc}")
        return False
    print(f"step 1 outcome: OK, {NOTES_PATH} written")
    return True


def read_secret():
    """Try to read /etc/shadow. The profile denies this path explicitly."""
    print(f"step 2: read {SECRET_PATH}")
    try:
        with open(SECRET_PATH, "r", encoding="utf-8") as handle:
            handle.read(1)
    except PermissionError as exc:
        print(f"step 2 outcome: DENIED by {exc.__class__.__name__}: {exc}")
        return False
    except OSError as exc:
        print(f"step 2 outcome: FAILED with {exc.__class__.__name__}: {exc}")
        return False
    print(f"step 2 outcome: ALLOWED, {SECRET_PATH} was readable")
    return True


def main():
    print("apparmor demo starting")
    print(f"uid: {os.getuid() if hasattr(os, 'getuid') else 'n/a'}")
    write_notes()
    read_secret()
    print("apparmor demo finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
