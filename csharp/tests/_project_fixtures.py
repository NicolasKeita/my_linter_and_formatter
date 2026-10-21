import subprocess


def create_feature_project(target):
    project_dir = target / "App"
    project_dir.mkdir()
    project = project_dir / "App.csproj"
    project.write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
        "<TargetFramework>net10.0</TargetFramework>"
        "<DefineConstants>FEATURE</DefineConstants></PropertyGroup>"
        '<ItemGroup><Compile Remove="Ignored.cs" />'
        '<Compile Include="../Shared.cs" /></ItemGroup></Project>',
        encoding="utf-8",
    )
    (project_dir / "Ignored.cs").write_text("class Ignored { int first, second; }\n", encoding="utf-8")
    (project_dir / "Feature.cs").write_text(
        "#if FEATURE\nclass Feature\n{\n    int Six(int a, int b, int c, int d, int e, int f) => a;\n}\n#endif\n",
        encoding="utf-8",
    )
    (target / "Shared.cs").write_text(
        "class Shared\n{\n    int Six(int a, int b, int c, int d, int e, int f) => a;\n}\n", encoding="utf-8"
    )
    return project


def create_solution(case, target, project):
    created = subprocess.run(
        ["dotnet", "new", "sln", "--name", "Workspace"], cwd=target, capture_output=True, text=True
    )
    case.assertEqual(created.returncode, 0, created.stdout + created.stderr)
    solution = target / "Workspace.slnx"
    added = subprocess.run(
        ["dotnet", "sln", str(solution), "add", str(project)], cwd=target, capture_output=True, text=True
    )
    case.assertEqual(added.returncode, 0, added.stdout + added.stderr)
    return solution


def create_format_project(target):
    project = target / "Sample.csproj"
    project.write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
        "<TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>",
        encoding="utf-8",
    )
    source = target / "Sample.cs"
    source.write_text(
        "namespace Demo; class Sample{public int Add(int left,int right){return left+right;}}\n", encoding="utf-8"
    )
    return project, source
