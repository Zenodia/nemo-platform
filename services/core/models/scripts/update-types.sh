#!/usr/bin/env bash
#
# Update NIM Operator Types
#
# This script clones the k8s-nim-operator repository, generates Pydantic types
# from the CRD definitions, and cleans up the cloned repository.
#
# Usage:
#   ./scripts/update-types.sh                    # List available versions
#   ./scripts/update-types.sh --version v2.0.2   # Generate types from specific version

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the models service directory (parent of scripts/)
MODELS_DIR="$(dirname "$SCRIPT_DIR")"

OPERATOR_DIR="${MODELS_DIR}/k8s-nim-operator"
OPERATOR_REPO="https://github.com/NVIDIA/k8s-nim-operator.git"

VERSION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--version <tag>]"
            exit 1
            ;;
    esac
done

echo "================================================================================"
echo "NIM Operator Type Generator"
echo "================================================================================"
echo ""

# Step 1: Clone or update the k8s-nim-operator repository
if [ -d "$OPERATOR_DIR" ]; then
    echo "📁 Repository already exists at: $OPERATOR_DIR"
    echo "   Fetching latest tags..."
    cd "$OPERATOR_DIR"
    git fetch --tags --quiet
    cd "$MODELS_DIR"
else
    echo "📥 Cloning k8s-nim-operator repository..."
    git clone --quiet "$OPERATOR_REPO" "$OPERATOR_DIR"
    echo "   ✓ Cloned to: $OPERATOR_DIR"
fi
echo ""

# Step 2: If no version specified, list available tags
if [ -z "$VERSION" ]; then
    echo "📋 Available versions (tags):"
    echo ""
    cd "$OPERATOR_DIR"
    git tag --list --sort=-version:refname | head -20
    echo ""
    echo "================================================================================"
    echo "To generate types for a specific version, run:"
    echo "  $0 --version <tag>"
    echo ""
    echo "Example:"
    echo "  $0 --version v3.0.0"
    echo "================================================================================"
    echo ""
    echo "Repository left at: $OPERATOR_DIR"
    echo "To remove it manually: rm -rf $OPERATOR_DIR"
    exit 0
fi

# Step 3: Checkout the specified version
echo "🔖 Checking out version: $VERSION"
cd "$OPERATOR_DIR"
if ! git checkout --quiet "$VERSION" 2>/dev/null; then
    echo "   ✗ Error: Version '$VERSION' not found"
    echo "   Available tags:"
    git tag --list | head -20
    exit 1
fi
echo "   ✓ Checked out: $VERSION"
echo ""

# Step 4: Generate the Pydantic types
echo "🔨 Generating Pydantic types from CRDs..."
cd "$MODELS_DIR"
uv run python scripts/generate_nim_types.py --version "$VERSION"
echo ""

# Step 5: Clean up the cloned repository
echo "🧹 Cleaning up..."
rm -rf "$OPERATOR_DIR"
echo "   ✓ Removed: $OPERATOR_DIR"
echo ""

echo "================================================================================"
echo "✓ Successfully updated NIM Operator types from version $VERSION!"
echo "================================================================================"
echo ""
echo "Updated files:"
echo "  - src/models/nim_operator_types/nimservice.py"
echo "  - src/models/nim_operator_types/nimcache.py"
echo "  - src/models/nim_operator_types/__init__.py"
echo ""

