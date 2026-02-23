# Vera GCP — Tests

This directory contains the test suite for the GCP Compute Emulator.

## test.sh

`test.sh` contains 76 `gcpcli` (gcloud compute) commands covering the full lifecycle of 18 resource types:

- Zones and regions
- Machine types (list, describe)
- Networks and subnetworks
- Firewall rules
- Addresses (regional)
- Disks and snapshots
- Instances (create, describe, stop, start, delete)
- Health checks
- Backend services
- URL maps
- Target HTTP proxies
- Forwarding rules (global)
- Instance templates
- Operations (zone and global list)

Commands run end-to-end: create → describe → (stop/start where applicable) → delete. All 76 commands pass against the emulator.

## Running

Start the emulator in one terminal:

```bash
uv run main.py
# GCP Compute Emulator listening on 127.0.0.1:9100
```

Run the tests in another terminal:

```bash
source .venv/bin/activate
bash tests/test.sh
```

## cli/gcp_commands.json

Catalogue of gcloud compute commands with expected outputs, used for automated evaluation. Load it with `tests/utils/parse_gcp_commands.py`.

## tf/

Four Terraform example configurations using the `google` provider, pointed at the local emulator via:

```hcl
provider "google" {
  project      = "vera-project"
  region       = "us-central1"
  access_token = "vera-local-token"
  endpoints {
    compute = "http://localhost:9100/"
  }
}
```
