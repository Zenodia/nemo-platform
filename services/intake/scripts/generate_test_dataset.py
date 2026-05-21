#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate comprehensive test dataset for Intake API.

This script creates a realistic dataset of ~100 entry records across multiple
scenarios to test and demonstrate the Intake system capabilities.

Dataset Overview:
- Single-turn entries across multiple tasks and timeframes
- Multi-turn conversations (threads) with various event types
- User feedback events (thumbs up/down, ratings, opinions)
- User action events (sharing, copying, etc.)
- Events targeting different message parts (responses, assistant messages)

The generated data demonstrates realistic AI interaction patterns and provides
comprehensive test coverage for the export and search functionality.
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

# ---------------------------------------------------------------------------
# Configuration and Utilities
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE = "default"

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[3] / ".tmp" / "intake" / "test_data"


class Conversation(TypedDict):
    """Multi-turn conversation fixture: one app/task with a sequence of (prompt, response) turns."""

    app_id: str
    task_id: str
    turns: List[Tuple[str, str]]


class Scenario(TypedDict):
    """Single-turn scenario fixture with attached events (feedback or actions)."""

    prompt: str
    response: str
    events: List[Dict[str, Any]]


# Task definitions for realistic scenarios
TASKS = {
    "customer-support": "AI-powered customer service chat assistant",
    "code-generation": "Software development code entry and generation",
    "content-writing": "Marketing content and blog post generation",
    "data-analysis": "Business intelligence and data insights generation",
    "legal-research": "Legal document analysis and research assistance",
    "medical-qa": "Medical information and diagnostic assistance",
    "education": "Educational content and tutoring assistance",
    "translation": "Multi-language translation and localization",
}

CLIENT_IDS = ["acme-corp", "globodyne", "initech", "hooli", "pied-piper"]


def generate_entry_id() -> str:
    """Generate realistic entry ID."""
    return f"comp_{uuid.uuid4().hex[:12]}"


def generate_thread_id() -> str:
    """Generate realistic thread ID."""
    return f"thread_{uuid.uuid4().hex[:8]}"


@dataclass
class EntryDraft:
    """In-memory representation of a v2 EntryInput payload."""

    workspace: str
    external_id: str
    model: str
    messages: List[Dict[str, Any]]
    response_text: str
    usage: Dict[str, Any]
    app_id: str
    task_id: str
    thread_id: Optional[str] = None
    events: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to the JSON shape accepted by POST /entries."""
        entry: Dict[str, Any] = {
            "external_id": self.external_id,
            "data": {
                "request": {"model": self.model, "messages": self.messages},
                "response": {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": self.response_text},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": self.usage,
                },
            },
            "context": {
                "app": f"{self.workspace}/{self.app_id}",
                "task": self.task_id,
                "thread_id": self.thread_id,
            },
        }
        if self.events:
            entry["events"] = self.events
        return entry


# ---------------------------------------------------------------------------
# Single-Turn Entry Generators
# ---------------------------------------------------------------------------


def create_single_turn_entries(workspace: str) -> List[Dict[str, Any]]:
    """
    Create 40 single-turn entries across multiple tasks and clients.

    These represent standalone AI interactions without follow-up conversations.
    Each entry has:
    - Random app_id and task_id
    - Realistic prompts and responses for the task type
    - Timestamps spread across the last 30 days
    - No events (pure entry data)

    Returns list of entry payloads ready for POST /entries
    """
    entries = []

    # Templates for different task types
    scenarios = [
        (
            "customer-support",
            "How do I reset my password?",
            "I can help you reset your password. Please visit the account settings page and click 'Forgot Password'. You'll receive a reset link via email within 5 minutes.",
        ),
        (
            "customer-support",
            "My order hasn't arrived yet, can you help?",
            "Let me check on your order status. I see it was shipped yesterday and should arrive within 2-3 business days. Here's your tracking number: ABC123456789.",
        ),
        (
            "customer-support",
            "I'm having trouble with the mobile app",
            "I understand the app issues you're experiencing. Try clearing the cache and data, then restart the app. If the problem persists, please update to the latest version.",
        ),
        (
            "code-generation",
            "Write a Python function to validate email addresses",
            "```python\nimport re\n\ndef validate_email(email):\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None\n```",
        ),
        (
            "code-generation",
            "Create a REST API endpoint for user authentication",
            "```python\nfrom flask import Flask, request, jsonify\nfrom werkzeug.security import check_password_hash\n\n@app.route('/auth', methods=['POST'])\ndef authenticate():\n    data = request.get_json()\n    # Authentication logic here\n    return jsonify({'token': 'jwt_token_here'})\n```",
        ),
        (
            "content-writing",
            "Write a blog post about sustainable living",
            "# Sustainable Living: Small Changes, Big Impact\n\nIn today's world, making environmentally conscious choices has never been more important. Here are 10 simple ways to reduce your carbon footprint and contribute to a healthier planet...",
        ),
        (
            "content-writing",
            "Create social media copy for a new product launch",
            "🚀 Introducing our revolutionary new product! Experience the future of innovation with cutting-edge technology that transforms how you work and play. #Innovation #TechLaunch #GameChanger",
        ),
        (
            "data-analysis",
            "Analyze customer churn patterns in our dataset",
            "Based on the analysis, customer churn is highest in months 3-6 after signup (28% churn rate). Key factors include lack of feature usage (45% correlation) and poor onboarding entry (62% of churned users didn't complete setup).",
        ),
        (
            "data-analysis",
            "Create a dashboard showing sales performance metrics",
            "The sales dashboard reveals a 15% increase in Q3 performance with strongest growth in the enterprise segment (34% YoY). Regional breakdown shows North America leading at $2.3M, followed by Europe at $1.8M.",
        ),
        (
            "legal-research",
            "Research trademark infringement laws",
            "Trademark infringement occurs when a party uses a mark that is identical or confusingly similar to a registered trademark. Key factors include: likelihood of confusion, strength of the mark, and similarity of goods/services.",
        ),
        (
            "medical-qa",
            "Explain the symptoms of diabetes",
            "Common diabetes symptoms include frequent urination, excessive thirst, unexplained weight loss, fatigue, and blurred vision. If you experience these symptoms, consult a healthcare provider for proper evaluation and testing.",
        ),
        (
            "education",
            "Explain photosynthesis to a middle school student",
            "Photosynthesis is like a plant's way of making food using sunlight! Plants take in carbon dioxide from the air, water from their roots, and use sunlight energy to create glucose (sugar) and release oxygen.",
        ),
        (
            "translation",
            "Translate 'Hello, how are you?' to Spanish",
            "The translation of 'Hello, how are you?' to Spanish is: 'Hola, ¿cómo estás?' (informal) or 'Hola, ¿cómo está usted?' (formal).",
        ),
    ]

    for i in range(40):
        app_id = random.choice(CLIENT_IDS)
        task_key = random.choice(list(TASKS.keys()))

        # Pick a scenario that matches this task or use a generic one
        matching_scenarios = [s for s in scenarios if s[0] == task_key]
        if matching_scenarios:
            _, prompt, response = random.choice(matching_scenarios)
        else:
            prompt = f"Generic prompt for {task_key} task"
            response = f"Generic response for {task_key}"

        prompt_tokens = random.randint(20, 100)
        completion_tokens = random.randint(50, 200)
        entries.append(
            EntryDraft(
                workspace=workspace,
                external_id=generate_entry_id(),
                model="llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                response_text=response,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                app_id=app_id,
                task_id=task_key,
                thread_id=None,
            ).to_dict()
        )

    return entries


def create_conversation_threads(workspace: str) -> List[Dict[str, Any]]:
    """
    Create multi-turn conversation threads with realistic back-and-forth.

    These represent ongoing conversations where users have follow-up questions.
    Each thread contains:
    - 3-4 turns of conversation
    - Realistic conversation flow for the task type
    - Events targeting different parts of the conversation
    - Consistent thread_id across all turns

    Returns list of entry payloads ready for POST /entries
    """
    entries = []

    # Conversation scenarios
    conversations: List[Conversation] = [
        {
            "app_id": "acme-corp",
            "task_id": "customer-support",
            "turns": [
                (
                    "I'm having trouble logging into my account",
                    "I can help you with that login issue. Can you tell me what error message you're seeing?",
                ),
                (
                    "It says 'invalid credentials' but I'm sure my password is correct",
                    "That error usually means either the email or password is incorrect. Let's try resetting your password to be sure. I'll send you a reset link.",
                ),
                (
                    "I got the email and reset it, but it's still not working",
                    "I see the issue now - your account was temporarily locked due to multiple failed attempts. I've unlocked it for you. Please try logging in again with your new password.",
                ),
            ],
        },
        {
            "app_id": "hooli",
            "task_id": "code-generation",
            "turns": [
                (
                    "I need to create a user registration API endpoint",
                    "I'll help you create a user registration endpoint. Here's a basic structure:\n\n```python\nfrom flask import Flask, request, jsonify\nfrom werkzeug.security import generate_password_hash\n\n@app.route('/register', methods=['POST'])\ndef register():\n    data = request.get_json()\n    email = data.get('email')\n    password = data.get('password')\n    \n    # Hash password and save user\n    hashed_password = generate_password_hash(password)\n    # Save to database...\n    \n    return jsonify({'message': 'User created successfully'}), 201\n```",
                ),
                (
                    "This looks good, but I also need email validation and duplicate checking",
                    "Great point! Let me enhance that with proper validation:\n\n```python\nimport re\nfrom sqlalchemy.exc import IntegrityError\n\ndef validate_email(email):\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None\n\n@app.route('/register', methods=['POST'])\ndef register():\n    data = request.get_json()\n    email = data.get('email')\n    password = data.get('password')\n    \n    # Validate input\n    if not email or not password:\n        return jsonify({'error': 'Email and password required'}), 400\n    \n    if not validate_email(email):\n        return jsonify({'error': 'Invalid email format'}), 400\n    \n    # Check for existing user\n    existing_user = User.query.filter_by(email=email).first()\n    if existing_user:\n        return jsonify({'error': 'User already exists'}), 409\n        \n    # Create user...\n```",
                ),
                (
                    "Perfect! Can you also add password strength validation?",
                    "Absolutely! Here's a password strength validator:\n\n```python\ndef validate_password_strength(password):\n    if len(password) < 8:\n        return False, 'Password must be at least 8 characters long'\n    if not re.search(r'[A-Z]', password):\n        return False, 'Password must contain at least one uppercase letter'\n    if not re.search(r'[a-z]', password):\n        return False, 'Password must contain at least one lowercase letter'\n    if not re.search(r'\\d', password):\n        return False, 'Password must contain at least one number'\n    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):\n        return False, 'Password must contain at least one special character'\n    return True, 'Password is strong'\n\n# Add this validation before creating the user:\nis_strong, message = validate_password_strength(password)\nif not is_strong:\n    return jsonify({'error': message}), 400\n```",
                ),
            ],
        },
        {
            "app_id": "globodyne",
            "task_id": "data-analysis",
            "turns": [
                (
                    "Can you help me analyze our sales data trends?",
                    "I'd be happy to help analyze your sales data! What specific aspects would you like to focus on? For example: monthly trends, regional performance, product categories, or seasonal patterns?",
                ),
                (
                    "I want to understand why our Q2 sales dropped compared to Q1",
                    "Let's investigate the Q2 sales decline. I'll need to examine several factors:\n\n1. **Monthly breakdown**: Compare April, May, June individually\n2. **Product performance**: Which products/categories were most affected\n3. **Regional analysis**: Geographic impact patterns\n4. **External factors**: Market conditions, competition, seasonality\n\nCan you share your sales data or tell me what data sources you have available?",
                ),
                (
                    "We have sales by month, product category, and region. Q1 was $2.4M, Q2 was $1.8M",
                    "That's a significant 25% decline from Q1 to Q2 ($600k drop). Here's my analysis approach:\n\n**Key Questions:**\n- Which product categories drove the decline?\n- Was the drop consistent across all regions?\n- Did it happen gradually or sudden in a specific month?\n\n**Recommended Analysis:**\n1. Break down the $600k loss by category and region\n2. Compare month-over-month trends within Q2\n3. Look for external factors (market conditions, competitor launches)\n4. Check if this aligns with historical seasonal patterns\n\nThis will help identify if it's a temporary market condition or a deeper business issue requiring strategic changes.",
                ),
            ],
        },
        {
            "app_id": "initech",
            "task_id": "content-writing",
            "turns": [
                (
                    "I need help writing a press release for our new product launch",
                    "I'd be happy to help you write a compelling press release! To create the most effective announcement, I'll need some key details:\n\n1. **Product name and category**\n2. **Key features and benefits**\n3. **Target audience**\n4. **Launch date and availability**\n5. **Company background**\n6. **Any notable partnerships or achievements**\n\nWhat's the product you're launching?",
                ),
                (
                    "It's a new project management software called 'TaskFlow' that uses AI to optimize team workflows",
                    "Excellent! TaskFlow sounds innovative. Here's a draft press release structure:\n\n**FOR IMMEDIATE RELEASE**\n\n**Initech Launches TaskFlow: AI-Powered Project Management Platform Revolutionizes Team Productivity**\n\n*Revolutionary software leverages artificial intelligence to optimize workflows and boost team efficiency*\n\n[City, Date] – Initech today announced the launch of TaskFlow, a cutting-edge project management platform that harnesses the power of artificial intelligence to optimize team workflows and dramatically improve productivity.\n\nWould you like me to continue with specific features and benefits? What are TaskFlow's main AI capabilities?",
                ),
                (
                    "The AI can predict project bottlenecks, automatically assign tasks based on team skills, and suggest optimal deadlines",
                    'Perfect! Here\'s the complete press release:\n\n**FOR IMMEDIATE RELEASE**\n\n**Initech Launches TaskFlow: AI-Powered Project Management Platform Revolutionizes Team Productivity**\n\n*Revolutionary software leverages artificial intelligence to optimize workflows and boost team efficiency by up to 40%*\n\n[City, Date] – Initech today announced the launch of TaskFlow, a cutting-edge project management platform that harnesses artificial intelligence to transform how teams collaborate and execute projects.\n\n**Key Features:**\n• **Predictive Analytics**: AI algorithms identify potential bottlenecks before they impact deadlines\n• **Smart Task Assignment**: Automatically matches tasks to team members based on skills, availability, and task\n• **Optimized Scheduling**: Suggests realistic deadlines using historical data and team capacity\n\n"TaskFlow represents the future of project management," said [Spokesperson Name], [Title] at Initech. "Our AI doesn\'t just track progress – it actively optimizes your team\'s workflow to ensure projects succeed."\n\nTaskFlow is available immediately with pricing starting at $X per user per month. For more information, visit [website] or contact [email].\n\n**About Initech**\n[Company description]\n\n###',
                ),
            ],
        },
    ]

    # Generate entries for each conversation
    for conv in conversations:
        thread_id = generate_thread_id()

        for turn_idx, (prompt, response) in enumerate(conv["turns"]):
            # Build message history (all previous turns)
            messages = []
            for prev_idx in range(turn_idx):
                prev_prompt, prev_response = conv["turns"][prev_idx]
                messages.extend(
                    [
                        {"role": "user", "content": prev_prompt},
                        {"role": "assistant", "content": prev_response},
                    ]
                )

            # Add current user message
            messages.append({"role": "user", "content": prompt})

            # Create events for some turns
            events = []

            # Add thumbs up on the first response of each thread
            if turn_idx == 0:
                events.append({"event_type": "user_feedback", "thumb": "up"})

            # Add copy action on code responses
            if "```" in response and turn_idx == 1:
                events.append({"event_type": "user_action", "action": "copy_clicked", "metadata": {"code_block": True}})

            # Add rating on final turn
            if turn_idx == len(conv["turns"]) - 1:
                events.append({"event_type": "user_feedback", "rating": 5})

            entries.append(
                EntryDraft(
                    workspace=workspace,
                    external_id=generate_entry_id(),
                    model="llama-3.1-70b-instruct",
                    messages=messages,
                    response_text=response,
                    usage={
                        "prompt_tokens": 200 + turn_idx * 50,
                        "completion_tokens": 300 + turn_idx * 100,
                        "total_tokens": 500 + turn_idx * 150,
                    },
                    app_id=conv["app_id"],
                    task_id=conv["task_id"],
                    thread_id=thread_id,
                    events=events or None,
                ).to_dict()
            )

    return entries


def create_feedback_heavy_entries(workspace: str) -> List[Dict[str, Any]]:
    """
    Create 30 entries with heavy user feedback events.

    These demonstrate various types of user feedback:
    - Thumbs up/down with reasons
    - 1-5 star ratings
    - Written opinions and comments
    - Multiple events per entry

    Returns list of entry payloads ready for POST /entries
    """
    entries = []

    feedback_scenarios: List[Scenario] = [
        {
            "prompt": "Explain quantum computing in simple terms",
            "response": "Quantum computing is like having a super-powered computer that can explore many solutions to a problem simultaneously, rather than checking them one by one like regular computers. Think of it as the difference between reading every book in a library one at a time versus somehow reading them all at once!",
            "events": [
                {"event_type": "user_feedback", "thumb": "up"},
                {"event_type": "user_feedback", "rating": 4},
                {
                    "event_type": "user_feedback",
                    "opinion": "Great analogy! Really helped me understand the concept.",
                },
            ],
        },
        {
            "prompt": "Write a Python function to reverse a string",
            "response": "```python\ndef reverse_string(s):\n    return s[::-1]\n```",
            "events": [
                {"event_type": "user_feedback", "thumb": "down"},
                {
                    "event_type": "user_feedback",
                    "opinion": "This works but could you explain how slicing works?",
                },
            ],
        },
        {
            "prompt": "What are the benefits of renewable energy?",
            "response": "Renewable energy offers numerous benefits: 1) Environmental - reduces greenhouse gas emissions and air pollution, 2) Economic - creates jobs and reduces energy costs long-term, 3) Energy security - reduces dependence on fossil fuel imports, 4) Sustainability - inexhaustible energy sources, 5) Health - cleaner air leads to better public health outcomes.",
            "events": [
                {"event_type": "user_feedback", "thumb": "up"},
                {"event_type": "user_feedback", "rating": 5},
                {"event_type": "user_action", "action": "share_clicked", "metadata": {"share_platform": "twitter"}},
            ],
        },
    ]

    # Add the specific feedback scenarios
    for scenario in feedback_scenarios:
        app_id = random.choice(CLIENT_IDS)
        task_id = random.choice(list(TASKS.keys()))

        entries.append(
            EntryDraft(
                workspace=workspace,
                external_id=generate_entry_id(),
                model="llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": scenario["prompt"]}],
                response_text=scenario["response"],
                usage={"prompt_tokens": 25, "completion_tokens": 75, "total_tokens": 100},
                app_id=app_id,
                task_id=task_id,
                thread_id=None,
                events=scenario["events"],
            ).to_dict()
        )

    # Generate additional random feedback entries
    for i in range(27):  # 27 more for total of 30
        app_id = random.choice(CLIENT_IDS)
        task_id = random.choice(list(TASKS.keys()))

        events = []

        # Random feedback patterns
        if random.random() < 0.7:  # 70% get thumbs
            thumb = "up" if random.random() < 0.8 else "down"  # 80% positive
            events.append({"event_type": "user_feedback", "thumb": thumb})

        if random.random() < 0.3:  # 30% get ratings
            rating = random.randint(1, 5)
            events.append({"event_type": "user_feedback", "rating": rating})

        if random.random() < 0.2:  # 20% get opinions
            opinions = [
                "Very helpful response!",
                "Could be more detailed",
                "Perfect explanation",
                "Not quite what I was looking for",
                "This solved my problem exactly",
                "Good information but needs examples",
                "Clear and concise, thanks!",
                "Could use more context",
            ]
            events.append(
                {
                    "event_type": "user_feedback",
                    "opinion": random.choice(opinions),
                }
            )

        prompt = f"Sample question about {task_id}"
        entries.append(
            EntryDraft(
                workspace=workspace,
                external_id=generate_entry_id(),
                model="llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                response_text=f"Sample response for {task_id} with feedback potential",
                usage={"prompt_tokens": 20, "completion_tokens": 50, "total_tokens": 70},
                app_id=app_id,
                task_id=task_id,
                thread_id=None,
                events=events or None,
            ).to_dict()
        )

    return entries


def create_action_heavy_entries(workspace: str) -> List[Dict[str, Any]]:
    """
    Create 20 entries with user action events.

    These demonstrate user interactions beyond feedback:
    - Copy button clicks
    - Share actions
    - Link clicks
    - Export actions

    Returns list of entry payloads ready for POST /entries
    """
    entries = []

    action_scenarios: List[Scenario] = [
        {
            "prompt": "Generate a SQL query to find active users",
            "response": "```sql\nSELECT user_id, email, last_login\nFROM users \nWHERE last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY)\nAND status = 'active'\nORDER BY last_login DESC;\n```",
            "events": [
                {"event_type": "user_action", "action": "copy_clicked", "metadata": {"copied_content": "sql_query"}},
                {
                    "event_type": "user_action",
                    "action": "share_clicked",
                    "metadata": {"share_platform": "slack", "team_share": True},
                },
            ],
        },
        {
            "prompt": "Show me how to deploy a React app to production",
            "response": "Here's a step-by-step guide to deploy your React app:\n\n1. Build the production version:\n```bash\nnpm run build\n```\n\n2. Choose a hosting platform (Netlify, Vercel, or AWS S3)\n\n3. For Netlify:\n- Connect your GitHub repo\n- Set build command: `npm run build`\n- Set publish directory: `build`\n\n4. Configure environment variables if needed\n\nYour app will be live with automatic SSL and CDN!",
            "events": [
                {"event_type": "user_action", "action": "copy_clicked", "metadata": {"copied_content": "bash_command"}},
                {"event_type": "user_action", "action": "link_clicked", "metadata": {"external_link": "netlify.com"}},
            ],
        },
    ]

    # Add specific action scenarios
    for scenario in action_scenarios:
        app_id = random.choice(CLIENT_IDS)
        task_id = "code-generation"  # These are code-related

        entries.append(
            EntryDraft(
                workspace=workspace,
                external_id=generate_entry_id(),
                model="llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": scenario["prompt"]}],
                response_text=scenario["response"],
                usage={"prompt_tokens": 30, "completion_tokens": 120, "total_tokens": 150},
                app_id=app_id,
                task_id=task_id,
                thread_id=None,
                events=scenario["events"],
            ).to_dict()
        )

    # Generate more random action entries
    for i in range(18):  # 18 more for total of 20
        app_id = random.choice(CLIENT_IDS)
        task_id = random.choice(list(TASKS.keys()))

        # Random action events
        events = []
        action_types = ["copy_clicked", "share_clicked", "link_clicked", "export_clicked", "bookmark_clicked"]

        if random.random() < 0.8:  # 80% get at least one action
            action = random.choice(action_types)
            events.append({"event_type": "user_action", "action": action, "metadata": {"action_context": task_id}})

        if random.random() < 0.3:  # 30% get second action
            action = random.choice(action_types)
            events.append({"event_type": "user_action", "action": action, "metadata": {"secondary_action": True}})

        prompt = f"Sample prompt for {task_id} task"
        entries.append(
            EntryDraft(
                workspace=workspace,
                external_id=generate_entry_id(),
                model="llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                response_text=f"Response with actionable content for {task_id}",
                usage={"prompt_tokens": 30, "completion_tokens": 80, "total_tokens": 110},
                app_id=app_id,
                task_id=task_id,
                thread_id=None,
                events=events or None,
            ).to_dict()
        )

    return entries


# ---------------------------------------------------------------------------
# Main Generation Function
# ---------------------------------------------------------------------------


def generate_complete_dataset(workspace: str = DEFAULT_WORKSPACE) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate the complete test dataset with all scenarios.

    Returns:
        Dictionary with categorized entry data:
        - single_turns: 40 standalone entries
        - conversations: ~12 multi-turn conversation entries
        - feedback_heavy: 30 entries with user feedback
        - action_heavy: 20 entries with user actions

    Total: ~102 entry records
    """
    print(f"🎯 Generating comprehensive test dataset for workspace '{workspace}'...")

    dataset = {
        "single_turns": create_single_turn_entries(workspace),
        "conversations": create_conversation_threads(workspace),
        "feedback_heavy": create_feedback_heavy_entries(workspace),
        "action_heavy": create_action_heavy_entries(workspace),
    }

    total_entries = sum(len(entries) for entries in dataset.values())

    print("✅ Dataset generation complete!")
    print(f"   • Single-turn entries: {len(dataset['single_turns'])}")
    print(f"   • Conversation entries: {len(dataset['conversations'])}")
    print(f"   • Feedback-heavy entries: {len(dataset['feedback_heavy'])}")
    print(f"   • Action-heavy entries: {len(dataset['action_heavy'])}")
    print(f"   • Total entries: {total_entries}")

    return dataset


def save_dataset_to_files(dataset: Dict[str, List[Dict[str, Any]]], output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    """Save the generated dataset to JSON files for loading via API."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for category, entries in dataset.items():
        file_path = output_path / f"{category}.json"
        with open(file_path, "w") as f:
            json.dump(entries, f, indent=2, default=str)
        print(f"💾 Saved {len(entries)} entries to {file_path}")

    # Also save everything as one big file
    all_entries = []
    for entries in dataset.values():
        all_entries.extend(entries)

    with open(output_path / "all_entries.json", "w") as f:
        json.dump(all_entries, f, indent=2, default=str)

    print(f"💾 Saved all {len(all_entries)} entries to {output_path}/all_entries.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a v2 Intake API test dataset as JSON files.")
    parser.add_argument(
        "--workspace",
        default=DEFAULT_WORKSPACE,
        help=(
            "Workspace to embed in each entry's context.app "
            "(must match load_test_data.py --workspace; default: default)"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write JSON files (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    dataset = generate_complete_dataset(workspace=args.workspace)

    save_dataset_to_files(dataset, output_dir=args.output_dir)

    print("\n🚀 Ready to load data! Use the load_test_data.py script to POST to the API.")
