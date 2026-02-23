# Hello World — single GCP Compute instance

Deploys a single Compute Engine VM in the default network.

## Usage

```bash
# Point Terraform at the emulator
export GOOGLE_BACKEND_OVERRIDE=http://localhost:9100

terraform init
terraform apply -auto-approve
```
