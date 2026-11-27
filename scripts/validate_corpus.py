#!/usr/bin/env python3
"""Validate the Labyrinth rule test corpus (Minotaur-Labyrinth tests/).

Checks, per case directory tests/<grammar-dir>/<rule-id>/:

- the grammar dir exists under the rule pack root (rules/) and contains the rule id
- the case has a vulnerable.* file, a safe.* file, and an expected.json
- expected.json schema: rule == case dir name, cwe matches CWE-<number>,
  source is a non-empty string, findings is a non-empty list
- every finding references an existing non-safe file in the case, with a line
  inside the file and a severity equal to the rule's severity in the pack

Usage: python3 scripts/validate_corpus.py [tests-dir] [rules-dir]
       (defaults: tests/ rules/)
Exit code 0 when the corpus is valid, 1 otherwise (errors on stderr).
"""

import json
import re
import sys
from pathlib import Path

import yaml

CWE = re.compile(r"^CWE-\d+$")


def load_pack(rules_root):
    rules = {}
    for f in sorted(list(rules_root.rglob("*.yaml")) + list(rules_root.rglob("*.yml"))):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
            continue
        grammar = f.relative_to(rules_root).parts[0]
        for rule in data["rules"]:
            if isinstance(rule, dict) and isinstance(rule.get("id"), str):
                rules[rule["id"]] = (rule.get("severity"), grammar)
    return rules


def validate_case(case_dir, tests_root, rules, errors):
    rel = case_dir.relative_to(tests_root).as_posix()
    grammar, rule_id = case_dir.parent.name, case_dir.name

    if rule_id not in rules:
        errors.append(f"{rel}: no rule with id '{rule_id}' in the rule pack")
        return
    severity, rule_grammar = rules[rule_id]
    if rule_grammar != grammar:
        errors.append(f"{rel}: rule '{rule_id}' lives in rules/{rule_grammar}/, not rules/{grammar}/")

    vulnerable = sorted(p for p in case_dir.glob("vulnerable.*") if p.is_file())
    safe = sorted(p for p in case_dir.glob("safe.*") if p.is_file())
    if not vulnerable:
        errors.append(f"{rel}: missing a 'vulnerable.*' sample file")
    if not safe:
        errors.append(f"{rel}: missing a 'safe.*' sample file")

    expected_path = case_dir / "expected.json"
    if not expected_path.is_file():
        errors.append(f"{rel}: missing expected.json")
        return
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        errors.append(f"{rel}: invalid expected.json: {ex}")
        return
    if not isinstance(expected, dict):
        errors.append(f"{rel}: expected.json must be a mapping")
        return

    if expected.get("rule") != rule_id:
        errors.append(f"{rel}: expected.json 'rule' must be '{rule_id}'")
    cwe = expected.get("cwe")
    if not isinstance(cwe, str) or not CWE.match(cwe):
        errors.append(f"{rel}: expected.json 'cwe' must match CWE-<number>")
    source = expected.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append(f"{rel}: expected.json 'source' is required (provenance)")

    findings = expected.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append(f"{rel}: expected.json 'findings' must be a non-empty list")
        return
    for i, finding in enumerate(findings):
        flabel = f"{rel}: findings[{i}]"
        if not isinstance(finding, dict):
            errors.append(f"{flabel}: entry must be a mapping")
            continue
        fname = finding.get("file")
        fpath = case_dir / str(fname) if isinstance(fname, str) else None
        if fpath is None or not fpath.is_file():
            errors.append(f"{flabel}: 'file' must name an existing file in the case dir")
            continue
        if fpath.name.startswith("safe"):
            errors.append(f"{flabel}: findings must reference a vulnerable.* file, not '{fpath.name}'")
        line = finding.get("line")
        n_lines = len(fpath.read_text(encoding="utf-8").splitlines())
        if not isinstance(line, int) or not 1 <= line <= n_lines:
            errors.append(f"{flabel}: 'line' must be an integer in [1, {n_lines}] of {fpath.name}")
        if finding.get("severity") != severity:
            errors.append(f"{flabel}: 'severity' must equal the rule severity '{severity}'")


def validate_corpus(tests_root, rules_root):
    tests_root = Path(tests_root)
    rules_root = Path(rules_root)
    if not tests_root.is_dir():
        return [f"Corpus directory does not exist: '{tests_root}'."], 0
    rules = load_pack(rules_root)
    if not rules:
        return [f"Rule pack directory contains no rules: '{rules_root}'."], 0

    errors = []
    case_count = 0
    for grammar_dir in sorted(p for p in tests_root.iterdir() if p.is_dir()):
        if not (rules_root / grammar_dir.name).is_dir():
            errors.append(f"{grammar_dir.name}: no such directory under the rule pack root '{rules_root}'")
            continue
        for case_dir in sorted(p for p in grammar_dir.iterdir() if p.is_dir()):
            case_count += 1
            validate_case(case_dir, tests_root, rules, errors)
    if case_count == 0 and not errors:
        errors.append(f"Corpus directory contains no case directories: '{tests_root}'.")
    return errors, case_count


def main(argv):
    tests_root = argv[1] if len(argv) > 1 else "tests"
    rules_root = argv[2] if len(argv) > 2 else "rules"
    errors, case_count = validate_corpus(tests_root, rules_root)
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"INVALID: {len(errors)} error(s) in {case_count} case(s) under '{tests_root}'.", file=sys.stderr)
        return 1
    print(f"OK: {case_count} case(s) under '{tests_root}' are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
