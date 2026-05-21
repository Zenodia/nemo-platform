# Agent Spec: <name>

Date: <YYYY-MM-DD>
Author: <user>

## Job

One sentence describing what the agent does. Concrete, not aspirational.

## Audience

Who talks to it. Internal employees, external customers, developers, etc.
Affects tone and what is safe to say.

## Categories

Buckets of questions or tasks the agent handles. Aim for 3 to 6.

- <category 1>
- <category 2>
- <category 3>

## Tools

Tools the agent calls beyond the model itself. Default: `current_datetime`.

| Tool | Purpose | Credentials needed |
|---|---|---|
| current_datetime | clock for time-sensitive answers | none |

If no tools beyond clock, write: "Prompt-only. No tools."

## Model

Inference target. Cloud (NVIDIA Build API) or local NIM. Specific model id.

- Mode: <cloud | host-gpu | byoe>
- Model: <model id, e.g., nvidia-llama-3-3-nemotron-super-49b-v1>

## Framework

The agent will be wrapped in NVIDIA Agent Toolkit (NAT) as a LangGraph workflow.
If the source agent is not LangGraph (CrewAI, AutoGen, plain LangChain,
Pydantic AI), note the wrapper work needed here.

## Constraints

Negative requirements. Things the agent must not do or say.

- <constraint>

## Success criteria

How we know it works. Two or three concrete check questions and the kind
of answer that counts as a pass.

1. Question: <question text>
   Pass criteria: <what a good answer looks like>

2. Question: <question text>
   Pass criteria: <what a good answer looks like>

## Open questions

Anything the user could not answer yet. These are the items `nemo-build-agent`
will ask before scaffolding.

- <open question>
