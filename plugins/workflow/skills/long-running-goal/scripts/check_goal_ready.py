#!/usr/bin/env python3
"""Lightweight readiness checks for a long-running-goal Markdown file."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))

from markdown_contract import (  # noqa: E402
    missing_required_pattern_errors,
    placeholder_errors,
    render_errors,
    strip_fenced_blocks,
)


@dataclass(frozen=True)
class MilestoneState:
    name: str
    status: str
    review: str
    checkpoint: str


def _table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def milestone_states(markdown_text: str) -> list[MilestoneState]:
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        header = [cell.casefold() for cell in _table_cells(line)]
        if len(header) < 4 or header[:4] not in (
            ["milestone", "status", "review", "checkpoint"],
            ["stage", "status", "review", "checkpoint"],
            ["阶段", "状态", "review", "checkpoint"],
        ):
            continue

        states: list[MilestoneState] = []
        for row in lines[index + 2 :]:
            if not row.lstrip().startswith("|"):
                break
            cells = _table_cells(row)
            if len(cells) < 4:
                continue
            name_match = re.match(r"(?i)^(M\d+|Close)(?:\s|$)", cells[0])
            if name_match:
                name = name_match.group(1)
                name = name.upper() if name.casefold() != "close" else "Close"
                states.append(MilestoneState(name, *cells[1:4]))
        return states
    return []


def h2_section(markdown_text: str, heading_pattern: str) -> str | None:
    match = re.search(
        rf"(?ims)^##\s+(?:{heading_pattern})\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
        markdown_text,
    )
    return match.group("body") if match else None


def named_contract_fields(
    section_text: str,
    labels: dict[str, str],
) -> dict[str, str]:
    collected: dict[str, list[str]] = {}
    current: str | None = None
    for line in section_text.splitlines():
        matched = False
        for label, pattern in labels.items():
            match = re.match(
                rf"(?i)^\s*(?:\d+\.\s*)?{pattern}(?:\s*/[^:：\n]+)?\s*[:：]\s*(.*)$",
                line,
            )
            if match:
                current = label
                collected[current] = [match.group(1)]
                matched = True
                break
        if not matched and current is not None:
            collected[current].append(line)
    return {label: "\n".join(lines).strip() for label, lines in collected.items()}


def milestone_sections(markdown_text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    for match in re.finditer(
        r"(?ims)^#{2,3}\s+(?P<name>M\d+)\b[^\n]*\n"
        r"(?P<body>.*?)(?=^#{1,3}\s+|\Z)",
        markdown_text,
    ):
        sections.setdefault(match.group("name").casefold(), []).append(match.group("body"))
    return sections


def milestone_section_statuses(sections: dict[str, str]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for name, body in sections.items():
        status_match = re.search(
            r"(?im)^(?:Status|状态)\s*[:：]\s*`?([^`\n]+)`?\s*$",
            body,
        )
        if status_match:
            statuses[name] = status_match.group(1).strip()
    return statuses


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goal_file", type=Path)
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Allow Draft status while still checking placeholders and structure.",
    )
    args = parser.parse_args()

    path = args.goal_file
    if not path.exists():
        print(f"missing goal file: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    visible_text = strip_fenced_blocks(text)
    errors: list[str] = []
    overall_statuses = re.findall(
        r"(?im)^(?:overall status|整体状态|goal status|目标状态)\s*[:：]\s*`?([^`\n]+)`?\s*$",
        visible_text,
    )
    normalized_overall_statuses = [status.strip().lower() for status in overall_statuses]

    errors.extend(placeholder_errors(text))

    required_patterns = {
        "M0 milestone": r"\bM0\b",
        "review gate": r"(?i)\breview\s*gate\b|Review gate|评审|验收",
        "checkpoint evidence": r"(?i)\bcheckpoint\b|检查点",
        "checkpoint component": r"(?i)\bcheckpoint\s+component\b|components/checkpoint\.md",
        "planning preflight": r"(?i)\bplanning\s+preflight\b|components/planning-preflight\.md|grill-with-docs",
        "rollback path": r"(?i)\brollback\b|回滚",
        "close/archive procedure": r"(?i)\b(close|archive)\b|关闭|归档",
        "validation evidence": r"(?i)\b(validation|verify|test)\b|验证|测试",
        "failure handling": r"(?i)\b(fail|failure|breakpoint|blocked)\b|失败|断点|阻塞",
        "continuation contract": r"(?i)\bcontinuation\s+contract\b|Continuation contract|继续执行的关键约束",
        "pre-approval boundary": r"(?im)^##\s+Pre-Approval\s*/\s*YOLO\b",
        "runtime hard stops": r"(?i)\bruntime\s+hard\s*stops?\b|运行时硬停止",
        "non-stops": r"(?i)\bnon[- ]?stops?\b|不应中断",
        "reusable prompt": r"(?i)\b(prompt)\b|推荐.*Prompt",
    }
    errors.extend(
        missing_required_pattern_errors(
            visible_text,
            required_patterns,
            message="missing required section signal",
        )
    )

    harness = h2_section(visible_text, r"Loop Blueprint\s*/\s*Harness(?:\s+边界)?")
    if harness is None:
        errors.append("missing Loop Blueprint / Harness section")
    else:
        execution_mode_match = re.search(
            r"(?im)^(?:Execution mode|执行模式)\s*[:：]\s*`?([^`\n]+)`?\s*$",
            harness,
        )
        if not execution_mode_match:
            errors.append("missing execution mode in Loop Blueprint / Harness section")
        else:
            execution_mode = execution_mode_match.group(1).strip().casefold()
            if execution_mode not in {
                "manual staged execution",
                "loop-shaped execution",
                "automated loop",
            }:
                errors.append(
                    "execution mode must be Manual staged execution, "
                    "Loop-shaped execution, or Automated loop"
                )
            elif execution_mode == "manual staged execution":
                opt_out = re.search(
                    r"(?is)Not applicable\s*:\s*manual staged execution(?P<reason>.*)$",
                    harness,
                )
                reason = (
                    opt_out.group("reason").strip(" \t\r\n:;,.—-") if opt_out else ""
                )
                if len(reason) < 10:
                    errors.append("manual harness opt-out requires a reason")
                if re.search(
                    r"(?i)\b(?:uses?|requires?|reads?\s+from|writes?\s+to)\s+"
                    r"(?:the\s+)?(?:[A-Za-z0-9_.-]+\s+)?connector\b|"
                    r"\bconnector-backed\b",
                    visible_text,
                ):
                    errors.append(
                        "goal declares connector use but Loop harness is Not applicable"
                    )
                if re.search(
                    r"(?i)\b(?:uses?|requires?|orchestrates?)\s+"
                    r"(?:(?:parallel|multiple)\s+)?(?:worktrees?|sub-?agents?)\b|"
                    r"\b(?:runs?|uses?|requires?)\s+(?:an?\s+)?"
                    r"(?:automated|recurring)\s+(?:loop|trigger|schedule)\b",
                    visible_text,
                ):
                    errors.append(
                        "goal declares Loop-shaped orchestration but harness is Not applicable"
                    )
            else:
                harness_fields = {
                    "Trigger": r"Trigger",
                    "Inputs": r"Inputs",
                    "Triage and orchestration": r"Triage\s+and\s+orchestration",
                    "Worktree and isolation": r"Worktree\s+and\s+isolation",
                    "Skills and context": r"Skills\s+and\s+context",
                    "Connector read/write boundaries": r"Connector\s+read/write\s+boundaries",
                    "Independent verification": r"Independent\s+verification",
                    "Runtime hard stops": r"Runtime\s+hard\s+stops",
                    "Durable learning": r"Durable\s+learning",
                }
                harness_values = named_contract_fields(harness, harness_fields)
                for label in harness_fields:
                    if label not in harness_values:
                        errors.append(
                            f"Loop-shaped goal is missing harness field: {label}"
                        )
                    elif not harness_values[label].strip(" \t\r\n-*"):
                        errors.append(
                            f"Loop-shaped goal has empty harness field: {label}"
                        )

    approval = h2_section(visible_text, r"Pre-Approval\s*/\s*YOLO(?:\s+边界)?")
    if approval is None:
        errors.append("missing Pre-Approval / YOLO section")
    else:
        approval_labels = {
            "Pre-approved YOLO local operations": r"Pre-approved\s+YOLO\s+local\s+operations",
            "Pre-approved external reads/writes": r"Pre-approved\s+external\s+reads/writes",
            "Runtime hard stops": r"Runtime\s+hard\s+stops",
            "Non-stops": r"Non-stops",
        }
        approval_fields = named_contract_fields(approval, approval_labels)
        for label in approval_labels:
            if not approval_fields.get(label):
                errors.append(f"missing Pre-Approval / YOLO field: {label}")

        local_operations = approval_fields.get(
            "Pre-approved YOLO local operations", ""
        )
        normalized_local_operations = re.sub(
            r"(?i)non[- ]destructive", "", local_operations
        )
        unsafe_local_pattern = re.compile(
            r"(?i)\b(?:delete\s+production|drop\s+(?:database|table)|destroy|"
            r"irreversible|privacy[- ]sensitive|publish|deploy\s+to|"
            r"send\b.*\bmessage|external\s+(?:write|message)|post\s+to)\b"
        )
        if (
            not re.search(r"(?i)\bnon[- ]destructive\b", local_operations)
            or not re.search(r"(?i)\blocal\b", local_operations)
            or unsafe_local_pattern.search(normalized_local_operations)
        ):
            errors.append("YOLO local operations must be non-destructive and local")

        external_approvals = approval_fields.get(
            "Pre-approved external reads/writes", ""
        )
        document_is_draft = bool(normalized_overall_statuses) and set(
            normalized_overall_statuses
        ) == {"draft"}
        if re.search(
            r"(?i)\b(?:pending approval|approval pending|TBD|to be decided|"
            r"unapproved|needs? approval|awaiting (?:user )?approval)\b",
            external_approvals,
        ) and not document_is_draft:
            errors.append("unresolved external write approval keeps the goal Draft")

        hard_stops = approval_fields.get("Runtime hard stops", "")
        for line in hard_stops.splitlines():
            for clause in re.split(
                r"(?i)[;。]|，\s*(?=但)|,\s*(?=(?:but|however)\b)|\.(?=\s|$)",
                line,
            ):
                if re.search(
                    r"(?i)\b(?:not|never|isn't|is not|do not)\b", clause
                ):
                    continue
                recoverable = re.search(
                    r"(?i)\b(?:milestone boundary|checkpoint|rebuild|refresh|reinstall|"
                    r"review gate|first\s+(?:failed\s+)?validation|"
                    r"first\s+validation\s+failure)\b",
                    clause,
                )
                if recoverable:
                    errors.append(
                        "runtime hard stop misclassifies recoverable work: "
                        + recoverable.group(0)
                    )
                    break
            else:
                continue
            break

    states = milestone_states(visible_text)
    if not states:
        errors.append("missing milestone status table")
    close_rows = [state for state in states if state.name.casefold() == "close"]
    milestone_rows = [item for item in states if item.name.casefold() != "close"]
    if states and len(close_rows) != 1:
        errors.append("milestone status table must contain exactly one Close row")
    for state in states:
        if state.status.casefold() not in {
            "ready",
            "not started",
            "in progress",
            "blocked",
            "done",
        }:
            errors.append(f"{state.name} has invalid milestone status {state.status}")
        if state.review.casefold() not in {"pending", "passed", "failed"}:
            errors.append(f"{state.name} has invalid Review status {state.review}")
        if state.checkpoint.casefold() not in {"pending", "done"}:
            errors.append(f"{state.name} has invalid Checkpoint status {state.checkpoint}")
        if state.review.casefold() == "failed" and state.status.casefold() not in {
            "in progress",
            "blocked",
        }:
            errors.append(
                f"{state.name} Review Failed requires milestone status In Progress or Blocked"
            )
        if state.status.casefold() != "done":
            if state.review.casefold() == "passed" or state.checkpoint.casefold() == "done":
                errors.append(
                    f"{state.name} Review/Checkpoint completion requires milestone status Done"
                )
            continue
        if state.review.casefold() != "passed":
            errors.append(
                f"{state.name} status Done requires Review Passed; found {state.review}"
            )
        if state.checkpoint.casefold() != "done":
            errors.append(
                f"{state.name} status Done requires Checkpoint Done; found {state.checkpoint}"
            )

    section_groups = milestone_sections(visible_text)
    for name, bodies in section_groups.items():
        if len(bodies) > 1:
            errors.append(f"duplicate milestone sections: {name.upper()}")
    section_bodies = {name: bodies[0] for name, bodies in section_groups.items()}
    table_ids = {state.name.casefold() for state in milestone_rows}
    section_ids = set(section_groups)
    if "m0" not in table_ids:
        errors.append("milestone status table must include M0")
    for name in sorted(table_ids - section_ids):
        errors.append(f"milestone table has no matching section: {name.upper()}")
    for name in sorted(section_ids - table_ids):
        errors.append(f"milestone section has no matching table row: {name.upper()}")

    section_statuses = milestone_section_statuses(section_bodies)
    for state in states:
        section_status = section_statuses.get(state.name.casefold())
        if section_status and section_status.casefold() != state.status.casefold():
            errors.append(
                f"{state.name} status disagrees between section and milestone table: "
                f"{section_status} != {state.status}"
            )
        if state.status.casefold() == "blocked":
            if state.name.casefold() == "close":
                section_body = h2_section(visible_text, r"Close Gate|关闭门") or ""
            else:
                section_body = section_bodies.get(state.name.casefold(), "")
            if not re.search(
                r"(?im)^(?:Runtime hard-stop evidence|运行时硬停止证据)\s*[:：]\s*\S",
                section_body,
            ):
                errors.append(
                    f"{state.name} Blocked requires section-local runtime hard-stop evidence"
                )

    first_incomplete: MilestoneState | None = None
    milestone_numbers = [int(state.name[1:]) for state in milestone_rows]
    duplicate_numbers = sorted(
        number for number in set(milestone_numbers) if milestone_numbers.count(number) > 1
    )
    if duplicate_numbers:
        errors.append(
            "duplicate milestone rows: "
            + ", ".join(f"M{number}" for number in duplicate_numbers)
        )
    elif milestone_numbers:
        missing_numbers = sorted(set(range(max(milestone_numbers) + 1)) - set(milestone_numbers))
        if missing_numbers:
            errors.append(
                "milestone sequence must be contiguous from M0; missing "
                + ", ".join(f"M{number}" for number in missing_numbers)
            )
        elif milestone_numbers != sorted(milestone_numbers):
            errors.append("milestone rows must be ordered from M0")
    for state in milestone_rows:
        normalized_status = state.status.casefold()
        if normalized_status == "done" and first_incomplete:
            errors.append(
                "milestone order invalid: Done milestone "
                f"{state.name} follows incomplete {first_incomplete.name}"
            )
        elif normalized_status != "done":
            if first_incomplete and normalized_status in {
                "ready",
                "in progress",
                "blocked",
            }:
                errors.append(
                    f"milestone order invalid: {state.name} {state.status} "
                    f"requires {first_incomplete.name} Done"
                )
            first_incomplete = first_incomplete or state

    current_rows = [
        state
        for state in states
        if state.status.casefold() in {"ready", "in progress", "blocked"}
    ]
    if len(current_rows) > 1:
        errors.append(
            "multiple current milestones: "
            + ", ".join(f"{state.name} {state.status}" for state in current_rows)
        )

    if close_rows and close_rows[0].status.casefold() in {
        "ready",
        "in progress",
        "blocked",
        "done",
    }:
        incomplete_milestones = [
            state.name for state in milestone_rows if state.status.casefold() != "done"
        ]
        if incomplete_milestones:
            errors.append(
                f"Close {close_rows[0].status} requires all milestones Done; incomplete: "
                + ", ".join(incomplete_milestones)
            )

    marker: str | None = None
    marker_match = re.search(
        r"(?im)^Planning preflight marker\s*[:：]\s*`?([^`\n]+)`?\s*$",
        visible_text,
    )
    if not marker_match:
        if not args.allow_draft:
            errors.append("missing planning preflight marker field")
    else:
        marker = marker_match.group(1).strip()
        marker_pattern = re.compile(
            r"^preflight:[A-Za-z0-9_.-]+:(?:skip:)?[0-9]{8}-[A-Za-z0-9_.-]+$"
        )
        if not marker_pattern.match(marker):
            errors.append(
                "planning preflight marker must be a non-placeholder id like "
                "preflight:<goal_slug>:<yyyymmdd>-<short-id> or "
                "preflight:<goal_slug>:skip:<yyyymmdd>-<short-id>"
            )

    preflight_status: str | None = None
    status_match = re.search(
        r"(?im)^Planning preflight status\s*[:：]\s*`?([^`\n]+)`?\s*$",
        visible_text,
    )
    if not status_match:
        if not args.allow_draft:
            errors.append("missing planning preflight status field")
    else:
        preflight_status = status_match.group(1).strip().lower()
        valid_statuses = {
            "done",
            "skipped by explicit user instruction",
        }
        if preflight_status not in valid_statuses:
            errors.append(
                "planning preflight status must be Done or Skipped by explicit user instruction"
            )

    if marker and preflight_status:
        marker_is_skip = ":skip:" in marker
        status_is_skip = preflight_status == "skipped by explicit user instruction"
        if marker_is_skip and not status_is_skip:
            errors.append(
                "preflight skip marker requires status Skipped by explicit user instruction"
            )
        elif status_is_skip and not marker_is_skip:
            errors.append("skipped preflight status requires a :skip: marker")

    source_match = re.search(
        r"(?im)^Preflight source\s*[:：]\s*`?([^`\n]+)`?\s*$",
        visible_text,
    )
    preflight_source = source_match.group(1).strip().casefold() if source_match else None
    if not preflight_source:
        if not args.allow_draft:
            errors.append("missing planning preflight source field")
    elif marker and preflight_status:
        if ":skip:" in marker and not preflight_source.startswith("user skip"):
            errors.append("skipped preflight requires source user skip")
        elif ":skip:" not in marker and preflight_source != "grill-with-docs":
            errors.append("completed preflight requires source grill-with-docs")

    if args.allow_draft and any((marker_match, status_match, source_match)) and not all(
        (marker_match, status_match, source_match)
    ):
        if not marker_match:
            errors.append("missing planning preflight marker field")
        if not status_match:
            errors.append("missing planning preflight status field")
        if not source_match:
            errors.append("missing planning preflight source field")

    if not overall_statuses:
        if not args.allow_draft:
            errors.append("missing overall goal status field")
    else:
        allowed_statuses = {"draft", "ready", "in progress", "closed"}
        invalid_statuses = [
            status.strip() for status in overall_statuses if status.strip().lower() not in allowed_statuses
        ]
        if invalid_statuses:
            errors.append(
                "invalid overall goal status; expected Draft, Ready, In Progress, or Closed; found "
                + ", ".join(sorted(set(invalid_statuses)))
            )

        distinct_overall_statuses = set(normalized_overall_statuses)
        if len(distinct_overall_statuses) > 1:
            errors.append(
                "overall goal statuses disagree: "
                + ", ".join(status.strip() for status in overall_statuses)
            )

        overall_status = normalized_overall_statuses[0]
        if overall_status == "draft" and not args.allow_draft:
            errors.append(
                "overall goal status must be Ready, In Progress, or Closed; found Draft"
            )
        elif overall_status == "ready":
            if not current_rows:
                errors.append("overall Ready requires exactly one Ready milestone")
            elif len(current_rows) == 1:
                current = current_rows[0]
                if current.status.casefold() != "ready":
                    errors.append(
                        "overall Ready requires current milestone Ready; found "
                        f"{current.name} {current.status}"
                    )
        elif overall_status == "in progress":
            if not current_rows:
                errors.append(
                    "overall In Progress requires exactly one In Progress or Blocked milestone"
                )
            elif len(current_rows) == 1:
                current = current_rows[0]
                if current.status.casefold() not in {"in progress", "blocked"}:
                    errors.append(
                        "overall In Progress requires current milestone In Progress or Blocked; "
                        f"found {current.name} {current.status}"
                    )

        close_complete = len(close_rows) == 1 and (
            close_rows[0].status.casefold(),
            close_rows[0].review.casefold(),
            close_rows[0].checkpoint.casefold(),
        ) == ("done", "passed", "done")
        if close_complete and overall_status != "closed":
            errors.append(
                "Close is Done/Passed/Done but overall goal status is "
                + overall_status.title()
            )

        if "closed" in normalized_overall_statuses and states:
            incomplete = [
                state.name
                for state in states
                if (
                    state.status.casefold(),
                    state.review.casefold(),
                    state.checkpoint.casefold(),
                )
                != ("done", "passed", "done")
            ]
            if incomplete:
                errors.append(
                    "Closed goal requires every milestone and Close row to be "
                    "Done/Passed/Done; incomplete: "
                    + ", ".join(incomplete)
                )
            close_evidence = h2_section(
                visible_text,
                r"Close execution evidence|Close 执行证据|关闭执行证据",
            )
            if close_evidence is None:
                close_gate = h2_section(visible_text, r"Close Gate|关闭门")
                if close_gate and re.search(
                    r"(?i)\bClose execution evidence\b|Close 执行证据|关闭执行证据",
                    close_gate,
                ):
                    close_evidence = close_gate
            if close_evidence is None:
                errors.append("Closed goal requires Close execution evidence")
            else:
                if not re.search(r"(?i)\b(?:validation|test)\b|验证|测试", close_evidence):
                    errors.append("Close execution evidence must record validation")
                if not re.search(r"(?i)\bcheckpoint\b|检查点", close_evidence):
                    errors.append("Close execution evidence must record checkpoint evidence")

    if errors:
        return render_errors(path, errors)

    print(f"{path}: goal readiness checks OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
