# One Webserver with Variables — parameterized GCP instance + firewall

Deploys a VM web server where the port is configurable via an input variable.

## Usage

```bash
export GOOGLE_BACKEND_OVERRIDE=http://localhost:9100

# Use default port (8080)
terraform init && terraform apply -auto-approve

# Use a custom port
terraform apply -auto-approve -var="server_port=9090"
```
