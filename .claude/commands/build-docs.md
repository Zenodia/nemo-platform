---
description: Build documentation with various options
---
Build the documentation using one of these modes:

1. **Fast build** (default) - Quick iteration, skips SDK docs:
   ```bash
   cd docs && make html-fast
   ```

2. **Full build** - Complete build including SDK docs:
   ```bash
   cd docs && make html
   ```

Ask the user which mode they prefer, then run the appropriate command.
After building, let them know they can view the docs at `docs/_build/html/index.html`.

