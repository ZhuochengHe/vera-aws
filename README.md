
<h1 align="center">Vera: True Simulation of Any Cloud</h1>

<p align="center">
  <img src="assets/vera-cloud.png" alt="Vera" width="80%">
</p>

<p align="center">
💻 A <b>high-fidelity, multi-cloud emulator</b> that runs entirely on your laptop.
</p>

<p align="center">
🛠️ Build and test cloud infrastructure locally — <b>no cloud accounts, no billing, no risk</b>.
</p>

<p align="center">
☁️ <b>Full API coverage</b>: Amazon EC2 (89 resources) and GCP Compute (91 resources).
</p>

<h2 align="center">The world's first anycloud emulator</h2>



## What is Vera?

<p align="center">
  <img src="assets/workflow.png" alt="Workflow" width="90%">
</p>

Cloud infrastructure is expensive to experiment with. Even a quick test — spinning up a virtual machine, creating a network, attaching a disk — means provisioning real resources, waiting on remote APIs, and paying for what you use. Mistakes cost money and time, especially in a shared environment.

Vera runs the cloud on your laptop. It mimics the APIs of Amazon Web Services and Google Cloud Platform locally, so your tools: CLI, Terraform, Python SDKs behave exactly as they would against the real thing, except everything happens on your machine in milliseconds, with no credentials, no cost, no safety concerns, and no cleanup required.


## Why Vera?

<p align="center">
  <img src="assets/why-vera2.png" alt="Why Vera" width="80%">
</p>

**No account needed.** Vera ships with fake credentials built in. You never authenticate against a real cloud provider, which means there's nothing to sign up for, nothing to configure, and no risk of accidentally hitting production.

**Fast feedback.** Because requests never leave your machine, operations that would take seconds or minutes against a real cloud complete instantly. Iterating on infrastructure code becomes as fast as iterating on any other code.

**Works with your existing tools.** Vera doesn't require you to change how you write infrastructure. Standard AWS CLI commands, standard `gcloud` commands, standard Terraform configurations — all of them work against Vera without modification.

**Safe by default.** There's no way to accidentally destroy a real resource or incur a surprise bill. Every resource lives in memory and disappears when you stop the emulator.

**Broad coverage.** Vera covers 89 AWS EC2 resource types and 91 GCP Compute resource types — VPCs, instances, disks, firewalls, load balancers, routing, snapshots, and much more. It handles the full lifecycle of the resources developers actually use day to day.


## The Emulators

### Vera AWS

Emulates the Amazon EC2 API with support for 89 resource types. Drop-in wrappers for the AWS CLI (`awscli`) and Terraform (`terlocal`) are included, so you can run your existing commands and configurations unchanged.

In head-to-head testing against 260 real AWS CLI commands, Vera AWS passes **80%** — compared to **47%** for LocalStack.

→ [Vera AWS documentation](emulators/aws-ec2/README.md)

---

### Vera GCP

Emulates the Google Cloud Compute API with support for 91 resource types. A drop-in wrapper for the gcloud CLI (`gcpcli`) handles credential isolation automatically, so `gcloud compute` commands route to the local emulator with no real Google account required. The Google Cloud Compute Python SDK is also supported.

Seeded resources (a default network, common zones, machine types, and image families) are available immediately on startup with no setup needed.

→ [Vera GCP documentation](emulators/google-compute/README.md)

---

## Quick Start

Each emulator lives in its own directory under `emulators/`. Setup is a single command:

```bash
# AWS
cd emulators/aws-ec2
./install.sh

# GCP
cd emulators/google-compute
./install.sh
```

From there, use `awscli`, `terlocal`, or `gcpcli` exactly as you would their real counterparts. See the individual READMEs for usage examples, test suites, and the full list of supported resources.

## Testing a CLI command

After finishing the setup, start the emulator. 

```bash
cd emulators/aws-ec2

uv run main.py
```

Test your CLI commands in another terminal. 

```bash
cd emulators/aws-ec2

uv run awscli ec2 create-vpc --cidr-block 10.0.0.0/16
```

A response will be generated.
```json
{
    "Vpc": {
        "OwnerId": "",
        "InstanceTenancy": "default",
        ...
    }
}
```


## Supported Resources (More resources coming soon!)

| Emulator | Resources Types|
|---|---|
| Vera AWS | 89 EC2 resources|
| Vera GCP | 91 Compute resources|

Full resource lists are in each emulator's README and on the [Vera website](https://project-vera.github.io/).
