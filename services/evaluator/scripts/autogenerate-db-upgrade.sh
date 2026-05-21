#!/bin/sh

while getopts 'm:' opt; do
  case "$opt" in
    m)
      arg="${OPTARG}"
      UPGRADE=$arg docker compose -f docker-compose-db-migration.yaml up --build --abort-on-container-exit
      ;;
  esac
done
