#!/bin/bash
set -euo pipefail

# Main function that fetches and calculates RC tags
fetch_rc_tags() {
  echo "Fetching latest RC tags for ${NGC_CLI_SERVICE}..."

  # Get the release version from branch name (e.g., release/25.01 -> 25.01)
  RELEASE_VERSION=$(echo $CI_COMMIT_REF_NAME | sed 's|^release/||')
  echo "Release version: ${RELEASE_VERSION}"

  # Fetch all tags from NGC for this image
  NGC_IMAGE_PATH="${NGC_REGISTRY}/${NGC_CLI_ORG}/${NGC_CLI_TEAM}/${NGC_CLI_SERVICE}"
  echo "Fetching tags from: ${NGC_IMAGE_PATH}"

  # Get all tags matching the release version pattern (e.g., 25.01-rc*)
  # NGC returns an array of objects with "tag" field: [{"tag": "...", ...}, ...]
  ALL_TAGS=$(ngc registry image list ${NGC_IMAGE_PATH} --format_type json 2>/dev/null | jq -r '.[].tag' || echo "")
  echo "All tags: ${ALL_TAGS}"

  if [ -z "$ALL_TAGS" ]; then
    echo "No tags found in NGC registry"
    # Initialize for first RC
    export NEXT_RC="${RELEASE_VERSION}-rc1"
  else
    # Filter tags matching the release version pattern with RC suffix
    # Pattern: YY.MM-rcN (e.g., 25.01-rc0, 25.12-rc15)
    RC_TAGS=$(echo "$ALL_TAGS" | grep -E "^${RELEASE_VERSION}-rc[0-9]+$" || true)
    
    if [ -z "$RC_TAGS" ]; then
      echo "No RC tags found for version ${RELEASE_VERSION}"
      # Initialize for first RC
      export NEXT_RC="${RELEASE_VERSION}-rc1"
    else
      echo "Found RC tags:"
      echo "$RC_TAGS"
      
      # Sort tags and get the latest one
      # Use version sort to handle multi-digit numbers correctly (e.g., rc10 > rc2)
      LATEST_RC=$(echo "$RC_TAGS" | sort -V | tail -n1)
      
      echo "Latest RC tag: ${LATEST_RC}"
      
      # Extract RC number from latest tag
      # Format: YY.MM-rcN (supports multi-digit values)
      RC_NUMBER=$(echo $LATEST_RC | sed -E 's/^.*-rc([0-9]+)$/\1/')
      
      echo "Current RC: ${RC_NUMBER}"
      
      # Increment RC number (handles double digits correctly)
      NEXT_RC_NUMBER=$((RC_NUMBER + 1))
      export NEXT_RC="${RELEASE_VERSION}-rc${NEXT_RC_NUMBER}"
    fi
  fi

  echo "NEXT_RC=${NEXT_RC}"
  echo "RC_TAG=${RELEASE_VERSION}-rc"

  # Write to dotenv file for downstream jobs
  echo "NEXT_RC=${NEXT_RC}" >> build.env
  echo "RC_TAG=${RELEASE_VERSION}-rc" >> build.env
}

# Only run if executed directly (not sourced for testing)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  fetch_rc_tags
fi
