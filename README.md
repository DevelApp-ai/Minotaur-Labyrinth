# Minotaur-Labyrinth

Minotaur-Labyrinth SAST: the Labyrinth rule engine and the Labyrinth rule packs.

The Labyrinth engine is packaged as the NuGet package **`develapp.labyrinth`**
(published to the DevelApp-ai GitHub Packages feed) so Minotaur, the Minotaur
MCP server and client machines consume the same binary. Rule sets ship as
compact `.labyrinthpack` update packages built by the engine itself.

## What is here

- `src/Minotaur.Labyrinth` — the engine:
  - Semgrep-style YAML rule schema (`source:`/`source-url:`/`license:`
    attribution per rule), pattern compilation through the real
    DevelApp.StepLexer/StepParser pipeline with the target grammar,
  - search + taint analysis engines, console and SARIF reporting,
  - the binary rule pack format (`.labyrinthpack`): gzip-compressed
    post-grammar-parse rule set with a grammar name + SHA-256 staleness
    guard, so a pack can never silently drift from the grammar it was
    compiled against,
  - the `ScanHost` host adapter (target-grammar resolution, source
    materialization, document-order data-flow graph) so consumers scan
    without reimplementing the host side.
- `src/Minotaur.Labyrinth.Tests` — engine tests plus the corpus gate: the
  shipped `rules/` + `tests/` run through the engine both from YAML and
  through a packed rule file.
- `rules/`, `tests/` — the shipped Labyrinth rule packs and their
  vulnerable/safe corpus cases (today: csharp10, 5 rules).

## Consuming the package

The package is served from the DevelApp-ai GitHub Packages feed (NuGet.config
in this repo shows the source; consumers need `NUGET_AUTH_TOKEN` or a PAT with
`packages:read`):

```xml
<PackageReference Include="develapp.labyrinth" Version="0.1.0" />
```

Minimal scan (rules as a packed update file):

```csharp
var grammarsRoot = ScanHost.FindGrammarsRoot();
var target = ScanHost.ResolveTarget("csharp10");
var grammarContent = File.ReadAllText(ScanHost.GrammarFilePath(grammarsRoot, target));

var packed = LabyrinthRulePack.TryRead(
    "csharp10.labyrinthpack",
    expectedTargetGrammarName: target.Directory,
    expectedGrammarSha256: LabyrinthRulePack.GrammarSha256(grammarContent));

var graph = ScanHost.BuildGraph(source, filePath, grammarContent, target.Directory, out var nodes);
var findings = ScanHost.RunCompiledRules(packed.Rules, graph, nodes, filePath);
```

Building a pack from a YAML rule directory (patterns parse once, at build
time):

```csharp
var built = LabyrinthRulePack.Build(rulesDir, grammarContent, target.Directory, "csharp10.labyrinthpack");
```

## Grammars

Grammars are owned by the Minotaur-Grammars repository and downloaded at build
time (per maintainer direction: Minotaur does not embed grammars). Disable
locally with `-p:SkipGrammarDownload=true`.

## Provenance

The engine and rules originate from the DevelApp-ai/Minotaur repository
(Labyrinth layers, issues #100/#101/#103/#105 and the binary rule pack format
of #283); they live here as their own package starting at version 0.1.0.
