"""Load my-apparmor-profile into the running Linux kernel.

AppArmor is a Linux kernel feature. This script only works on a Linux host, or
on WSL2 running a Linux Docker engine. Windows Docker Desktop cannot load
AppArmor profiles into its VM.

Exit codes:
  0 - apparmor_parser accepted the profile
  1 - apparmor_parser rejected the profile
  2 - the environment cannot load profiles at all
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROFILE_FILE = "my-apparmor-profile"
PROFILE_NAME = "devops-demo"
COMMAND = ["sudo", "apparmor_parser", "-r", "-W", PROFILE_FILE]


def missing_tool():
    for tool in ("sudo", "apparmor_parser"):
        if shutil.which(tool) is None:
            return tool
    return None


def main():
    here = Path(__file__).resolve().parent
    print(f"profile file: {here / PROFILE_FILE}")
    print("command:", " ".join(COMMAND))

    if not (here / PROFILE_FILE).is_file():
        print(f"error: {PROFILE_FILE} is missing next to this script")
        return 2

    missing = missing_tool()
    if missing is not None:
        print(f"error: '{missing}' was not found on PATH")
        print("AppArmor is a Linux kernel feature. Run this on a Linux host, or")
        print("on WSL2 with a Linux Docker engine. Windows Docker Desktop cannot")
        print("apply AppArmor profiles to containers.")
        return 2

    # Standard input and output are inherited so that sudo can ask for a
    # password. Cache the credentials first if you run this non-interactively.
    completed = subprocess.run(COMMAND, cwd=here, check=False)
    print(f"apparmor_parser return code: {completed.returncode}")

    if completed.returncode != 0:
        print("the profile was not loaded; check the messages above")
        return 1

    print(f"profile '{PROFILE_NAME}' is loaded. Check it with: sudo aa-status")
    return 0


if __name__ == "__main__":
    sys.exit(main())
