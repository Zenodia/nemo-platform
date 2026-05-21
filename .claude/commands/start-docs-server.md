---
allowed-tools: Bash(cd docs && make live:*)
description: Start a live documentation server with auto-reload
---
Start a live documentation server for development with full SDK documentation.

Run:
```bash
cd docs && make live
```

The server will be available at `http://localhost:8000` after the initial build completes.
It will automatically rebuild when you change documentation files.

