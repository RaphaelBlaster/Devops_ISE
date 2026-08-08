# Exercise 5 - Confine a container process with an AppArmor profile

## Overview

AppArmor restricts what a program may do, using a profile that is loaded into
the kernel and attached to a process. Docker passes the profile name to the
container with `--security-opt apparmor=<name>`, and from then on the kernel
enforces it.

This exercise writes one profile, named `devops-demo`, and shows it working on a
container that is otherwise unremarkable:

- the profile denies reading `/etc/shadow`;
- the profile allows writes under `/tmp/apparmor-demo/` and nowhere else;
- the profile denies raw and packet network sockets.

`app.py` inside the container tries both file operations and prints what
happened. `test_restricted_actions.py` turns those two observations into checks
and exits non-zero if the profile is not being enforced.

The profile is enforced by the host kernel, not by the image, so it cannot be
baked into the Dockerfile. It has to be loaded on the machine that runs the
containers.

## Prerequisites

- **AppArmor is a Linux kernel feature.** It does not exist on Windows and there
  is no equivalent switch in the Windows kernel.
- Run this exercise on a **Linux host**, or on **WSL2 running a Linux Docker
  engine** (Docker Engine installed inside the WSL2 distribution, or Docker
  Desktop with the WSL2 backend where you work inside the distribution and talk
  to the same daemon).
- **Windows Docker Desktop cannot apply it.** The daemon runs in a Linux VM
  whose kernel you do not load profiles into from Windows, so
  `--security-opt apparmor=devops-demo` is rejected with an error such as
  `invalid argument` or `AppArmor profile is not loaded`. Do not expect the
  checks below to pass on a Windows-only setup.
- `apparmor-utils` installed on the host for `aa-status`, and
  `apparmor_parser` (part of `apparmor`) for loading the profile. On Debian or
  Ubuntu:

  ```bash
  sudo apt-get update
  sudo apt-get install -y apparmor apparmor-utils
  ```

- A user that may run `sudo`, and Docker with permission to run containers.
- Python 3.11 or newer for the two helper scripts.

## Steps

These commands are Linux shell commands. On WSL2, run them inside the WSL2
distribution, in the directory that holds these files.

1. Check that the kernel has AppArmor and that it is enabled.

   ```bash
   sudo aa-status
   ```

   The output starts with `apparmor module is loaded.` followed by counts of
   loaded profiles. If the module is not loaded, enable it in the host
   bootloader with `apparmor=1 security=apparmor` and reboot.

2. Load the profile. `-r` replaces an existing profile of the same name, `-W`
   only reports errors.

   ```bash
   python apply_apparmor.py
   ```

   The script prints the command it runs and the return code from
   `apparmor_parser`. It also prints an explanation and exits 2 when AppArmor is
   not available, which is what happens on Windows.

   The same thing by hand, if you prefer:

   ```bash
   sudo apparmor_parser -r -W my-apparmor-profile
   ```

3. Confirm that the profile is in the list.

   ```bash
   sudo aa-status | grep devops-demo
   ```

4. Build the image.

   ```bash
   docker build -t apparmor-demo:latest .
   ```

5. Run the container with the profile attached and watch what it prints.

   ```bash
   docker run --rm --security-opt apparmor=devops-demo apparmor-demo:latest
   ```

6. Run the automated checks.

   ```bash
   python test_restricted_actions.py
   ```

7. Compare with the same container without the profile. Both steps succeed,
   which shows that the denials in step 5 came from the profile.

   ```bash
   docker run --rm apparmor-demo:latest
   ```

8. Unload the profile when you are finished. `-R` removes it from the kernel.

   ```bash
   sudo apparmor_parser -R my-apparmor-profile
   ```

## Verification

The kernel reports the profile as loaded:

```bash
sudo aa-status
```

Expected shape of the output, on a host where AppArmor is enabled:

```text
apparmor module is loaded.
62 profiles are loaded.
58 profiles are in enforce mode.
   ...
   devops-demo
   ...
40 profiles are in complain mode.
   ...
8 processes have profiles defined.
6 processes are in enforce mode.
0 processes are in complain mode.
0 processes are unconfined but have a profile defined.
```

`devops-demo` has to appear in the enforce list, and `apparmor module is
loaded.` has to be the first line. On Windows, or on a kernel booted without
AppArmor, the command prints `apparmor module is not loaded.` or does not exist
at all.

The container prints one denied step and one allowed step:

```bash
docker run --rm --security-opt apparmor=devops-demo apparmor-demo:latest
```

Expected shape:

```text
apparmor demo starting
uid: 0
step 1: create /tmp/apparmor-demo and write /tmp/apparmor-demo/notes.txt
step 1 outcome: OK, /tmp/apparmor-demo/notes.txt written
step 2: read /etc/shadow
step 2 outcome: DENIED by PermissionError: [Errno 13] Permission denied: '/etc/shadow'
apparmor demo finished
```

The exit code is 0 in both cases, because the demo reports rather than fails:

```bash
docker run --rm --security-opt apparmor=devops-demo apparmor-demo:latest; echo "exit code: $?"
```

Expected last line:

```text
exit code: 0
```

The automated checks print one PASS per check:

```bash
python test_restricted_actions.py
```

Expected shape:

```text
image: apparmor-demo:latest
profile: devops-demo
--- read /etc/shadow is denied
    exit code: 1
    output: Traceback (most recent call last):
    ...
    PermissionError: [Errno 13] Permission denied: '/etc/shadow'
    PASS
--- write /tmp/apparmor-demo/notes.txt succeeds
    exit code: 0
    output: written
    PASS
result: PASS
```

The script exits 0 only when both lines read `PASS`. If the profile is not
loaded, the first check fails because the read succeeds, and the exit code of
`python test_restricted_actions.py` is 1.

Run the same container without the profile to see the difference:

```bash
docker run --rm apparmor-demo:latest
```

Expected:

```text
step 2 outcome: ALLOWED, /etc/shadow was readable
```

Note that `docker run --rm --security-opt apparmor=devops-demo` fails at start
time when the profile is missing. On Windows Docker Desktop the error mentions
the profile or reports an invalid argument, which is the documented limitation,
not a fault in the profile file.

## Files

- `app.py` - writes `/tmp/apparmor-demo/notes.txt`, then tries to read
  `/etc/shadow`, prints the outcome of each step and exits 0.
- `my-apparmor-profile` - AppArmor profile named `devops-demo` with
  `flags=(attach_disconnected,mediate_deleted)`; denies reads of `/etc/shadow`,
  allows writes only under `/tmp/apparmor-demo/`, and denies raw and packet
  network sockets. The first line states that it must be loaded on a Linux host.
- `apply_apparmor.py` - runs `sudo apparmor_parser -r -W my-apparmor-profile`
  through `subprocess`, prints the return code, and explains that AppArmor
  requires Linux. Exits 2 when the tools are not present.
- `test_restricted_actions.py` - runs the image with
  `--security-opt apparmor=devops-demo`, asserts that the `/etc/shadow` read is
  denied and that the `/tmp` write succeeds, prints `PASS` or `FAIL` per check,
  and exits non-zero when a check fails.
- `Dockerfile` - `python:3.11-slim` image that copies `app.py` and runs it with
  `python app.py`.
- `README.md` - this file.
