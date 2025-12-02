"""
Natural language UI layer for the DBMigration project.

This module provides an interactive CLI that:
1. Accepts a free-form natural language request from the user
2. Uses an LLM (if available) or simple rules to map it to one or more
   structured migration tasks
3. Generates an executable CLI command equivalent to the planned actions
4. Shows a concise summary and asks for confirmation
5. Executes the requested actions via AgentRouter after confirmation
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agents.agent_router import AgentRouter
from agents.schema_agent import SchemaAgent
from src.utils.config_loader import load_config

logger = logging.getLogger(__name__)


SUPPORTED_TASK_TYPES = [
    "schema_migration",
    "data_migration",
    "validate",
    "convert_query",
]


@dataclass
class PlannedTask:
    """Structured representation of a single planned task."""

    type: str
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NLPlan:
    """Overall plan produced from a natural language request."""

    intent: str
    tasks: List[PlannedTask]
    cli_command: str
    notes: Optional[str] = None


class NaturalLanguagePlanner(SchemaAgent):
    """
    Planner that converts natural language to structured tasks.

    Inherits from SchemaAgent purely to reuse its LLM wiring; it does NOT
    execute schema tasks itself here.
    """

    def __init__(self):
        super().__init__()

    def can_handle(self, task: Dict[str, Any]) -> bool:  # pragma: no cover - not used
        return False

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - not used
        raise NotImplementedError("NaturalLanguagePlanner is not used as a normal agent.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def plan_from_text(
        self,
        text: str,
        default_config_path: str = "config/config.yaml",
    ) -> NLPlan:
        """
        Create an NLPlan from a natural language description.

        Attempts LLM-based parsing first; falls back to simple heuristics
        when LLM is unavailable.
        """
        text = text.strip()
        if not text:
            raise ValueError("Empty description is not allowed.")

        if self.llm_client:
            logger.info("Using LLM to interpret natural language request")
            try:
                return self._plan_with_llm(text, default_config_path)
            except Exception as e:
                logger.warning(f"LLM-based planning failed, falling back to rules: {e}")

        logger.info("Using rule-based interpretation for natural language request")
        return self._plan_with_rules(text, default_config_path)

    # ------------------------------------------------------------------
    # LLM-based planning
    # ------------------------------------------------------------------
    def _plan_with_llm(self, text: str, default_config_path: str) -> NLPlan:
        prompt = f"""
You are helping a user run the DBMigration CLI.

The user describes what they want to do in natural language.
You must map it to one or more tasks using this schema:

  - Allowed task types:
      - "schema_migration": migrate Oracle schema to PostgreSQL
      - "data_migration": migrate table data
      - "validate": run validation/comparison between Oracle and PostgreSQL
      - "convert_query": convert an Oracle SQL query to PostgreSQL

  - For each task, you may use these options (all optional, omit if not needed):
      - tables: list of table names (strings) or null for all tables
      - truncate: boolean (for data_migration)
      - batch_size: integer (for data_migration)
      - schema_sample_size: integer (for validate)
      - data_sample_size: integer (for validate)
      - query: string (for convert_query)

You must respond with STRICT JSON in this shape (no comments, no markdown):
{{
  "intent": "<short plain-language summary of what the user wants>",
  "tasks": [
    {{
      "type": "schema_migration",
      "options": {{
        "tables": ["USERS", "ORDERS"],
        "truncate": false,
        "batch_size": 1000
      }}
    }}
  ],
  "cli_command": "python migrate.py --config {default_config_path} --task schema_migration --tables USERS,ORDERS",
  "notes": "Any brief caveats or assumptions, or empty string if none"
}}

User request:
\"\"\"{text}\"\"\""""

        raw = self.call_llm(
            prompt,
            system_prompt=(
                "You are a precise planner that outputs ONLY valid JSON conforming to the given schema. "
                "Never include backticks, markdown, or commentary."
            ),
            temperature=0.1,
            max_tokens=700,
        )

        if not raw:
            raise RuntimeError("LLM returned no content.")

        cleaned = self._extract_json(raw)
        data = json.loads(cleaned)

        intent = data.get("intent", "").strip() or text
        notes = (data.get("notes") or "").strip() or None
        cli_command = data.get("cli_command") or f"python migrate.py --config {default_config_path}"

        tasks: List[PlannedTask] = []
        for t in data.get("tasks", []):
            t_type = (t.get("type") or "").strip()
            if t_type not in SUPPORTED_TASK_TYPES:
                logger.warning(f"Unsupported task type from LLM, skipping: {t_type!r}")
                continue
            options = t.get("options") or {}
            # Ensure tables is either list or None
            if "tables" in options and options["tables"] is not None and not isinstance(options["tables"], list):
                options["tables"] = [str(options["tables"])]
            tasks.append(PlannedTask(type=t_type, options=options))

        if not tasks:
            raise RuntimeError("LLM did not produce any valid tasks.")

        return NLPlan(intent=intent, tasks=tasks, cli_command=cli_command, notes=notes)

    @staticmethod
    def _extract_json(raw: str) -> str:
        """
        Extract JSON from an LLM response that might be wrapped in code fences.
        """
        raw = raw.strip()
        if raw.startswith("```"):
            # Strip first fence
            raw = raw.split("```", 2)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        return raw.strip()

    # ------------------------------------------------------------------
    # Rule-based planning (no LLM available)
    # ------------------------------------------------------------------
    def _plan_with_rules(self, text: str, default_config_path: str) -> NLPlan:
        lower = text.lower()

        tasks: List[PlannedTask] = []

        # Detect query conversion
        if "convert query" in lower or "translate query" in lower or "convert sql" in lower:
            tasks.append(
                PlannedTask(
                    type="convert_query",
                    options={"query": text},
                )
            )
            intent = "Convert an Oracle SQL query to PostgreSQL."
            cli_command = f'python migrate.py --config {default_config_path} --query "<oracle_query_here>"'
            notes = (
                "Heuristic mapping: you may need to edit the query manually in the command. "
                "For best results, configure an LLM provider."
            )
            return NLPlan(intent=intent, tasks=tasks, cli_command=cli_command, notes=notes)

        wants_validate = "validate" in lower or "verify" in lower or "check" in lower or "compare" in lower
        mentions_schema = "schema" in lower
        mentions_data = "data" in lower or "rows" in lower or "records" in lower

        if wants_validate:
            tasks.append(
                PlannedTask(
                    type="validate",
                    options={
                        "schema_sample_size": 10,
                        "data_sample_size": 5,
                    },
                )
            )

        # Migration intents
        if mentions_schema and not mentions_data:
            # Schema-only migration
            tasks.insert(
                0,
                PlannedTask(
                    type="schema_migration",
                    options={"tables": None},
                ),
            )
            cli_command = f"python migrate.py --config {default_config_path} --schema-only"
            intent = "Migrate schema only from Oracle to PostgreSQL."
        elif mentions_data and not mentions_schema:
            # Data-only migration
            tasks.insert(
                0,
                PlannedTask(
                    type="data_migration",
                    options={
                        "tables": None,
                        "truncate": False,
                        "batch_size": 1000,
                    },
                ),
            )
            cli_command = f"python migrate.py --config {default_config_path} --data-only --batch-size 1000"
            intent = "Migrate data only from Oracle to PostgreSQL."
        else:
            # Default: full migration (schema + data)
            tasks.insert(
                0,
                PlannedTask(
                    type="schema_migration",
                    options={"tables": None},
                ),
            )
            tasks.insert(
                1,
                PlannedTask(
                    type="data_migration",
                    options={
                        "tables": None,
                        "truncate": False,
                        "batch_size": 1000,
                    },
                ),
            )
            cli_command = f"python migrate.py --config {default_config_path}"
            intent = "Run a full migration (schema and data) from Oracle to PostgreSQL."

        notes = (
            "This plan was generated using simple keyword rules because no LLM provider is configured. "
            "For more nuanced interpretations, configure an OpenAI/Anthropic/Ollama/Azure OpenAI provider."
        )

        return NLPlan(intent=intent, tasks=tasks, cli_command=cli_command, notes=notes)


def summarize_plan(plan: NLPlan) -> str:
    """Build a human-readable summary string for terminal output."""
    lines: List[str] = []
    lines.append("\n" + "=" * 70)
    lines.append("  NATURAL LANGUAGE PLAN")
    lines.append("=" * 70)
    lines.append(f"\nIntent: {plan.intent}")

    lines.append("\nPlanned tasks:")
    for i, t in enumerate(plan.tasks, start=1):
        lines.append(f"  {i}. type = {t.type}")
        if t.options:
            lines.append("     options:")
            for k, v in t.options.items():
                lines.append(f"       - {k}: {v}")

    lines.append("\nEquivalent CLI command:")
    lines.append(f"  {plan.cli_command}")

    if plan.notes:
        lines.append("\nNotes:")
        lines.append(f"  {plan.notes}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def execute_plan(plan: NLPlan, config_path: str = "config/config.yaml") -> List[Dict[str, Any]]:
    """
    Execute all tasks in the plan using AgentRouter.

    This assumes that database connection details are already present in
    the config file or environment.
    """
    config = load_config(config_path)
    router = AgentRouter(config)

    results: List[Dict[str, Any]] = []

    for task in plan.tasks:
        payload: Dict[str, Any] = {
            "type": task.type,
            "config": config,
        }
        payload.update(task.options or {})

        logger.info(f"Executing planned task: {task.type}")
        result = router.execute_task(payload)
        results.append(result)

    return results


def run_natural_language_ui(config_path: str = "config/config.yaml") -> Tuple[Optional[NLPlan], Optional[List[Dict[str, Any]]]]:
    """
    Run a simple REPL-style natural language UI.

    Flow:
      1. Ask the user to describe what they want to do
      2. Build a plan and show a summary + equivalent CLI command
      3. Ask for confirmation
      4. Execute tasks if approved
    """
    print("\n" + "=" * 70)
    print("  Oracle to PostgreSQL Migration - Natural Language UI")
    print("=" * 70)
    print(
        "\nDescribe what you want to do in natural language, for example:\n"
        "  - \"Migrate the full database from Oracle to Postgres\"\n"
        "  - \"Only migrate data for USERS and ORDERS tables\"\n"
        "  - \"Validate that data between Oracle and Postgres matches\"\n"
        "  - \"Convert this Oracle query to PostgreSQL: SELECT ...\"\n"
    )
    print("Type 'exit' or 'quit' to abort.\n")

    try:
        text = input("What would you like to do? \n> ").strip()
    except KeyboardInterrupt:
        print("\n\n✗ Natural language UI cancelled by user.")
        return None, None

    if not text or text.lower() in {"exit", "quit"}:
        print("\n✗ No request provided. Exiting.")
        return None, None

    planner = NaturalLanguagePlanner()

    try:
        plan = planner.plan_from_text(text, default_config_path=config_path)
    except Exception as e:
        logger.error(f"Failed to interpret natural language request: {e}", exc_info=True)
        print(f"\n✗ Failed to interpret request: {e}")
        return None, None

    # Show summary and confirmation
    summary = summarize_plan(plan)
    print(summary)

    print("\n--- Approval Required ---")
    print("Review the planned actions above carefully.")
    print("This may modify your target PostgreSQL database depending on the tasks.")

    while True:
        try:
            resp = input("\nDo you want to proceed with these actions? (yes/no): ").strip().lower()
        except KeyboardInterrupt:
            print("\n\n✗ Natural language UI cancelled by user.")
            return plan, None

        if resp in {"yes", "y"}:
            print("\n✓ Approved. Executing tasks...\n")
            try:
                results = execute_plan(plan, config_path=config_path)
            except Exception as e:
                logger.error(f"Failed to execute plan: {e}", exc_info=True)
                print(f"\n✗ Failed to execute plan: {e}")
                return plan, None

            print("\nExecution summary:")
            for i, r in enumerate(results, start=1):
                agent_name = r.get("agent", "Unknown")
                status = r.get("status", "unknown")
                message = r.get("message")
                print(f"  {i}. Agent {agent_name} -> status: {status}")
                if message and status != "success":
                    print(f"       message: {message}")

            print("\n✓ All planned tasks have been processed.")
            return plan, results

        if resp in {"no", "n"}:
            print("\n✗ Plan cancelled by user. No actions were taken.")
            return plan, None

        print("Please answer 'yes' or 'no'.")



