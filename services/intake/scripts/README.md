# Intake Scripts

This directory contains utility scripts for the Intake service.

## seed-entries.py

A script to seed the database with test entry records. Supports two modes:

### API Mode (Default)

Makes HTTP requests to the Intake service API. This is the recommended approach as it ensures tasks and clients are properly created through the server's business logic.

**Usage:**
```bash
# Use default localhost endpoint
python -m scripts.seed-entries

# Use custom API endpoint
python -m scripts.seed-entries --api-url https://your-api-endpoint.com/v1/intake/entries

# Custom count and timeout
python -m scripts.seed-entries --count 25 --timeout 60

# Verbose logging
python -m scripts.seed-entries --verbose
```

### Database Mode

Directly inserts records into the database, bypassing API server logic. This mode is legacy and not recommended as it doesn't create tasks and clients properly.

**Prerequisites:**
- `cd` into `services/intake`
- Intake is running in a container via `docker-compose -f docker-compose.test.yaml up --build`

**Usage:**
```bash
# Run inside the container
docker exec -it nemo-intake python -m scripts.seed-entries --mode database

# Or with custom count
docker exec -it nemo-intake python -m scripts.seed-entries --mode database --count 100
```

### Command Line Options

- `--mode`: Choose between `api` (default) or `database`
- `--api-url`: API endpoint URL (default: `http://localhost:8000/v1/intake/entries`)
- `--count`: Number of entries to create (default: 50)
- `--timeout`: HTTP timeout in seconds for API mode (default: 30)
- `--verbose`: Enable verbose logging

### Examples

```bash
# API mode with default localhost endpoint (recommended)
python -m scripts.seed-entries

# API mode with 100 entries
python -m scripts.seed-entries --count 100

# API mode with custom endpoint and verbose logging
python -m scripts.seed-entries --api-url https://staging.example.com/v1/intake/entries --count 25 --verbose

# Database mode (legacy)
docker exec -it nemo-intake python -m scripts.seed-entries --mode database --count 100
``` 