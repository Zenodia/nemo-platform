# Legacy Evaluator Service

This directory contains legacy NeMo Evaluator service code.

Evaluator functionality is in the process of migrating to the first-party
Evaluator plugin in `plugins/nemo-evaluator` and the shared Evaluator SDK in
`packages/nemo_evaluator_sdk`. New Evaluator work should target those packages
unless it is specifically maintaining compatibility for this legacy service.
