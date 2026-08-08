# Kubernetes setup on Windows

## Overview

This directory holds the one-time setup for the Kubernetes exercises in this
repository. `install.ps1` installs Chocolatey when it is missing, then installs
the two packages the exercises need:

- `minikube` - the single-machine cluster used by Exercise 3 and Exercise 10.
- `kubernetes-cli` - the `kubectl` client that talks to that cluster.

The script is idempotent. It checks each item before touching it, so a second
run on a working machine only prints the version output and changes nothing.

## Prerequisites

- Windows 10 or 11, 64-bit, with PowerShell 5.1 or newer.
- An administrator account. The script refuses to run in a normal shell because
  Chocolatey and both packages install machine-wide.
- Hardware virtualisation enabled. Minikube needs a virtual machine, either
  through Hyper-V or through the Linux virtual machine that Docker Desktop runs.
  On Windows 11 this is the "Virtual Machine Platform" and "Windows Hypervisor
  Platform" pair of features.
- Either Docker Desktop with the Linux container engine, or the Hyper-V feature.
  The `docker` driver is the one used by the exercise READMEs and is the easiest
  path; the `hyperv` driver works without Docker Desktop.
- At least 4 GB of free memory and about 3 GB of free disk space for the images
  and the cluster.
- An internet connection for the Chocolatey packages and for the cluster images
  that Minikube pulls on first start.

## Steps

1. Open PowerShell as administrator: press Start, type `PowerShell`, right-click
   "Windows PowerShell", choose "Run as administrator".

2. Allow the script to run in this session and start it. The script checks for an
   elevated shell itself, so this is only a convenience.

   ```powershell
   Set-Location .\K8s-Setup
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\install.ps1
   ```

   If script execution is blocked by policy, run it in a child process instead:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```

3. Open a new PowerShell window so the updated `PATH` is picked up, then confirm
   both tools answer.

   ```powershell
   minikube version
   kubectl version --client
   ```

4. Start the cluster. Docker Desktop must be running before this command.

   ```powershell
   minikube start --driver=docker
   ```

   The first start downloads the node image and takes a few minutes. To give the
   cluster a name of its own, add `-p devops`; every later command then needs the
   same `-p devops` flag.

5. Check the cluster state.

   ```powershell
   minikube status
   kubectl get nodes
   ```

6. Open the dashboard, which runs as an addon inside the cluster.

   ```powershell
   minikube dashboard
   ```

   The command keeps running and opens a browser tab. Stop it with Ctrl+C when
   you are finished; the addon itself keeps running.

7. Stop the cluster without deleting it. Containers and images stay on disk, and
   `minikube start` brings the same cluster back.

   ```powershell
   minikube stop
   ```

8. Delete the cluster and everything in it, including the loaded images. Do this
   before starting an exercise from scratch.

   ```powershell
   minikube delete
   ```

   To remove every profile at once:

   ```powershell
   minikube delete --all
   ```

9. Useful checks when a start fails.

   ```powershell
   minikube logs
   minikube ssh -- free -m
   minikube config view
   ```

   `minikube config view` lists the saved defaults, for example a driver or a
   memory value that a later `minikube start` silently reuses.

### Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Unable to find driver "docker"` or `No possible driver was detected` | Docker Desktop is not running, or it runs Windows containers | Start Docker Desktop, wait for the whale icon to stop animating, switch it to Linux containers, then `minikube start --driver=docker` again |
| `This computer doesn't have VT-x/AMD-v enabled` or `virtualization support is not enabled` | Virtualisation is switched off in the firmware | Reboot into BIOS/UEFI, enable Intel VT-x or AMD-V (sometimes named SVM), save and reboot; check with `systeminfo` and look at the Hyper-V requirements block |
| `start: port 8443 is already in use` or the dashboard does not open | Another process holds the port, often an old Minikube cluster or another Kubernetes tool | Find it with `Get-Process -Id (Get-NetTCPConnection -LocalPort 8443).OwningProcess` or `netstat -ano \| findstr 8443`, stop that process, or run `minikube delete` and start again |
| `Insufficient memory` / the node image never finishes booting | The profile asks for more memory than the machine has free | Close other virtual machines and browsers, then `minikube start --driver=docker --memory=1800`; for a multi-node profile give each node its own share or use fewer nodes |
| `minikube start` fails with a Hyper-V error after VirtualBox was installed, or VirtualBox refuses to start | Hyper-V and VirtualBox both want the hardware virtualisation extensions and cannot share them | Pick one: remove the Hyper-V and Virtual Machine Platform features with `Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All`, reboot, and use VirtualBox; or keep Hyper-V and use the `hyperv` or `docker` driver and drop VirtualBox |
| `choco` is not recognised after install | The package wrote the new `PATH` but this shell still has the old one | Close the window and open a new PowerShell; or run `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine')` |
| `minikube` and `kubectl` are not found after a reboot | The install added the tools to a PATH entry the shell does not read | Re-run `.\install.ps1`; it skips the installs it already has and re-prints the versions |

## Verification

`install.ps1` ends with both version commands, so its own output is the first
check. Expected shape:

```text
==> minikube version
minikube version: v1.34.0
commit: 38f9d5b0f9a3c1f7c9c5b7e0e2c3f8d1a2b4c6e8

==> kubectl version --client
Client Version: v1.34.0
Kustomize Version: v5.5.0
```

The exact version numbers depend on the day you install. What matters is that
both commands print a version instead of a "not recognised" error.

Then the cluster itself. After `minikube start --driver=docker` and
`minikube status`, the status command reports each component:

```text
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

The single node must be `Ready`:

```powershell
kubectl get nodes
```

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   94s   v1.34.0
```

`STATUS Ready` is the pass condition: the node registered with the API server
and its kubelet is reporting healthy. `NotReady` right after a start usually
means the container runtime inside the node is still coming up; wait thirty
seconds and repeat the command.

A final check that the client is talking to the Minikube context and not to some
other cluster:

```powershell
kubectl config current-context
kubectl get ns
```

```text
minikube
```

```text
NAME              STATUS   AGE
default           Active   2m
kube-node-lease   Active   2m
kube-public       Active   2m
kube-system       Active   2m
```

The context must be `minikube`, and the four namespaces above are the ones a
fresh cluster always has.

`minikube stop` then `minikube status` must show `host: Stopped` for the control
plane, and `minikube start` must bring the same node back to `Ready`. That
confirms the profile is reusable and the exercises do not need a fresh install
each time.

## Files

- `install.ps1` - idempotent setup script. Checks for an elevated shell, installs
  Chocolatey when `choco` is missing (using a process-scoped
  `Set-ExecutionPolicy Bypass`), installs the `minikube` and `kubernetes-cli`
  packages when their commands are missing, refreshes the session `PATH`, and
  finishes by printing `minikube version` and `kubectl version --client`.
- `README.md` - this file.
