#!/usr/bin/env bash
set -e

OS="$(uname -s)"
ENDPOINT="${VERA_ENDPOINT:-http://localhost:9100}"
PROJECT="${VERA_PROJECT:-vera-project}"

# --- uv ---
if ! command -v uv >/dev/null 2>&1; then
    echo "==> uv not found, installing..."
    if [ "$OS" = "Darwin" ] || [ "$OS" = "Linux" ]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "!!! uv auto-install only supported on macOS/Linux."
        exit 1
    fi
fi

uv sync
# Optional: install the google-cloud-compute Python SDK for SDK-based testing
# uv sync --extra sdk
source .venv/bin/activate

echo "==> Vera GCP installer  (endpoint: $ENDPOINT, project: $PROJECT)"

# --- Google Cloud SDK (gcloud CLI) ---
if command -v gcloud >/dev/null 2>&1; then
    echo "==> gcloud found: $(gcloud version 2>&1 | head -1)"
else
    echo "==> gcloud not found, attempting install..."
    installed=false

    if [ "$OS" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
        brew install --cask google-cloud-sdk && installed=true
        GCLOUD_BREW="$(brew --prefix)/share/google-cloud-sdk"
        [ -f "$GCLOUD_BREW/path.bash.inc" ] && source "$GCLOUD_BREW/path.bash.inc"
    elif [ "$OS" = "Linux" ]; then
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update -qq
            sudo apt-get install -y -qq apt-transport-https ca-certificates gnupg
            curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
                | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg 2>/dev/null
            echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
                | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null
            sudo apt-get update -qq && sudo apt-get install -y -qq google-cloud-cli && installed=true
        elif command -v yum >/dev/null 2>&1; then
            sudo tee /etc/yum.repos.d/google-cloud-sdk.repo << 'REPO'
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
REPO
            sudo yum install -y google-cloud-cli && installed=true
        fi
    fi

    if [ "$installed" = false ]; then
        echo "!!! Could not auto-install gcloud. Install manually:"
        echo "    https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
fi

# --- Disable gcloud auth for local emulator use ---
# We set a fake OAuth access token so gcloud skips the auth flow entirely.
# The emulator accepts any bearer token without validation.
# GOOGLE_OAUTH_ACCESS_TOKEN is the official gcloud env var for a pre-obtained token.
GCLOUD_CONFIG_DIR="${CLOUDSDK_CONFIG:-$HOME/.config/gcloud}"
mkdir -p "$GCLOUD_CONFIG_DIR"

# Suppress the "You do not appear to have access to project" warnings
gcloud config set core/disable_usage_reporting true 2>/dev/null || true
gcloud config set core/project "$PROJECT" 2>/dev/null || true

# Write a minimal properties file that disables auth prompts globally
PROPERTIES_FILE="$GCLOUD_CONFIG_DIR/properties"
if ! grep -q '\[core\]' "$PROPERTIES_FILE" 2>/dev/null; then
    cat >> "$PROPERTIES_FILE" << 'PROPS'

[core]
disable_usage_reporting = true
PROPS
fi

# --- gcpcli wrapper ---
# Drop-in for "gcloud compute". Injects the emulator endpoint and a fake token
# so no real GCP project or credentials are needed.
BIN_DIR="$(pwd)/.venv/bin"
VERA_CONFIG_DIR="$(pwd)/.venv/vera-gcloud-config"
mkdir -p "$BIN_DIR" "$VERA_CONFIG_DIR"

# Resolve the full path to gcloud so the wrapper works regardless of PATH
GCLOUD_BIN="$(command -v gcloud)"
if [ -z "$GCLOUD_BIN" ]; then
    echo "!!! gcloud not found in PATH — wrapper will try 'gcloud' at runtime"
    GCLOUD_BIN="gcloud"
fi

# Write a static fake access token file — used by --access-token-file so gcloud
# never performs account credential lookup (more reliable than GOOGLE_OAUTH_ACCESS_TOKEN
# when a specific account is configured).
TOKEN_FILE="${VERA_CONFIG_DIR}/access_token"
echo "vera-local-token" > "$TOKEN_FILE"

# Pre-populate an isolated gcloud config dir (no account set — avoids credential checks).
CLOUDSDK_CONFIG="$VERA_CONFIG_DIR" "$GCLOUD_BIN" config set core/project "$PROJECT" 2>/dev/null || true
CLOUDSDK_CONFIG="$VERA_CONFIG_DIR" "$GCLOUD_BIN" config set core/disable_usage_reporting true 2>/dev/null || true
CLOUDSDK_CONFIG="$VERA_CONFIG_DIR" "$GCLOUD_BIN" config set core/disable_prompts true 2>/dev/null || true

cat > "$BIN_DIR/gcpcli" << EOF
#!/bin/bash
# Vera GCP — local emulator wrapper for gcloud compute
# No real GCP account or credentials needed — all calls go to the local emulator.
exec env \\
  CLOUDSDK_CONFIG="${VERA_CONFIG_DIR}" \\
  CLOUDSDK_API_ENDPOINT_OVERRIDES_COMPUTE="${ENDPOINT}/" \\
  CLOUDSDK_CORE_DISABLE_PROMPTS="1" \\
  CLOUDSDK_CORE_PROJECT="${PROJECT}" \\
  "${GCLOUD_BIN}" compute --access-token-file="${TOKEN_FILE}" "\$@"
EOF
chmod +x "$BIN_DIR/gcpcli"

echo ""
echo "==> Done!"
echo ""
echo "    Start the emulator:"
echo "      uv run main.py"
echo ""
echo "    Run compute commands (no real GCP account needed):"
echo "      uv run gcpcli instances list"
echo "      uv run gcpcli disks list"
