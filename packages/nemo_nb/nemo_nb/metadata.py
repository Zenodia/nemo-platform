# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Cell metadata parsing and validation.

Supports:
- Hide cell via metadata.nemo_nb.hide or tags
- Language detection for syntax highlighting

Note: Most features now use marker-based commands instead of metadata.
See markers.py for marker-based command parsing.
"""

from typing import Dict


class CellMetadata:
    """Parse and validate cell metadata.

    Minimal metadata support - most features use markers now.
    """

    def __init__(self, cell: Dict):
        self.cell = cell
        self.metadata = cell.get("metadata", {})
        self.nemo_config = self.metadata.get("nemo_nb", {})
        self.tags = self.metadata.get("tags", [])

    def should_hide(self) -> bool:
        """Check if cell should be hidden.

        Supports:
        - metadata.nemo_nb.hide = true
        - metadata.tags includes "hide-cell"

        Returns:
            True if cell should be omitted from output
        """
        return self.nemo_config.get("hide", False) or "hide-cell" in self.tags

    def get_language(self) -> str:
        """Get code cell language for syntax highlighting.

        Default: python

        Supports:
        - metadata.language: Direct language specification
        - metadata.vscode.languageId: VSCode language identifier
        - Converts "shellscript" and "bash" to "sh" for proper rendering

        Returns:
            Language identifier for code fence (e.g., "python", "sh")
        """
        # Check for direct language specification
        if lang := self.metadata.get("language"):
            # Normalize bash to sh
            if lang == "bash":
                return "sh"
            return lang

        # Check for VSCode language identifier
        vscode_meta = self.metadata.get("vscode", {})
        if lang_id := vscode_meta.get("languageId"):
            # Convert VSCode language IDs to standard code fence languages
            if lang_id == "shellscript":
                return "sh"
            return lang_id

        # Default to Python
        return "python"
