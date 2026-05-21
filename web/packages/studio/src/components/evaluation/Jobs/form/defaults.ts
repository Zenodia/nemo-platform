// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const DEFAULT_SYSTEM_PROMPT = `You are evaluating the HELPFULNESS of an AI assistant's response.

Helpfulness measures the overall utility of the response in addressing the user's needs. Rate on a 0-4 integer scale:

0 - The response fails to address the user's request, provides irrelevant information, or could cause harm.
1 - The response partially addresses the request but has significant gaps, errors, or misunderstandings.
2 - The response addresses the core request adequately but may lack detail, clarity, or completeness.
3 - The response fully addresses the request with appropriate detail and is genuinely useful.
4 - The response excellently addresses the request, providing comprehensive and well-structured information that fully satisfies the user's needs.

Focus on whether the response helps the user accomplish their goal, not on style or verbosity.

A shorter response that directly solves the problem can score higher than a longer one that misses the point.`;

export const DEFAULT_PROMPT_TEMPLATE = `User prompt: {{input}}
Assistant response: {{output}}

Rate this response.`;

export const DEFAULT_TEST_DATASET = `{
  "input": "How do I merge two sorted arrays in Python without extra space?",
  "output": "Use two pointers starting at the end of both arrays and fill from the back of the larger buffer, comparing values so you overwrite safely in O(n) time."
},
{
  "input": "Quick dinner idea with chicken, rice, and whatever is in a normal pantry?",
  "output": "Try one-pan chicken thighs: brown the chicken, add rice, broth, and frozen peas, cover and simmer until the rice is tender."
},
{
  "input": "My manager takes credit for my work in meetings. What should I do first?",
  "output": "Document your contributions in writing, then request a short 1:1 to clarify expectations for how work is credited in group settings."
},
{
  "input": "Is this headache something serious? It came on suddenly and my vision is blurry.",
  "output": "Sudden headache with vision changes can be urgent. Please seek in-person medical care or emergency services now rather than waiting."
},
{
  "input": "Explain why gradient descent can overshoot if the learning rate is too high.",
  "output": "Each step moves proportional to the gradient; if the rate is large, updates can jump past the minimum and oscillate or diverge instead of converging."
},
{
  "input": "Write a two-sentence product blurb for noise-canceling earbuds aimed at commuters.",
  "output": "Block train rumble and café chatter so your playlist stays front and center. Lightweight fit and all-day battery for door-to-desk listening."
},
{
  "input": "Customer says our shipment arrived damaged and they want a refund today.",
  "output": "I'm sorry that happened. I can start a replacement or refund—may I have your order number and a photo of the packaging and damaged items?"
},
{
  "input": "Summarize the tone: formal, casual, or mixed? Input: 'Per the memo dated 4/1, pls send the deck by EOD. Thx!'",
  "output": "Mixed: the opening is formal office language, while the close uses casual abbreviations and shorthand."
}`;
