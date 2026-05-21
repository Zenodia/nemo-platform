// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const entriesPage1 = {
  object: 'list',
  data: [
    {
      id: 'entry-89Fe7ikidKAU6b3dxsL326',
      created_at: '2025-12-16T22:40:12.241917',
      updated_at: '2025-12-16T22:40:12.241918',
      external_id: null,
      data: {
        request: {
          messages: [
            {
              role: 'user',
              content:
                'You are an expert at creating high-quality tracker issues from minimal input.\n\nIf called via API, you will receive:\n- title: Issue title (may be vague)\n- description: Issue description (may be empty or just a Slack link)\n- project_id: Target project to create issue in\n- labels: Optional labels\n\nIf called via Slack, you will receive:\n- messages: List of messages from slack, converted to agent message format (OpenAI-style).\n  Each message has a role (user or assistant), content, and user_id.\n\nCreate a plan to enhance this issue:\n\n1. ANALYZE INPUT:\n   - Is description empty or just a link?\n   - Does title need expansion?\n   - Is there a Slack thread to fetch?\n\n2. GATHER CONTEXT:\n   - If Slack link present: fetch thread with get_slack_thread\n   - Summarize discussion with summarize_thread\n   - Extract technical requirements and code references\n\n3. BUILD COMPREHENSIVE DESCRIPTION:\n   - Clear problem statement or goal\n   - Technical details and requirements\n   - Code files/systems to modify (if mentioned)\n   - Suggested unit tests (if applicable)\n   - Acceptance criteria checklist\n\n4. CREATE PAYLOAD:\n   - Use create_issue_payload with enhanced description\n   - Return JSON for user review\n\nYour plan should be clear and account for missing information.\n',
            },
          ],
          model: 'meta/llama-3.3-70b-instruct',
        },
        response: {
          choices: [
            {
              index: 0,
              message: {
                role: 'assistant',
                content:
                  '**Enhanced Issue Creation Plan**\n=====================================\n\n### 1. ANALYZE INPUT\n\n* **Check description**: Verify if the description is empty or contains only a link.\n\t+ If empty or link-only, proceed to gather context from other sources.\n* **Assess title**: Evaluate if the title needs expansion or clarification.\n\t+ If unclear, attempt to extract relevant information from the description or Slack thread (if available).\n* **Identify Slack thread**: Determine if a Slack thread is associated with the issue.\n\t+ If a Slack thread is present, prepare to fetch and analyze the discussion.\n\n### 2. GATHER CONTEXT\n\n* **Fetch Slack thread**: Use `get_slack_thread` to retrieve the Slack thread associated with the issue (if applicable).\n* **Summarize discussion**: Apply `summarize_thread` to condense the Slack thread into a concise summary.\n* **Extract technical details**: Identify and extract technical requirements, code references, and other relevant information from the summary.\n\t+ Look for keywords like "bug," "feature," "fix," or specific technology mentions.\n\n### 3. BUILD COMPREHENSIVE DESCRIPTION\n\n* **Clear problem statement or goal**: Craft a concise problem statement or goal based on the gathered context.\n* **Technical details and requirements**: Include extracted technical details, such as:\n\t+ Code files or systems to modify\n\t+ Specific technologies or libraries involved\n\t+ Relevant configuration or setup information\n* **SS',
              },
              finish_reason: 'stop',
            },
          ],
          usage: {
            prompt_tokens: 89385,
            completion_tokens: 45750,
            total_tokens: 135135,
          },
        },
      },
      context: {
        app: 'unknown',
        task: '<workflow>',
        thread_id: null,
        user_id: null,
        trace_id: null,
        session_id: null,
        created_at: '2025-12-16T22:40:12.241855Z',
      },
      namespace: 'default',
      user_rating: null,
      events: [],
      schema_version: '1.0',
      description: null,
      project: null,
      custom_fields: {},
      ownership: null,
    },
    {
      id: 'entry-JM89hCVjj1w4dbJnMjJ4py',
      created_at: '2025-12-16T22:40:12.240606',
      updated_at: '2025-12-16T22:40:12.240607',
      external_id: null,
      data: {
        request: {
          messages: [
            {
              role: 'user',
              content:
                'You are an expert at creating high-quality tracker issues from minimal input.\n\nIf called via API, you will receive:\n- title: Issue title (may be vague)\n- description: Issue description (may be empty or just a Slack link)\n- project_id: Target project to create issue in\n- labels: Optional labels\n\nIf called via Slack, you will receive:\n- messages: List of messages from slack, converted to agent message format (OpenAI-style).\n  Each message has a role (user or assistant), content, and user_id.\n\nCreate a plan to enhance this issue:\n\n1. ANALYZE INPUT:\n   - Is description empty or just a link?\n   - Does title need expansion?\n   - Is there a Slack thread to fetch?\n\n2. GATHER CONTEXT:\n   - If Slack link present: fetch thread with get_slack_thread\n   - Summarize discussion with summarize_thread\n   - Extract technical requirements and code references\n\n3. BUILD COMPREHENSIVE DESCRIPTION:\n   - Clear problem statement or goal\n   - Technical details and requirements\n   - Code files/systems to modify (if mentioned)\n   - Suggested unit tests (if applicable)\n   - Acceptance criteria checklist\n\n4. CREATE PAYLOAD:\n   - Use create_issue_payload with enhanced description\n   - Return JSON for user review\n\nYour plan should be clear and account for missing information.\n',
            },
          ],
          model: 'meta/llama-3.3-70b-instruct',
        },
        response: {
          choices: [
            {
              index: 0,
              message: {
                role: 'assistant',
                content:
                  '**Enhancing Tracker Issues from Minimal Input**\n=====================================================\n\n### 1. Analyze Input\n\nTo create a high-quality tracker issue, we first need to analyze the input provided. This involves checking the following:\n\n* **Description**: Is the description empty or does it only contain a Slack link? If so, we need to fetch the Slack thread to gather more context.\n* **Title**: Does the title need expansion? If the title is vague, we may need to modify it based on the information gathered from the Slack thread or description.\n* **Slack Thread**: Is there a Slack thread to fetch? If a Slack link is present, we need to retrieve the thread to gather more context.\n\n### 2. Gather Context\n\nTo gather context, we will perform the following steps:\n\n* **Fetch Slack Thread**: If a Slack link is present, use the `get_slack_thread` function to retrieve the thread.\n* **Summarize Discussion**: Use the `summarize_thread` function to summarize the discussion in the Slack thread.\n* **Extract Technical Requirements**: Extract technical requirements and code references from the Slack thread or description.\n\n### 3. Build Comprehensive Description\n\nUsing the gathered context, we will build a comprehensive description for the tracker issue. This description should include:\n\n* **Clear Problem Statement or Goal**: A clear statement of the problem or goal.\n* **Technical Details and Requirements**: Technical details and requirements extracted from the Slack thread or description.\n* ** **',
              },
              finish_reason: 'stop',
            },
          ],
          usage: {
            prompt_tokens: 89385,
            completion_tokens: 45750,
            total_tokens: 135135,
          },
        },
      },
      context: {
        app: 'unknown',
        task: '<workflow>',
        thread_id: null,
        user_id: null,
        trace_id: null,
        session_id: null,
        created_at: '2025-12-16T22:40:12.240534Z',
      },
      namespace: 'default',
      user_rating: null,
      events: [],
      schema_version: '1.0',
      description: null,
      project: null,
      custom_fields: {},
      ownership: null,
    },
  ],
  pagination: {
    page: 1,
    page_size: 10,
    current_page_size: 2,
    total_pages: 1,
    total_results: 2,
  },
  sort: '-created_at',
};
