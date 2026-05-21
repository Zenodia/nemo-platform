#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE nemo_db;
    CREATE DATABASE nemo_test_db;
EOSQL