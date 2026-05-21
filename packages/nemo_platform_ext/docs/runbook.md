# CLI Runbook

## Configuration Management

### First-Time Setup

```bash
# Set the base URL and authenticate
nemo config set --base-url https://nmp.dev.example.com
nemo auth login

# Or configure a named context
nemo config set --context prod --base-url https://nmp.prod.example.com --activate
nemo auth login
```

### View Config

```bash
nemo config view                    # Full config (YAML format)
nemo config view -f json            # JSON format
nemo config view --minify           # Show only current context and its references
```

### List Resources

```bash
# List all clusters
nemo config get-clusters
nemo config get-clusters -f json

# List all contexts (shows current context indicator)
nemo config get-contexts
nemo config get-contexts my-context    # Get specific context details

# List all users
nemo config get-users
nemo config get-users -f json
```

### Quick Configuration

Set values on the current (or specified) context:

```bash
# Set base URL on current context's cluster
nemo config set --base-url https://api.example.com

# Set access token on current context's user
nemo config set --access-token YOUR_ACCESS_TOKEN
nemo config set --access-token -            # Prompt for token securely

# Set default workspace
nemo config set --workspace production

# Set output preferences
nemo config set --output-format json --timestamp-format relative

# Set values on a specific context
nemo config set --context staging --workspace dev

# Activate a context while setting values
nemo config set --context prod --activate --workspace production
```

### Context Management

```bash
nemo config current-context         # Show current context name
nemo config use-context staging     # Switch to a different context
```

### Cluster Management

```bash
# Create a new cluster
nemo config set-cluster my-cluster --base-url https://api.example.com

# Update existing cluster
nemo config set-cluster my-cluster --base-url https://new-api.example.com

# Delete a cluster (will fail if any contexts reference it)
nemo config delete-cluster my-cluster

# To delete a cluster that is referenced by contexts:
# 1. First delete the referencing contexts or update them to reference a different cluster
nemo config delete-context my-context
# 2. Then delete the cluster
nemo config delete-cluster my-cluster
```

### User Management

```bash
# Create user with access token
nemo config set-user my-user --access-token YOUR_ACCESS_TOKEN

# Create user with secure token prompt
nemo config set-user my-user --access-token -

# Create user without authentication
nemo config set-user anonymous --no-auth

# Delete a user (will fail if any contexts reference it)
nemo config delete-user my-user

# To delete a user that is referenced by contexts:
# 1. First delete the referencing contexts or update them to reference a different user
nemo config set-context my-context --user different-user
# 2. Then delete the user
nemo config delete-user my-user
```

### Context Configuration

```bash
# Create a new context (requires existing cluster and user)
nemo config set-context my-context --cluster my-cluster --user my-user

# Create context with workspace and preferences
nemo config set-context my-context --cluster my-cluster --user my-user \
  --workspace production --output-format json --page-size 50

# Update existing context
nemo config set-context my-context --workspace staging
nemo config set-context my-context --output-format table --timestamp-format relative

# Delete a context
nemo config delete-context my-context
```

## Common Operations

### List Resources

```bash
nemo workspaces list

# With pagination
nemo workspaces list --page 1 --page-size 20

# Fetch all pages
nemo workspaces list --all-pages

# Filter columns
nemo workspaces list --output-columns id,description,created_at
```

### Get Resource

```bash
nemo workspaces get my-workspace
```

### Create Resource

```bash
# From inline data
nemo workspaces create --input-data '{"id": "dev", "description": "Development"}'

# From file
nemo workspaces create --input-file config.json

# From stdin
cat config.json | nemo workspaces create --input-file -

# With field overrides
nemo workspaces create --input-file base.json --id "production"
```

### Update Resource

```bash
nemo workspaces update my-workspace --input-file updates.json
nemo workspaces update my-workspace --input-data '{"description": "Updated"}'
```

### Delete Resource

```bash
nemo workspaces delete my-workspace
```

## Output Formats

```bash
nemo workspaces list -f table       # Default: rich table
nemo workspaces list -f json        # Pretty JSON
nemo workspaces list -f yaml        # YAML
nemo workspaces list -f markdown    # Markdown table
nemo workspaces list -f csv         # CSV
nemo workspaces list -f raw         # Compact JSON
nemo workspaces list -f code        # Python SDK code
```

### Export to File

```bash
nemo workspaces list --all-pages --no-truncate -f markdown > workspaces.md
nemo workspaces list -f csv > workspaces.csv
```

## Multiple Contexts

```bash
# Create cluster and user first
nemo config set-cluster prod-cluster --base-url https://api.prod.com
nemo config set-user prod-user --access-token -

# Create production context
nemo config set-context prod --cluster prod-cluster --user prod-user

# Create staging cluster and context
nemo config set-cluster staging-cluster --base-url https://api.stage.com
nemo config set-user staging-user --access-token -
nemo config set-context staging --cluster staging-cluster --user staging-user

# Switch between contexts
nemo config use-context staging
nemo config current-context         # Shows: staging

# Use context override for single command
nemo --context prod workspaces list
```

## Environment Variables

Override any setting via environment variables:

```bash
# Override config file path
NMP_CONFIG_FILE=/etc/nmp/config.yaml nemo config view

# Override base URL for single command
NMP_BASE_URL=http://localhost:8080 nemo workspaces list

# Set defaults for session
export NMP_OUTPUT_FORMAT=json
export NMP_WORKSPACE=dev
```

## Troubleshooting

### Base URL Not Set

```
Error: Base URL not specified
```

Fix: Set via config, env var, or CLI flag:
```bash
nemo config set-cluster my-cluster --base-url https://nmp.example.com
# or
export NMP_BASE_URL=https://nmp.example.com
# or
nemo --base-url https://nmp.example.com workspaces list
```

### No Config File Found

```
Error: No config file found
```

Fix: Set the base URL:
```bash
nemo config set --base-url https://nmp.example.com
```

### Debug Mode

Enable verbose logging:
```bash
nemo -v workspaces list
```

## Testing Commands

### Unit Tests

```bash
cd packages/nemo_platform_ext
uv run pytest
```
