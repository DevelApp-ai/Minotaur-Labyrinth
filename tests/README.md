# Labyrinth rule test corpus

This directory is the test corpus for the rule pack in [`rules/`](../rules/).
Each **case** exercises exactly one rule:

```
tests/
  <grammar-dir>/            # same folder name as under rules/ (e.g. java17, cpp20, common)
    <rule-id>/              # the rule the case exercises
      vulnerable.<ext>      # MUST trigger the rule (at least one finding)
      safe.<ext>            # MUST NOT trigger the rule (zero findings)
      expected.json         # ground truth for the case
```

`expected.json` schema:

```json
{
  "rule": "java-weak-crypto-md5",
  "cwe": "CWE-328",
  "source": "NIST/SAMATE Juliet Test Suite for Java 1.3, CWE328_Reversible_One_Way_Hash__MD5_01.java (CC0 1.0), excerpted",
  "findings": [
    { "file": "vulnerable.java", "line": 7, "severity": "WARNING" }
  ]
}
```

- `rule` — must equal the case directory name and an existing rule id in `rules/<grammar-dir>/`.
- `cwe` — the CWE the case covers (`CWE-<number>`).
- `source` — provenance: where the sample comes from (vendored corpus file, or "authored" + the reference pattern).
- `findings` — expected findings on `vulnerable.<ext>` (line = sink line). `safe.<ext>` implicitly expects zero findings.

## Validation

CI runs the structural validator (layout, schema, rule-id existence, severity
match, finding file/line sanity):

```bash
python3 scripts/validate_rules.py rules/
python3 scripts/validate_corpus.py tests/
```

Engine-level verification (running Minotaur's `LabyrinthRulePackLoader` +
`LabyrinthTaintEngine` over each case directory and diffing against
`expected.json`) is done by the Minotaur host — see
[Minotaur's Labyrinth Rule Author Guide](https://github.com/DevelApp-ai/Minotaur/blob/main/docs/Labyrinth%20Rule%20Author%20Guide.md).

## Sources and licenses

| Source | Used for | License |
| :--- | :--- | :--- |
| [NIST/SAMATE Juliet Test Suite 1.3](https://samate.nist.gov/SARD/test-suites/112) (Java mirror: [find-sec-bugs/juliet-test-suite](https://github.com/find-sec-bugs/juliet-test-suite); C/C++ mirror: [arichardson/juliet-test-suite-c](https://github.com/arichardson/juliet-test-suite-c)) | vendored excerpts (java17 weak-crypto; sink shapes for cpp20) | CC0 1.0 Public Domain |
| [OWASP Benchmark](https://owasp.org/projects/benchmark) | CWE pattern reference for servlet/web cases (java17, csharp10, python311, javascript, typescript) | Apache-2.0 |
| [SecBench.js](https://github.com/cristianstaicu/SecBench.js) (ICSE'23) | server-side JavaScript vulnerability shapes (javascript) | research benchmark; excerpts authored here |
| PySASTBench / PyVul / SecCodeBench-V2 (Python CVE datasets) | Python CWE reference (python311) | see upstream |
| Authored for Minotaur-Labyrinth | minimal canonical vulnerable/safe pairs where public per-language corpora are thin (go119, rust2021, common) or where the rule's source API is framework-specific | MIT (this repo) |

Juliet/Benchmark files are excerpted (not vendored wholesale) so each case
stays a focused vulnerable/safe pair; the `source` field in `expected.json`
names the exact upstream file. When adding cases, prefer extending the mapped
public corpora and keep the provenance field accurate.

## Adding a case

1. Create `tests/<grammar-dir>/<rule-id>/`.
2. Add `vulnerable.<ext>` (triggers the rule) and `safe.<ext>` (does not).
3. Add `expected.json` with the rule id, CWE, source, and findings (sink line).
4. Run `python3 scripts/validate_corpus.py tests/` — must print `OK`.
