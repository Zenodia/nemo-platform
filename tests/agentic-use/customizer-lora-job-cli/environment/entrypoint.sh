#!/bin/bash
set -e

echo '=== Checking Docker socket ==='
if [ -S /var/run/docker.sock ]; then
    echo 'Docker socket found at /var/run/docker.sock'
    export DOCKER_HOST=unix:///var/run/docker.sock
else
    echo 'WARNING: Docker socket not found - job execution will not work'
fi

# Point the customizer at our training image (gpu-finetune-test has torch + nmp training module)
export NMP_CUSTOMIZER_TRAINING_AUTOMODEL_IMAGE=gpu-finetune-test:latest

cd /app && /app/.venv/bin/nemo services run > /tmp/nmp-api.log 2>&1 &
API_PID=$!
echo "Started API server with PID: $API_PID"

CONSECUTIVE_SUCCESS=0
for i in {1..60}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        CONSECUTIVE_SUCCESS=$((CONSECUTIVE_SUCCESS+1))
        echo "Health check passed ($CONSECUTIVE_SUCCESS/3)"
        if [ "$CONSECUTIVE_SUCCESS" -ge 3 ]; then
            echo 'NeMo Platform API ready and stable'
            break
        fi
    else
        CONSECUTIVE_SUCCESS=0
    fi
    sleep 1
done

if [ "$CONSECUTIVE_SUCCESS" -lt 3 ]; then
    echo 'API failed to become stable!'
    cat /tmp/nmp-api.log
    kill $API_PID 2>/dev/null
    exit 1
fi

echo '=== Pre-configuring CLI auth ==='
/app/.venv/bin/nmp auth login --base-url http://localhost:8080 --unsigned-token --email agent@harbor.local --no-exp

bash /app/setup-env.sh

exec runuser -u harbor -- "$@"
