# Exercise 8 - Freestyle job that runs a script from Git

## Overview

A Jenkins Freestyle job pulls a small repository from Git and runs
`hello-world.sh` from it as a build step. The point of the exercise is the
credential flow: Jenkins reads the repository with a fine-grained personal
access token that has exactly one permission, and the token is stored in the
Jenkins credential store rather than in the repository or in the job
configuration.

## Prerequisites

- Jenkins reachable on http://localhost:8080, as set up in Exercise 7.
- The Git plugin installed, which is part of the suggested plugin set.
- A Git host account that can create a repository, for example GitHub.
- Git on the machine that pushes the script, and PowerShell 5.1 or newer.

## Steps

1. Create an empty repository for the script, for example
   `jenkins-hello-world`, with a `main` branch.

2. Create a fine-grained personal access token for that repository only.

   - On GitHub: `Settings` -> `Developer settings` ->
     `Personal access tokens` -> `Fine-grained tokens` -> `Generate new token`.
   - `Repository access`: `Only select repositories`, then pick
     `jenkins-hello-world`.
   - `Permissions` -> `Repository permissions`: set `Contents` to
     `Read and write`.
   - Leave every other permission at `No access`. No account permissions, no
     `Metadata` change, no workflow scope.
   - Set a short expiry date and copy the token once. It cannot be read again.

   The token is a secret. It is never committed and never written into this
   directory.

3. Push `hello-world.sh` from this directory to the new repository.

   ```powershell
   cd .\Exercise8
   git init
   git remote add origin https://github.com/<your-account>/jenkins-hello-world.git
   git add hello-world.sh
   git commit -m "Add hello world build script"
   git branch -M main
   git push -u origin main
   ```

   When Git asks for credentials, use the account name as the user name and the
   token as the password. To avoid the prompt for the rest of the session:

   ```powershell
   git -c credential.helper= push -u origin main
   ```

4. Store the token in Jenkins. Open
   `Manage Jenkins` -> `Credentials` -> `System` -> `Global credentials` ->
   `Add Credentials`.

   | Field | Value |
   | --- | --- |
   | Kind | `Username with password` |
   | Username | the Git host account name |
   | Password | the personal access token |
   | ID | `github-jenkins-hello-world` |
   | Description | fine-grained token, Contents read and write |

5. Create the job: `New Item`, name `Hello-World-Job`, type `Freestyle project`,
   then `OK`.

6. In `Source Code Management` select `Git`.

   | Field | Value |
   | --- | --- |
   | Repository URL | `https://github.com/<your-account>/jenkins-hello-world.git` |
   | Credentials | `github-jenkins-hello-world` |
   | Branch Specifier | `*/main` |

7. In `Build Steps` add `Execute shell` and enter exactly:

   ```sh
   sh hello-world.sh
   ```

   The script is invoked through `sh`, so it does not need the executable bit.
   Keep the file with LF line endings: it runs under `sh` on a Linux agent, and a
   carriage return makes `set -eu` fail with `set: Illegal option`. The copy in
   this repository is stored with LF.
   On a Windows agent the step would be `Execute Windows batch command`; the
   laboratory agents are Linux containers.

8. Save the job and choose `Build Now`. Open the build in `Build History` and
   read `Console Output`.

## Verification

1. The console output of build #1 contains the greeting and the date.

   Expected output, in order:

   ```text
   Started by user ...
   Running as SYSTEM
   Building in workspace /var/jenkins_home/workspace/Hello-World-Job
   ...
   + sh hello-world.sh
   Hello, Jenkins!
   Current date: 2026-01-15 10:42:07 UTC
   Finished: SUCCESS
   ```

   The exact timestamp depends on when the build ran. Both `Hello, Jenkins!` and
   `Finished: SUCCESS` must be present.

2. The workspace holds the file that Git delivered.

   ```powershell
   docker exec jenkins ls -l /var/jenkins_home/workspace/Hello-World-Job
   ```

   Expected output: a line for `hello-world.sh` and a hidden `.git` directory,
   which is the clone that the Git plugin created.

3. Run the script locally, without Jenkins, to confirm the script itself works.

   ```powershell
   docker run --rm -v "${PWD}:/work" -w /work python:3.11-slim sh hello-world.sh
   ```

   Expected output: `Hello, Jenkins!` followed by a `Current date:` line.

4. Change the script, push again, and run `Build Now` a second time. The console
   output of build #2 must show the changed text, which proves that the job reads
   the repository rather than a cached copy.

5. The token is not in the repository.

   ```powershell
   git -C .\Exercise8 remote -v
   Get-ChildItem .\Exercise8 -Recurse -File | Select-String -Pattern "github_pat_|ghp_" | Select-Object Path,LineNumber
   ```

   Expected output: the remote URL, then no match. A committed token would show
   up as a `github_pat_` line.

## Files

| File | Purpose |
| --- | --- |
| `hello-world.sh` | Build step script: prints `Hello, Jenkins!` and the current date, and fails the build if either command fails because of `set -eu` |
| `README.md` | These steps, the token scope, the job configuration and the verification commands |
