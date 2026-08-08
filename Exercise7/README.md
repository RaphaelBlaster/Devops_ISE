# Exercise 7 - Jenkins controller from an image

## Overview

Jenkins is started as a container from the official `jenkins/jenkins:lts-jdk21`
image. The build history, the jobs and the plugins live in the named volume
`jenkins-home`, so the container itself is disposable: it can be removed and
recreated without losing the configuration.

Two ports are published. Port 8080 serves the web UI. Port 50000 is the inbound
agent port, which a build agent uses to register with the controller.

## Prerequisites

- Docker Desktop with the Linux container engine, running.
- Docker Compose v2.
- Ports 8080 and 50000 free on the host.
- PowerShell 5.1 or newer.

## Steps

1. Start the controller.

   ```powershell
   cd .\Exercise7
   docker compose up -d
   ```

2. Wait until the container is running and print the first lines of the log.

   ```powershell
   docker compose ps
   docker compose logs --tail 20 jenkins
   ```

3. Read the initial administrator password. It is generated on the first start
   and stored inside the volume, not in the repository.

   ```powershell
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

4. Open http://localhost:8080 in a browser and paste the password from the
   previous step.

5. Choose `Install suggested plugins` and wait for the installation to finish.

6. Create the first administrator user with the form, or choose
   `Continue as admin` and change the password afterwards under
   `Manage Jenkins` -> `Users`. Either way the account is stored in
   `jenkins-home`, so it survives a container restart.

7. Optionally install further plugins under
   `Manage Jenkins` -> `Plugins`. Configuration as code, the Pipeline plugins and
   the Git plugin are the ones the later exercises rely on.

8. Stop and restart the controller. All jobs and plugins are still there,
   because they live in the volume.

   ```powershell
   docker compose restart
   ```

9. Stop the controller, and remove the volume only when a clean slate is wanted.

   ```powershell
   docker compose down
   docker compose down -v
   ```

### Container names

Docker requires every container name to be unique on the machine. This Compose
file sets `container_name: jenkins`, so a second Jenkins stack started from a
copy of this directory fails with:

```text
Error response from daemon: Conflict. The container name "/jenkins" is already in use
```

Reuse the container that already exists instead of starting a second one:

```powershell
docker ps -a --filter "name=jenkins"
docker start jenkins
docker exec -it jenkins bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

If the existing container is not the one that is wanted, remove it and start
again. `docker compose down` removes the container but keeps the volume, so
`docker compose up -d` afterwards brings back the same Jenkins home:

```powershell
docker compose down
docker compose up -d
```

A container name can also be dropped from the Compose file, in which case
Compose generates names such as `jenkins-jenkins-1` and several stacks can run
side by side as long as their published ports differ.

## Verification

1. The container runs.

   ```powershell
   docker compose ps
   ```

   Expected output: one row for the `jenkins` service with state `running` and
   the mappings `0.0.0.0:8080->8080/tcp` and `0.0.0.0:50000->50000/tcp`.

2. The web UI answers.

   ```powershell
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8080/login
   ```

   Expected output: `200`.

3. The initial password exists and is not empty.

   ```powershell
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

   Expected output: a single line of 32 hexadecimal characters.

4. The volume is attached to the container.

   ```powershell
   docker inspect --format "{{json .Mounts}}" jenkins
   ```

   Expected output: a JSON array with one element containing
   `"Name":"jenkins-home"` and `"Destination":"/var/jenkins_home"`.

5. After signing in, http://localhost:8080 shows the Jenkins dashboard with the
   suggested plugins installed.

6. The password and any personal access tokens stay out of the repository. The
   file `.gitignore` in the repository root excludes `.env` and `*.token`, and
   nothing in this directory contains a credential:

   ```powershell
   Get-ChildItem .\Exercise7 -Recurse -File | Select-String -Pattern "initialAdminPassword|token|password" | Select-Object Path,LineNumber
   ```

   Expected output: no line from `docker-compose.yml`, and no file with a stored
   secret. The word `password` may only appear in this README as part of the
   command that reads the password out of the running container.

## Files

| File | Purpose |
| --- | --- |
| `docker-compose.yml` | Starts `jenkins/jenkins:lts-jdk21` as container `jenkins`, publishes 8080 and 50000, keeps `/var/jenkins_home` in the volume `jenkins-home`, restarts unless stopped, and notes that agents need their own Docker access to build images |
| `README.md` | These steps, the verification commands and the notes on container names and credentials |
