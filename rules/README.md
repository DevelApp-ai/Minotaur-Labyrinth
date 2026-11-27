# Labyrinth rule packs

This directory is the rule pack loaded by Minotaur/Golem via
`LabyrinthRulePackLoader.TryLoadDirectory("rules/")`, which scans `*.yaml` /
`*.yml` **recursively**. Rule ids must be unique across the whole pack.

## Why rules are not in Minotaur-Grammars

Minotaur-Grammars is the single home for **grammar definitions**; this repo
holds the **rule instances** (data) that the Labyrinth engine (Minotaur#100)
runs against code parsed with those grammars. Keeping them separate means
grammar release tarballs never carry rules, and rule packs can evolve without
re-tagging grammars.

## Layout conventions

- `rules/<language>/rules.yaml` — **language-specific** rules. The folder
  name is the target grammar's directory under `programming-languages/` in
  [Minotaur-Grammars](https://github.com/DevelApp-ai/Minotaur-Grammars) (the
  `LabyrinthTargetGrammars` registry in Minotaur), e.g. `csharp10`,
  `python311`, `javascriptes2022`. Every pattern in the folder is a snippet
  of that grammar, parsed via the grammar's `Labyrinth.extension` overlay.
- `rules/common/` — **language-neutral** rules. Patterns here are written
  against the generic data grammars (`json`, `xml`, ...) that are also
  Labyrinth target grammars, so the rules apply to config/data files of any
  project regardless of application language.

To add rules for another language, create `rules/<grammar-dir>/rules.yaml`
using a grammar dir that ships a `Labyrinth.extension` in Minotaur-Grammars
(flagged `"LabyrinthExtension": true` in its `minotaur-metadata.json`).

## Format

See the [rule file format](../README.md#rule-file-format) and Minotaur's
[Labyrinth Rule Author Guide](https://github.com/DevelApp-ai/Minotaur/blob/main/docs/Labyrinth%20Rule%20Author%20Guide.md).
Validate the whole pack with:

```bash
python3 ../scripts/validate_rules.py .
```
