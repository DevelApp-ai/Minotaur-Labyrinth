#!/usr/bin/env python3
"""Validate a Labyrinth rule pack directory (Minotaur-Labyrinth).

Mirrors Minotaur's LabyrinthRuleLoader.Validate + LabyrinthRulePackLoader
(DevelApp-ai/Minotaur#101/#105) and the Labyrinth grammar in
Minotaur-Grammars (specialized/labyrinth/Labyrinth.grammar, issue #182/#184):

- every .yaml/.yml file under the pack root has a non-empty `rules:` list
- rule ids are kebab-case and unique across the whole pack
- severity is ERROR|WARNING|INFO, type is search|taint
- search rules define `pattern` and no sources/sinks
- taint rules define non-empty sources and sinks of pattern entries
- propagator from/to are well-formed metavariables occurring in the pattern
- all patterns use well-formed $NAME metavariables

Usage: python3 scripts/validate_rules.py [pack-dir]   (default: rules/)
Exit code 0 when the pack is valid, 1 otherwise (errors on stderr).
"""

import re
import sys
from pathlib import Path

import yaml

RULE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
METAVAR = re.compile(r"^\$[A-Z_][A-Z0-9_]*$")
SEVERITIES = {"ERROR", "WARNING", "INFO"}
TYPES = {"search", "taint"}


def metavars_wellformed(pattern, errors, label):
    for m in re.finditer(r"\$[A-Za-z0-9_]*", pattern):
        if not METAVAR.match(m.group(0)):
            errors.append(f"{label}: malformed metavariable '{m.group(0)}' in pattern (expected $NAME with [A-Z_][A-Z0-9_]*)")


def validate_pattern_entry(entry, errors, label):
    if not isinstance(entry, dict):
        errors.append(f"{label}: entry must be a mapping with a 'pattern'")
        return
    pattern = entry.get("pattern")
    if not isinstance(pattern, str) or not pattern.strip():
        errors.append(f"{label}: 'pattern' is required and must be a non-empty string")
        return
    metavars_wellformed(pattern, errors, label)
    cond = entry.get("condition")
    if cond is not None and not isinstance(cond, str):
        errors.append(f"{label}: 'condition' must be a string")


def validate_rule(rule, label, errors):
    if not isinstance(rule, dict):
        errors.append(f"{label}: rule must be a mapping")
        return

    rid = rule.get("id")
    if not isinstance(rid, str) or not rid.strip():
        errors.append(f"{label}: 'id' is required")
    elif not RULE_ID.match(rid):
        errors.append(f"{label}: rule id '{rid}' must be kebab-case ([a-z0-9][a-z0-9-]*)")

    severity = rule.get("severity")
    if not isinstance(severity, str) or severity not in SEVERITIES:
        errors.append(f"{label} ({rid}): 'severity' must be one of {sorted(SEVERITIES)}")

    message = rule.get("message")
    if message is not None and not isinstance(message, str):
        errors.append(f"{label} ({rid}): 'message' must be a string")

    rtype = rule.get("type")
    if rtype not in TYPES:
        errors.append(f"{label} ({rid}): 'type' must be 'search' or 'taint'")
        return

    if rtype == "search":
        if rule.get("sources") or rule.get("sinks"):
            errors.append(f"{label} ({rid}): 'sources'/'sinks' are only valid for type 'taint'")
        pattern = rule.get("pattern")
        if not isinstance(pattern, str) or not pattern.strip():
            errors.append(f"{label} ({rid}): search rules require a 'pattern'")
        else:
            metavars_wellformed(pattern, errors, f"{label} ({rid})")
        cond = rule.get("condition")
        if cond is not None and not isinstance(cond, str):
            errors.append(f"{label} ({rid}): 'condition' must be a string")
        return

    sources = rule.get("sources")
    sinks = rule.get("sinks")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{label} ({rid}): taint rules require a non-empty 'sources' list")
    else:
        for j, e in enumerate(sources):
            validate_pattern_entry(e, errors, f"{label} ({rid}): sources[{j}]")
    if not isinstance(sinks, list) or not sinks:
        errors.append(f"{label} ({rid}): taint rules require a non-empty 'sinks' list")
    else:
        for j, e in enumerate(sinks):
            validate_pattern_entry(e, errors, f"{label} ({rid}): sinks[{j}]")

    for key in ("sanitizers",):
        entries = rule.get(key)
        if entries is None:
            continue
        if not isinstance(entries, list):
            errors.append(f"{label} ({rid}): '{key}' must be a list")
            continue
        for j, e in enumerate(entries):
            validate_pattern_entry(e, errors, f"{label} ({rid}): {key}[{j}]")

    propagators = rule.get("propagators")
    if propagators is None:
        return
    if not isinstance(propagators, list):
        errors.append(f"{label} ({rid}): 'propagators' must be a list")
        return
    for j, p in enumerate(propagators):
        plabel = f"{label} ({rid}): propagators[{j}]"
        if not isinstance(p, dict):
            errors.append(f"{plabel}: entry must be a mapping with 'pattern', 'from', 'to'")
            continue
        pattern = p.get("pattern")
        if not isinstance(pattern, str) or not pattern.strip():
            errors.append(f"{plabel}: 'pattern' is required and must be a non-empty string")
            pattern = ""
        else:
            metavars_wellformed(pattern, errors, plabel)
        for key in ("from", "to"):
            mv = p.get(key)
            if not isinstance(mv, str) or not METAVAR.match(mv):
                errors.append(f"{plabel}: '{key}' must be a metavariable ($NAME with [A-Z_][A-Z0-9_]*)")
            elif mv not in pattern:
                errors.append(f"{plabel}: '{key}' metavariable '{mv}' does not occur in the propagator pattern")


def validate_pack(root):
    root = Path(root)
    if not root.is_dir():
        return [f"Rule directory does not exist: '{root}'."], 0

    files = sorted(
        list(root.rglob("*.yaml")) + list(root.rglob("*.yml")),
        key=lambda f: str(f),
    )
    errors = []
    seen_ids = {}
    rule_count = 0
    for f in files:
        rel = f.relative_to(root).as_posix()
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as ex:
            errors.append(f"{rel}: invalid rule file YAML: {ex}")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("rules"), list) or not data["rules"]:
            errors.append(f"{rel}: rule file must contain a non-empty 'rules:' list")
            continue
        for i, rule in enumerate(data["rules"]):
            rule_count += 1
            before = len(errors)
            validate_rule(rule, f"{rel}: rules[{i}]", errors)
            if isinstance(rule, dict):
                rid = rule.get("id")
                if isinstance(rid, str) and rid and len(errors) == before:
                    if rid in seen_ids:
                        errors.append(f"{rel}: rules[{i}]: duplicate rule id '{rid}' (already defined in {seen_ids[rid]})")
                    else:
                        seen_ids[rid] = rel
    if rule_count == 0 and not errors:
        errors.append(f"Rule pack directory contains no rule files: '{root}'.")
    return errors, rule_count


def main(argv):
    root = argv[1] if len(argv) > 1 else "rules"
    errors, rule_count = validate_pack(root)
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"INVALID: {len(errors)} error(s) in {rule_count} rule(s) under '{root}'.", file=sys.stderr)
        return 1
    print(f"OK: {rule_count} rule(s) under '{root}' are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
