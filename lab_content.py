"""
Static curriculum content for the AI Agent Certification Lab.
Each module has: lesson text, a code exercise (reference solution shown
after attempt), and a multiple-choice quiz that is auto-graded server-side.
"""

MODULES = [
    {
        "id": "m1-foundations",
        "title": "Module 1 — Agent Foundations",
        "difficulty": "Beginner",
        "summary": "Understand what makes an LLM-based system an 'agent': the observe-think-act loop, state, and tools.",
        "lesson": """
An AI agent is more than a single prompt-response call. It is a system built
around a loop:

1. **Observe** — gather context (user input, tool results, memory).
2. **Think** — the model reasons about what to do next.
3. **Act** — the agent calls a tool, asks a clarifying question, or responds.
4. **Repeat** — the loop continues until a goal is reached or a stopping
   condition is hit.

This is often called the ReAct pattern (Reason + Act). The key design
decisions at this stage are: what tools the agent has access to, how state
(conversation history, scratchpad, memory) is represented, and when the loop
should terminate to avoid infinite cycles or runaway costs.
        """,
        "exercise": {
            "prompt": "Write a minimal Python loop that represents an agent's "
                      "observe-think-act cycle, stopping after a tool call "
                      "returns a 'done' signal or after a max number of steps.",
            "starter_code": """def run_agent(observe, think, act, max_steps=5):
    state = observe()
    for step in range(max_steps):
        # TODO: get the next action from the model
        action = None
        # TODO: execute the action and update state
        result = None
        if result == "done":
            break
    return state
""",
            "solution_code": """def run_agent(observe, think, act, max_steps=5):
    state = observe()
    for step in range(max_steps):
        action = think(state)
        result = act(action, state)
        state["last_result"] = result
        if result == "done":
            break
    return state
""",
        },
        "quiz": [
            {
                "question": "What best describes the core loop of an AI agent?",
                "options": [
                    "A single prompt sent once to the model",
                    "Observe, Think, Act, repeated until a stopping condition",
                    "Only retrieving documents from a database",
                    "Training a new model from scratch each session",
                ],
                "answer_index": 1,
            },
            {
                "question": "Why does an agent loop need a max-steps or stopping condition?",
                "options": [
                    "To make the code shorter",
                    "To prevent infinite loops and uncontrolled cost/actions",
                    "Because LLMs cannot be called more than once",
                    "It doesn't need one",
                ],
                "answer_index": 1,
            },
            {
                "question": "In the ReAct pattern, what does the 'Act' step typically involve?",
                "options": [
                    "Fine-tuning the model",
                    "Calling a tool/function or producing a final response",
                    "Deleting the conversation history",
                    "Rendering a UI component only",
                ],
                "answer_index": 1,
            },
        ],
        "pass_score": 70,
    },
    {
        "id": "m2-tools",
        "title": "Module 2 — Tool Use & Function Calling",
        "difficulty": "Intermediate",
        "summary": "Design safe, well-scoped tools and handle tool-call arguments, errors, and validation.",
        "lesson": """
Tools give an agent the ability to act on the world beyond generating text:
searching the web, querying a database, sending an email, or running code.

Good tool design follows a few principles:

- **Narrow scope** — each tool should do one thing well, with a clear,
  minimal input schema.
- **Validation** — never trust arguments blindly; validate types, ranges,
  and permissions before executing.
- **Idempotency & confirmation** — read-only tools (search, lookup) can run
  freely; tools with side effects (send, delete, purchase) should typically
  require explicit confirmation.
- **Structured errors** — return errors as structured data the model can
  reason about and recover from, rather than raw stack traces.
        """,
        "exercise": {
            "prompt": "Implement a `safe_divide` tool function that validates "
                      "its inputs and returns a structured result instead of "
                      "raising an unhandled exception.",
            "starter_code": """def safe_divide_tool(a, b):
    # TODO: validate inputs are numbers
    # TODO: handle division by zero gracefully
    # TODO: return {"ok": True, "result": ...} or {"ok": False, "error": ...}
    pass
""",
            "solution_code": """def safe_divide_tool(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return {"ok": False, "error": "Both inputs must be numbers."}
    if b == 0:
        return {"ok": False, "error": "Division by zero is not allowed."}
    return {"ok": True, "result": a / b}
""",
        },
        "quiz": [
            {
                "question": "Which tools should generally require explicit user confirmation before running?",
                "options": [
                    "Read-only search tools",
                    "Tools with side effects, like sending an email or deleting data",
                    "Tools that only format text",
                    "None — all tools should run automatically",
                ],
                "answer_index": 1,
            },
            {
                "question": "Why should a tool validate its arguments before executing?",
                "options": [
                    "It isn't necessary since the model never makes mistakes",
                    "To prevent invalid or malicious input from causing errors or unsafe actions",
                    "Validation slows down the agent unnecessarily",
                    "Only user-facing forms need validation",
                ],
                "answer_index": 1,
            },
            {
                "question": "What should a tool return when it fails, so the agent can recover?",
                "options": [
                    "Nothing — silently fail",
                    "A raw unhandled exception/stack trace",
                    "A structured error the model can reason about",
                    "Restart the entire program",
                ],
                "answer_index": 2,
            },
        ],
        "pass_score": 70,
    },
    {
        "id": "m3-multiagent",
        "title": "Module 3 — Multi-Agent Orchestration & Safety",
        "difficulty": "Advanced",
        "summary": "Coordinate multiple specialized agents and apply guardrails, evaluation, and human oversight.",
        "lesson": """
Complex tasks are often split across multiple specialized agents — for
example, a planner agent, a research agent, and a writer agent — coordinated
by an orchestrator. This mirrors how teams delegate work.

Key considerations:

- **Clear handoffs** — each agent should have a well-defined input/output
  contract so the orchestrator can route work reliably.
- **Shared state vs isolation** — decide what context is shared between
  agents versus scoped to one agent to avoid confusion or prompt injection
  from one agent's output leaking unchecked into another.
- **Guardrails** — input/output filtering, permission scoping per agent, and
  rate/step limits.
- **Evaluation** — track success rate, cost, and latency; test with
  adversarial and edge-case inputs before deploying.
- **Human oversight** — for high-stakes actions, keep a human in the loop
  or require approval gates.
        """,
        "exercise": {
            "prompt": "Sketch an orchestrator function that routes a task to "
                      "one of several specialized sub-agents based on task type, "
                      "and logs each handoff for auditability.",
            "starter_code": """def orchestrate(task, agents, log):
    # TODO: pick the right agent based on task["type"]
    # TODO: call the agent and record the handoff in `log`
    # TODO: return the agent's result
    pass
""",
            "solution_code": """def orchestrate(task, agents, log):
    agent = agents.get(task["type"])
    if agent is None:
        raise ValueError(f"No agent registered for task type: {task['type']}")
    log.append({"task_type": task["type"], "agent": agent.__name__})
    return agent(task)
""",
        },
        "quiz": [
            {
                "question": "Why use multiple specialized agents instead of one general agent?",
                "options": [
                    "It's always faster to build",
                    "Specialized agents can have narrower, better-scoped responsibilities and permissions",
                    "It removes the need for any guardrails",
                    "Multi-agent systems never fail",
                ],
                "answer_index": 1,
            },
            {
                "question": "What is a key risk when one agent's raw output is passed unchecked into another agent's context?",
                "options": [
                    "It might be prompt-injected or malformed and corrupt downstream behavior",
                    "It uses too much disk space",
                    "There is no risk at all",
                    "It automatically fixes formatting issues",
                ],
                "answer_index": 0,
            },
            {
                "question": "For high-stakes actions (payments, deletions, external communications), what is a recommended safeguard?",
                "options": [
                    "Let agents act fully autonomously with no review",
                    "A human-in-the-loop approval gate before the action executes",
                    "Disable all logging to simplify the pipeline",
                    "Skip evaluation before deployment",
                ],
                "answer_index": 1,
            },
        ],
        "pass_score": 70,
    },
    
]


FINAL_EXAM = [
    {
        "question": "What is the primary loop pattern underlying most AI agents?",
        "options": ["Train-Validate-Test", "Observe-Think-Act", "Compile-Run-Debug", "Extract-Transform-Load"],
        "answer_index": 1,
    },
    {
        "question": "What should trigger a stopping condition in an agent loop?",
        "options": [
            "Reaching a goal, hitting a max-step limit, or an explicit 'done' signal",
            "The user closing their laptop",
            "The model's context window being infinite",
            "Nothing — agents should never stop",
        ],
        "answer_index": 0,
    },
    {
        "question": "What is the safest default for a tool that has side effects (e.g., sending money)?",
        "options": [
            "Run it automatically every time it's suggested",
            "Require explicit confirmation or human approval first",
            "Never allow the model to know it exists",
            "Only log the action after it already happened",
        ],
        "answer_index": 1,
    },
    {
        "question": "Why validate tool arguments before execution?",
        "options": [
            "To prevent invalid, unsafe, or malicious input from being executed",
            "Validation is optional and rarely useful",
            "Because models never produce malformed arguments",
            "To make the code longer",
        ],
        "answer_index": 0,
    },
    {
        "question": "In multi-agent systems, why define clear input/output contracts between agents?",
        "options": [
            "So the orchestrator can route work reliably and avoid ambiguity",
            "Contracts are only needed for single-agent systems",
            "To make debugging impossible",
            "They have no real benefit",
        ],
        "answer_index": 0,
    },
    {
        "question": "What is a structured error return useful for?",
        "options": [
            "It lets the agent reason about the failure and potentially recover",
            "It hides all information from the model",
            "It is only useful for human developers, never for agents",
            "It replaces the need for any error handling",
        ],
        "answer_index": 0,
    },
    {
        "question": "Which practice best supports safe deployment of an agent system?",
        "options": [
            "Skipping evaluation to ship faster",
            "Testing with adversarial/edge-case inputs and tracking success rate, cost, and latency",
            "Granting every agent unrestricted permissions",
            "Avoiding all logging",
        ],
        "answer_index": 1,
    },
    {
        "question": "What risk does unchecked context-sharing between agents introduce?",
        "options": [
            "Faster execution with no downsides",
            "Potential prompt injection or corrupted downstream reasoning",
            "Reduced token usage",
            "Improved security automatically",
        ],
        "answer_index": 1,
    },
    {
        "question": "Which of these is a 'narrow scope' tool design principle?",
        "options": [
            "One tool should try to do as many unrelated things as possible",
            "Each tool should do one thing well with a minimal, clear input schema",
            "Tools should never have input schemas",
            "Tools should always require a full database dump as input",
        ],
        "answer_index": 1,
    },
    {
        "question": "What is human-in-the-loop oversight primarily used for?",
        "options": [
            "Slowing down low-stakes, reversible actions unnecessarily",
            "Approving or reviewing high-stakes or irreversible agent actions",
            "Replacing the need for any tool validation",
            "Only applies to non-AI systems",
        ],
        "answer_index": 1,
    },
]
