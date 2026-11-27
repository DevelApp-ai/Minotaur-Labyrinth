using System.Text.Json;
using Minotaur.Labyrinth;
using Xunit;

namespace Minotaur.Tests.Labyrinth;

/// <summary>
/// Corpus verification gate for the shipped csharp10 rule pack: runs every
/// tests/csharp10 case through the real engine and checks its expected.json —
/// the vulnerable file must produce the expected findings, the safe file none.
/// The rules are exercised both ways: from the YAML rule directory (the
/// classic loader path) and through a binary rule pack built by
/// <see cref="LabyrinthRulePack"/> (the update-package path), mirroring the
/// Minotaur repo's <c>labyrinth verify-corpus</c> gate so package releases
/// cannot regress the shipped rules.
/// </summary>
public sealed class CorpusVerificationTests
{
    [Fact]
    public void CSharp10_Corpus_Passes_ThroughYamlRules()
    {
        var failures = VerifyAll(packed: false);
        Assert.True(failures.Count == 0, string.Join("; ", failures));
    }

    [Fact]
    public void CSharp10_Corpus_Passes_ThroughPackedRules()
    {
        var failures = VerifyAll(packed: true);
        Assert.True(failures.Count == 0, string.Join("; ", failures));
    }

    private static List<string> VerifyAll(bool packed)
    {
        var root = AppContext.BaseDirectory;
        var rulesDir = Path.Combine(root, "rules", "csharp10");
        var testsRoot = Path.Combine(root, "tests", "csharp10");
        Assert.True(Directory.Exists(rulesDir), $"rules not found: {rulesDir}");
        Assert.True(Directory.Exists(testsRoot), $"corpus not found: {testsRoot}");

        var grammarsRoot = ScanHost.FindGrammarsRoot();
        var target = ScanHost.ResolveTarget("csharp10");
        var grammarContent = File.ReadAllText(ScanHost.GrammarFilePath(grammarsRoot, target));

        LabyrinthRulePackFileResult? pack = null;
        if (packed)
        {
            var packPath = Path.Combine(Path.GetTempPath(), "labyrinth-corpus-tests-" + Guid.NewGuid().ToString("N") + ".labyrinthpack");
            var built = LabyrinthRulePack.Build(rulesDir, grammarContent, target.Directory, packPath);
            Assert.True(built.IsValid, string.Join("; ", built.Errors));
            pack = LabyrinthRulePack.TryRead(packPath, target.Directory, LabyrinthRulePack.GrammarSha256(grammarContent));
            Assert.True(pack.IsValid, string.Join("; ", pack.Errors));
        }

        var failures = new List<string>();
        foreach (var caseDir in Directory.GetDirectories(testsRoot).OrderBy(d => d, StringComparer.Ordinal))
        {
            var ruleId = Path.GetFileName(caseDir);
            var failure = VerifyCase(rulesDir, caseDir, ruleId, target.Directory, grammarContent, pack);
            if (failure is not null)
            {
                failures.Add($"csharp10/{ruleId}: {failure}");
            }
        }

        Assert.True(Directory.GetDirectories(testsRoot).Length > 0, "no corpus cases found");
        return failures;
    }

    private static string? VerifyCase(
        string rulesDir, string caseDir, string ruleId, string grammarName, string grammarContent,
        LabyrinthRulePackFileResult? pack)
    {
        var vulnerable = Directory.GetFiles(caseDir, "vulnerable.*").FirstOrDefault();
        var safe = Directory.GetFiles(caseDir, "safe.*").FirstOrDefault();
        var expectedPath = Path.Combine(caseDir, "expected.json");
        if (vulnerable is null || safe is null || !File.Exists(expectedPath))
        {
            return "needs vulnerable.*, safe.* and expected.json";
        }

        using var doc = JsonDocument.Parse(File.ReadAllText(expectedPath));
        var root = doc.RootElement;
        if (root.GetProperty("rule").GetString() != ruleId)
        {
            return "expected.json 'rule' mismatch";
        }

        var expectedFindings = root.GetProperty("findings").EnumerateArray()
            .Select(f => (file: f.GetProperty("file").GetString()!, line: f.GetProperty("line").GetInt32()))
            .ToList();

        // Resolve the rule under verification: from the binary pack, or from
        // the YAML rule directory (the classic path).
        LabyrinthRule rule;
        IReadOnlyList<CompiledLabyrinthRule> compiledCaseRules;
        LabyrinthRuleSet? yamlCaseRules = null;
        if (pack is not null)
        {
            var compiledRule = pack.Rules.FirstOrDefault(r =>
                string.Equals(r.Rule.Id, ruleId, StringComparison.Ordinal));
            if (compiledRule is null)
            {
                return $"rule '{ruleId}' not found in rule pack";
            }

            rule = compiledRule.Rule;
            compiledCaseRules = new[] { compiledRule };
        }
        else
        {
            var loaded = new LabyrinthRulePackLoader().TryLoadDirectory(rulesDir);
            if (!loaded.IsValid)
            {
                return $"invalid rule pack: {string.Join("; ", loaded.Errors)}";
            }

            var yamlRule = loaded.RuleSet.Rules.FirstOrDefault(r => r.Id == ruleId);
            if (yamlRule is null)
            {
                return $"rule '{ruleId}' not found in {rulesDir}";
            }

            rule = yamlRule;
            yamlCaseRules = new LabyrinthRuleSet();
            yamlCaseRules.Rules.Add(yamlRule);
            compiledCaseRules = Array.Empty<CompiledLabyrinthRule>();
        }

        var findings = ScanFile(compiledCaseRules, yamlCaseRules, grammarContent, grammarName, vulnerable);
        foreach (var (file, line) in expectedFindings)
        {
            var hit = findings.Any(f =>
                f.RuleId == ruleId
                && f.Sink is ILabyrinthFindingLocation loc
                && Path.GetFileName(loc.FilePath) == file
                && loc.StartLine == line);
            if (!hit)
            {
                return $"expected finding {ruleId} @{file}:{line} not produced " +
                    $"(got: {string.Join(", ", findings.Where(f => f.RuleId == ruleId).Select(Describe))})";
            }
        }

        var safeFindings = ScanFile(compiledCaseRules, yamlCaseRules, grammarContent, grammarName, safe)
            .Where(f => f.RuleId == ruleId)
            .ToList();
        if (safeFindings.Count > 0)
        {
            return $"safe file produced findings: {string.Join(", ", safeFindings.Select(Describe))}";
        }

        return null;
    }

    private static string Describe(LabyrinthTaintFinding finding) =>
        finding.Sink is ILabyrinthFindingLocation loc
            ? $"{finding.RuleId} @{Path.GetFileName(loc.FilePath)}:{loc.StartLine}"
            : $"{finding.RuleId} @<no location>";

    private static List<LabyrinthTaintFinding> ScanFile(
        IReadOnlyList<CompiledLabyrinthRule> compiledRules,
        LabyrinthRuleSet? yamlRules,
        string grammarContent,
        string grammarName,
        string path)
    {
        var source = File.ReadAllText(path);
        var graph = ScanHost.BuildGraph(source, path, grammarContent, grammarName, out var nodes);
        return compiledRules.Count > 0
            ? ScanHost.RunCompiledRules(compiledRules, graph, nodes, path)
            : ScanHost.RunRules(yamlRules!, grammarContent, grammarName, graph, nodes, path);
    }
}
