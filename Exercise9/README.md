# Exercise 9 - declarative pipeline

## Overview

A small Flask application is built, tested, deployed and started by a Jenkins
declarative pipeline. The pipeline creates a virtual environment, installs the
pinned dependency, runs the unit tests with `unittest`, copies the artefacts into
a deploy directory, starts the application in the background, polls `/health`
until it answers, and then verifies the health payload. A `post` block stops the
application again, whatever the outcome of the build.

The application itself is trivial on purpose: the point of the exercise is the
pipeline, and a trivial application keeps the build fast.

## Prerequisites

- Python 3.11 or newer with the `venv` module on the machine used for the local
  run.
- PowerShell 5.1 or newer.
- Jenkins with the Pipeline and Git plugins, from Exercise 7 or a native install.
- A Jenkins agent that provides `git`, `python3` with `venv`, `curl` and a POSIX
  shell. The controller container from Exercise 7 has none of the Python tools,
  so an end to end run needs an agent image with them, for example
  `jenkins/jenkins:lts-jdk21` extended with
  `apt-get install -y python3 python3-venv curl`.
- Free port 5000 on the agent, or a different value in the `PORT` environment
  variable of the pipeline.
- The `Jenkinsfile` must use LF line endings. Its `sh` blocks are passed to the
  agent shell, and carriage returns make `set -eu` fail with
  `set: Illegal option`. The copy in this repository is stored with LF.

## Steps

### Local run

1. Create and activate the virtual environment.

   ```powershell
   cd .\Exercise9\python-flask-app
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If the execution policy blocks the activation script, allow it for this
   session only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the dependency.

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run the unit tests exactly as the pipeline does.

   ```powershell
   python -m unittest discover -s . -p "test_*.py" -v
   ```

4. Start the application and look at both endpoints.

   ```powershell
   python app.py
   ```

   In a second PowerShell window:

   ```powershell
   curl.exe -s http://localhost:5000/
   curl.exe -s http://localhost:5000/health
   ```

5. Stop the application with `Ctrl+C`, then leave the environment.

   ```powershell
   deactivate
   ```

   To remove it completely:

   ```powershell
   Remove-Item -Recurse -Force .\.venv
   ```

### Jenkins Pipeline from SCM

1. Push this repository to the Git host and store a personal access token as a
   Jenkins credential, as described in Exercise 8. The pipeline needs read access
   to the repository only.

2. `New Item` -> name `Exercise9-Pipeline` -> `Pipeline` -> `OK`.

3. Under `Pipeline` select `Pipeline script from SCM`.

   | Field | Value |
   | --- | --- |
   | SCM | `Git` |
   | Repository URL | `https://github.com/<your-account>/Devops_ISE.git` |
   | Credentials | the credential created in step 1 |
   | Branch Specifier | `*/main` |
   | Script Path | `Exercise9/Jenkinsfile` |

## Verification

1. The unit tests pass locally, with four tests.

   ```powershell
   cd .\Exercise9\python-flask-app
   python -m unittest discover -s . -p "test_*.py" -v
   ```

   Expected output ends with:

   ```text
   Ran 4 tests in 0.0xx s

   OK
   ```

2. The application answers locally.

   ```powershell
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:5000/
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:5000/health
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:5000/no-such-page
   curl.exe -s http://localhost:5000/health
   ```

   Expected output: `200`, `200`, `404`, then `{"status":"ok"}`.

3. The pipeline build succeeds. The console output of the `Verify` stage contains
   the health payload, and the build ends green:

   ```text
   health response: {"status":"ok"}
   ...
   Build result: SUCCESS
   Finished: SUCCESS
   ```

4. The deploy stage produced the artefacts, and the `post` block removed the pid
   file of the stopped process.

   ```powershell
   docker exec jenkins ls -l /var/jenkins_home/workspace/Exercise9-Pipeline/Exercise9/python-app-deploy
   ```

   Expected output: `.gitkeep`, `app.py`, `requirements.txt` and `app.log`. The
   file `app.pid` is gone, because `post` deleted it after stopping the process.

5. Run the build a second time without cleaning the workspace. It must still pass,
   which shows that `disableConcurrentBuilds()` and the `post` cleanup leave a
   usable workspace behind.

6. Check that the pipeline file has the required shape:

   ```powershell
   Select-String -Path .\Exercise9\Jenkinsfile -Pattern "timeout\(time: 10, unit: 'MINUTES'\)|disableConcurrentBuilds\(\)|stage\('"
   ```

   Expected output: one line for each of the two options and one line per stage
   name.

## Files

| File | Purpose |
| --- | --- |
| `Jenkinsfile` | Declarative pipeline with the stages `Checkout`, `Build`, `Test`, `Deploy`, `Run Application` and `Verify`, a ten minute timeout, `disableConcurrentBuilds()`, and a `post` block that stops the application and echoes the build result |
| `python-flask-app/app.py` | Flask application: `/` returns an HTML page, `/health` returns `{"status":"ok"}`, the port comes from `PORT` and defaults to 5000 |
| `python-flask-app/requirements.txt` | Pins `flask==3.1.0` |
| `python-flask-app/test_app.py` | Four `unittest` cases that use `app.test_client()`: index status, index content, health payload, unknown path |
| `python-app-deploy/.gitkeep` | Keeps the deploy directory in Git; the `Deploy` stage copies `app.py` and `requirements.txt` here, and `post` removes `app.pid` |
| `README.md` | These steps, the local PowerShell commands and the Pipeline from SCM configuration |


4. Under `Build Triggers`, optionally enable `Poll SCM` with the schedule
   `H/5 * * * *` so a push is picked up within five minutes.

5. `Save`, then `Build Now`.

6. The pipeline runs six stages: `Checkout`, `Build`, `Test`, `Deploy`,
   `Run Application` and `Verify`. The `post` block always runs, so the
   application process is stopped even when a stage fails.
