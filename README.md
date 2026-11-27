# Minotaur-Labyrinth

SAST rule packs for **Labyrinth**, the Semgrep-style rule engine of
[Minotaur](https://github.com/DevelApp-ai/Minotaur) (epic
[DevelApp-ai/Minotaur#100](https://github.com/DevelApp-ai/Minotaur/issues/100)),
also consumed by Golem (Minotaur's translation/error-correction and MCP front
end).

This repository is the **single home for Labyrinth SAST rules**. It holds rule
*instances* only — the rule *language* grammar lives in
[Minotaur-Grammars](https://github.com/DevelApp-ai/Minotaur-Grammars)
(`specialized/labyrinth/Labyrinth.grammar`, issue
[#182](https://github.com/DevelApp-ai/Minotaur-Grammars/issues/182)), and the
per-language pattern operators (`$METAVAR`, `...`) are shipped as optional
`Labyrinth.extension` overlays next to each target grammar (issue
[#184](https://github.com/DevelApp-ai/Minotaur-Grammars/issues/184)). See
[Why rules live here and not in Minotaur-Grammars](rules/README.md).

## Layout

```
rules/
  common/                 # language-neutral rules (config/data grammars: json, xml, ...)
    hardcoded-secrets.yaml
  csharp10/               # one folder per Labyrinth target grammar
    rules.yaml            #   (folder name = grammar dir under programming-languages/
  python311/              #    in Minotaur-Grammars, see LabyrinthTargetGrammars)
    rules.yaml
  javascript/
  typescript/
  java17/
  go119/
  rust2021/
  cpp20/
scripts/
  validate_rules.py       # pack validation (mirrors Minotaur's LabyrinthRuleLoader)
  validate_corpus.py      # test-corpus validation (layout + expected.json schema)
tests/                    # per-rule test corpus (vulnerable/safe samples + expected findings)
  README.md               #   layout, sources, licenses — see tests/README.md
```

`rules/<language>/` holds **language-specific** rules: each pattern is a
snippet written in that language's grammar (parsed by StepParser through the
target grammar + its `Labyrinth.extension` overlay).
`rules/common/` holds **language-neutral** rules: patterns written against the
generic data grammars (`json`, `xml`, ...) so they apply to config/data files
of any project, regardless of the application language.

## Consuming the rules in Minotaur / Golem

A rule pack is a directory of `.yaml`/`.yml` files scanned recursively.
Point Minotaur's loader at this repo's `rules/` directory:

```csharp
var pack = new LabyrinthRulePackLoader().TryLoadDirectory("rules/");
if (!pack.IsValid) { /* pack.Errors: "file.yaml: rules[i]: ..." per invalid rule */ }
var ruleSet = new LabyrinthRulePackLoader().LoadDirectory("rules/"); // throws, all errors aggregated
```

See [Minotaur's Labyrinth Rule Author Guide](https://github.com/DevelApp-ai/Minotaur/blob/main/docs/Labyrinth%20Rule%20Author%20Guide.md)
for the engine contract (rule schema, metavariables, ellipsis, Dynamic LINQ
`condition:`, reporting, baselines, exit codes).

### Scanning with the Minotaur CLI

The fastest way to run this pack is the `Minotaur.Cli` console app (merged in
[DevelApp-ai/Minotaur#245](https://github.com/DevelApp-ai/Minotaur/pull/245)):

```bash
# from a Minotaur checkout
dotnet run --project src/Minotaur.Cli -- labyrinth scan \
  --rules /path/to/Minotaur-Labyrinth/rules \
  --grammar java17 \
  --src /path/to/target-project \
  --sarif labyrinth.sarif
```

- `--rules` accepts this repo's pack root (`rules/`) — then only
  `rules/<grammar>` is loaded — or a single pack directory.
- `--grammar` is a `LabyrinthTargetGrammars` directory name (`labyrinth grammars`
  lists them); `--ext` overrides the default extension filter.
- Exit codes: `0` no reportable findings, `1` findings, `2` configuration error.
  Use `--write-baseline labyrinth-baseline.json` after triage and `--baseline`
  in CI so only new findings break the build.
- `labyrinth verify-corpus --rules rules --tests tests` runs this repo's `tests/`
  corpus through the engine (see [Test corpus](#test-corpus)).

## Rule file format

Each file is a `rules:` list. Rule keys, in order:

| Key | Required | Values | Meaning |
| :--- | :--- | :--- | :--- |
| `id` | yes | kebab-case, **unique across the whole pack** | Finding identifier |
| `severity` | yes | `ERROR`, `WARNING`, `INFO` | Finding severity (SARIF level) |
| `message` | yes | free text | Finding message |
| `type` | yes | `search`, `taint` | Analysis kind |
| `pattern` | search | target-grammar snippet | Single pattern to match |
| `condition` | no | Dynamic LINQ string | Extra boolean constraint on the match |
| `sources` / `sinks` | taint | pattern-entry list | Untrusted entry / dangerous arrival points |
| `sanitizers` | no | pattern-entry list | Matches that prune taint |
| `propagators` | no | `pattern` + `from`/`to` | Taint transfer between metavariables |

Patterns are snippets of the **target grammar** with `$NAME` metavariables
(matching one node, unified across the whole rule) and `...` ellipsis (zero or
more siblings). Pattern bodies are parsed by the target grammar +
`Labyrinth.extension` overlay — never by the rule-language grammar itself.

Example (taint rule, C#):

```yaml
rules:
  - id: csharp-sql-injection
    severity: ERROR
    message: "SQL statement built from untrusted request data; use parameterized queries."
    type: taint
    sources:
      - pattern: "Request.Query[$DATA]"
    sinks:
      - pattern: "$CMD.ExecuteNonQuery($SQL)"
    propagators:
      - pattern: "$SQL = $PREFIX + $DATA"
        from: $DATA
        to: $SQL
```

## Validation

Rule files must satisfy the Labyrinth grammar and Minotaur's
`LabyrinthRuleLoader` validation (unique ids, known severity/type, search
rules need `pattern`, taint rules need `sources` + `sinks`, propagator
`from`/`to` must occur in the propagator pattern). CI runs the same checks:

```bash
python3 scripts/validate_rules.py rules/
```

## Test corpus

`tests/` holds the per-rule test corpus: `tests/<grammar-dir>/<rule-id>/` with
`vulnerable.<ext>` (must trigger the rule), `safe.<ext>` (must not) and
`expected.json` (ground-truth findings + provenance). Validate its structure
with:

```bash
python3 scripts/validate_corpus.py tests/ rules/
```

See [tests/README.md](tests/README.md) for the layout, the corpus sources
(NIST/SAMATE Juliet, OWASP Benchmark, SecBench.js, ...) and their licenses.

## Licensing

MIT — see [LICENSE](LICENSE). Rules are data consumed by the engine; the
grammars they target carry their own per-grammar licenses in Minotaur-Grammars.
