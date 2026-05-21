# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""SPA-aware static file serving for the Studio UI."""

import logging
import os
import re
from pathlib import Path

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

logger = logging.getLogger(__name__)

# Pattern to match any STUDIO_UI_* markers for cleanup
STUDIO_UI_MARKER_PATTERN = re.compile(r"STUDIO_UI_[A-Z_]+")


class SPAStaticFiles(StaticFiles):
    """
    Static files handler with SPA (Single Page Application) support.

    This handler serves static files from the Vite build output and implements
    SPA routing by falling back to index.html for routes that don't match
    existing files. This enables client-side routing to work correctly.

    Features:
    - Serves static assets (JS, CSS, images, etc.) directly
    - Falls back to index.html for non-file routes (SPA routing)
    - Handles .html extension stripping for clean URLs
    - Injects runtime environment variables from platform config (pre-processed once at startup)
    """

    def __init__(
        self,
        *args,
        env_replacements: dict[str, str] | None = None,
        **kwargs,
    ):
        """Initialize SPA static files handler.

        Args:
            env_replacements: Optional dict of STUDIO_UI_* markers to replacement values.
                              These will be applied to HTML and JS files once at startup.
        """
        super().__init__(*args, **kwargs)
        self._env_replacements = env_replacements or {}
        # Cache for pre-processed file contents (path -> processed content)
        self._processed_cache: dict[str, str] = {}
        # Pre-process files that need env var replacement
        self._preprocess_files()

    def _apply_env_replacements(self, content: str) -> str:
        """Replace STUDIO_UI_* markers with actual values.

        First replaces known markers from env_replacements dict,
        then clears any remaining STUDIO_UI_* markers with empty strings.

        Args:
            content: File content to process

        Returns:
            Content with all STUDIO_UI_* markers replaced
        """
        # Replace known markers with their configured values
        for marker, value in self._env_replacements.items():
            content = content.replace(marker, value)

        # Clear any remaining STUDIO_UI_* markers (replace with empty string)
        # This prevents unmapped markers from appearing as literal text
        content = STUDIO_UI_MARKER_PATTERN.sub("", content)

        return content

    def _preprocess_files(self) -> None:
        """Pre-process HTML and JS files with env var replacements.

        Called once at startup to cache processed file contents.
        Only processes files that may contain STUDIO_UI_* markers.
        """
        if not self._env_replacements:
            logger.debug("No env replacements configured, skipping preprocessing")
            return

        directory = Path(str(self.directory))
        if not directory.exists():
            logger.warning(f"Static files directory does not exist: {directory}")
            return

        processed_count = 0
        for pattern in ["**/*.html", "**/*.js"]:
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        # Only cache if there are markers to replace
                        if STUDIO_UI_MARKER_PATTERN.search(content):
                            processed_content = self._apply_env_replacements(content)
                            # Store with relative path as key
                            rel_path = str(file_path.relative_to(directory))
                            self._processed_cache[rel_path] = processed_content
                            processed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to preprocess {file_path}: {e}")

        logger.info(f"Pre-processed {processed_count} files with env replacements")

    async def get_response(self, path: str, scope: Scope) -> Response:
        """
        Override to implement SPA fallback routing and environment injection.

        1. Try to serve the requested file directly
        2. If not found and path doesn't have an extension, try adding .html
        3. If still not found, serve index.html for client-side routing
        4. For pre-processed files (HTML/JS with env vars), serve from cache
        """
        # Normalize path for cache lookup
        rel_path = path.lstrip("/")

        # Try the original path first
        try:
            response = await super().get_response(path, scope)
            if response.status_code != 404:
                # Check if this JS file was pre-processed
                if path.endswith(".js") and rel_path in self._processed_cache:
                    return Response(
                        content=self._processed_cache[rel_path],
                        media_type="application/javascript",
                    )
                # Check if this HTML file was pre-processed
                if path.endswith(".html") and rel_path in self._processed_cache:
                    return Response(
                        content=self._processed_cache[rel_path],
                        media_type="text/html",
                    )
                # Handle index.html when path is "." or "" (root directory request)
                # StaticFiles serves index.html for directory requests with path="."
                if rel_path in ("", ".", "/") and "index.html" in self._processed_cache:
                    return Response(
                        content=self._processed_cache["index.html"],
                        media_type="text/html",
                    )
                return response
        except Exception:
            pass

        # If original path failed and doesn't have a file extension
        if not self._has_file_extension(path):
            # Try adding .html extension
            html_path = rel_path.rstrip("/") + ".html"
            full_path = Path(str(self.directory)) / html_path

            if full_path.is_file():
                return self._serve_file(html_path, full_path, "text/html")

            # Fall back to index.html for SPA routing
            index_path = Path(str(self.directory)) / "index.html"
            if index_path.is_file():
                return self._serve_file("index.html", index_path, "text/html")

        # Return the original response (likely 404)
        return await super().get_response(path, scope)

    def _serve_file(self, rel_path: str, file_path: Path, media_type: str) -> Response:
        """Serve a file, using cached pre-processed content if available.

        Args:
            rel_path: Relative path for cache lookup
            file_path: Full path to the file
            media_type: MIME type for the response

        Returns:
            Response with file content (pre-processed if it was cached)
        """
        # Use pre-processed cache if available
        if rel_path in self._processed_cache:
            return Response(content=self._processed_cache[rel_path], media_type=media_type)

        # Otherwise read from disk (file has no markers to replace)
        content = file_path.read_text(encoding="utf-8")
        return Response(content=content, media_type=media_type)

    @staticmethod
    def _has_file_extension(path: str) -> bool:
        """Check if the path appears to have a file extension."""
        # Get the last component of the path
        basename = os.path.basename(path.rstrip("/"))
        # Check if it has a dot followed by characters (file extension)
        if "." in basename:
            parts = basename.rsplit(".", 1)
            # Make sure there's actually an extension (not just a hidden file)
            return len(parts) == 2 and len(parts[1]) > 0
        return False
