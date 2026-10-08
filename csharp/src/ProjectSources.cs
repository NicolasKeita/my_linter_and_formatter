using System.Diagnostics;
using System.Text.Json;

using Microsoft.CodeAnalysis.CSharp;

namespace NkLint;

internal sealed record SourceFile(string Path, CSharpParseOptions Options);

internal static class ProjectSources
{
    internal static IReadOnlyList<SourceFile> FromProject(string project)
    {
        using var initial = QueryProject(project, targetFramework: null);
        var frameworks = GetProperty(initial.RootElement, "TargetFrameworks")
            .Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        if (frameworks.Length == 0)
        {
            return ExtractSources(initial.RootElement);
        }

        var sources = new List<SourceFile>();
        foreach (var framework in frameworks)
        {
            using var evaluated = QueryProject(project, framework);
            sources.AddRange(ExtractSources(evaluated.RootElement));
        }

        return sources;
    }

    internal static IReadOnlyList<SourceFile> FromSolution(string solution)
    {
        var output = RunDotnet(["sln", solution, "list"]);
        var directory = Path.GetDirectoryName(solution)!;
        var sources = new List<SourceFile>();

        foreach (var line in output.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries))
        {
            var project = line.Trim();
            if (!project.EndsWith(".csproj", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            var path = Path.GetFullPath(Path.Combine(directory, project));
            sources.AddRange(FromProject(path));
        }

        return sources;
    }

    private static JsonDocument QueryProject(string project, string? targetFramework)
    {
        var arguments = new List<string>
        {
            "msbuild", project,
            "-target:AddImplicitDefineConstants",
            "-getItem:Compile",
            "-getProperty:DefineConstants",
            "-getProperty:LangVersion",
            "-getProperty:TargetFrameworks",
            "-nologo",
        };

        if (targetFramework is not null)
        {
            arguments.Add($"-property:TargetFramework={targetFramework}");
        }

        string output;
        try
        {
            output = RunDotnet(arguments);
        }
        catch (IOException exception) when (exception.Message.Contains("MSB4057", StringComparison.Ordinal))
        {
            arguments.Remove("-target:AddImplicitDefineConstants");
            output = RunDotnet(arguments);
        }

        try
        {
            return JsonDocument.Parse(output);
        }
        catch (JsonException exception)
        {
            throw new IOException($"Réponse MSBuild illisible pour {project} : {exception.Message}", exception);
        }
    }

    private static IReadOnlyList<SourceFile> ExtractSources(JsonElement root)
    {
        var defineConstants = GetProperty(root, "DefineConstants");
        var symbols = defineConstants.Split([';', ','],
            StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var language = LanguageVersion.Latest;
        var configuredVersion = GetProperty(root, "LangVersion");

        if (LanguageVersionFacts.TryParse(configuredVersion, out var parsed))
        {
            language = parsed;
        }

        var options = new CSharpParseOptions(language, preprocessorSymbols: symbols);
        var result = new List<SourceFile>();
        if (!root.TryGetProperty("Items", out var items)
            || !items.TryGetProperty("Compile", out var compileItems))
        {
            return result;
        }

        foreach (var item in compileItems.EnumerateArray())
        {
            var path = item.GetProperty("FullPath").GetString();
            if (path is not null && Path.GetExtension(path).Equals(".cs", StringComparison.OrdinalIgnoreCase))
            {
                result.Add(new SourceFile(path, options));
            }
        }

        return result;
    }

    private static string GetProperty(JsonElement root, string name)
    {
        if (root.TryGetProperty("Properties", out var properties)
            && properties.TryGetProperty(name, out var value))
        {
            return value.GetString() ?? string.Empty;
        }

        return string.Empty;
    }

    private static string RunDotnet(IEnumerable<string> arguments)
    {
        var start = new ProcessStartInfo("dotnet")
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };

        foreach (var argument in arguments)
        {
            start.ArgumentList.Add(argument);
        }

        using var process = Process.Start(start)
            ?? throw new IOException("Impossible de démarrer dotnet.");
        var output = process.StandardOutput.ReadToEndAsync();
        var error = process.StandardError.ReadToEndAsync();
        process.WaitForExit();
        if (process.ExitCode != 0)
        {
            throw new IOException($"dotnet a échoué ({process.ExitCode}) : {error.Result}{output.Result}");
        }

        return output.Result;
    }
}
