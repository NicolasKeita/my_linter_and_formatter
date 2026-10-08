# Linter et formatter C#

`nk-csharp` reprend les contrôles de taille, de déclarations et de commentaires du linter C++
en les appliquant à la syntaxe C# avec Roslyn. `dotnet format` effectue les corrections de style
selon le fichier [`.editorconfig`](.editorconfig) fourni ici. Le SDK .NET 10 est requis ; les
assemblages Roslyn proviennent du SDK installé, sans paquet NuGet supplémentaire.

## Utilisation

Depuis la racine de ce dépôt :

```sh
dotnet build csharp/NkLint.csproj
dotnet run --project csharp/NkLint.csproj -- init chemin/vers/projet
dotnet run --project csharp/NkLint.csproj -- lint chemin/vers/projet
dotnet run --project csharp/NkLint.csproj -- format chemin/vers/projet/Projet.csproj
dotnet run --project csharp/NkLint.csproj -- check chemin/vers/projet/Projet.csproj
```

`init` copie la configuration dans le dossier indiqué et refuse d'écraser un `.editorconfig`
existant. Si le projet en possède déjà un, fusionnez les réglages souhaités manuellement.
La commande `format` modifie le projet avec `dotnet format`. La commande `check` lance
`dotnet format --verify-no-changes`, puis le linter, et ne modifie pas les sources. Les deux
commandes de formatage exigent un `.csproj`, `.sln` ou `.slnx`. Un dossier convient s'il
contient exactement un de ces fichiers à sa racine. `lint` accepte aussi un fichier `.cs`.

Avec un `.csproj`, le linter demande à MSBuild les fichiers `Compile` évalués : les entrées
`Include` et `Remove`, même hors du dossier du projet, sont respectées. Il reprend aussi les
symboles `DefineConstants` et la version du langage pour les branches conditionnelles `#if`.
Une solution réunit les fichiers de ses projets C#, y compris les projets à plusieurs frameworks.
Avec un dossier ou un fichier `.cs` isolé, le linter parcourt les sources directement et
utilise la syntaxe C# la plus récente sans symboles de projet. Pour `check` sur un dossier,
le linter utilise le même projet ou la même solution que `dotnet format`.

Les commandes retournent 0 si tout est conforme, 1 en cas d'écart et 2 si les arguments ou
le chemin sont invalides. Pour les erreurs de compilation et les diagnostics sémantiques,
exécutez aussi `dotnet build` sur votre projet.

## Règles du linter

| Code | Contrôle |
| --- | --- |
| NK000 | Erreur de syntaxe C#. |
| NK001 | Ligne de 120 caractères maximum, commentaires compris. |
| NK002 | Fichier de 400 lignes maximum. |
| NK003 | Corps de méthode, constructeur, accesseur, fonction locale ou lambda de 40 lignes maximum. |
| NK004 | Définition de méthode, constructeur, opérateur, fonction locale ou lambda avec 5 paramètres maximum. |
| NK005 | Une variable par déclaration locale, champ ou événement. Les déclarations `for` sont exemptées. |
| NK006 | Aucun commentaire `//` ou `/* */` à l'intérieur d'un corps de fonction. |
| NK007 | Commentaires sur une ligne distincte du code. |
| NK008 | Ligne vide entre les déclarations locales initiales et l'instruction suivante. |
| NK009 | Signale une variable initialisée puis immédiatement retournée. |
| NK010 | Fichier sans code C#. |
| NK011 | Au plus 10 fichiers `.cs` directs par dossier. |

Le contrôle descend dans les sous-dossiers et ignore `.git`, `.vs`, `bin`, `obj`,
`node_modules` et `TestResults`, ainsi que les fichiers `*.g.cs`, `*.generated.cs`,
`*.Designer.cs` et `*.AssemblyInfo.cs`. Le linter lit les arbres syntaxiques Roslyn :
les virgules d'un appel ou d'un type générique ne sont pas prises pour des déclarations
multiples, et `//` dans une chaîne de caractères n'est pas traité comme un commentaire.
Les plafonds de 400 lignes par fichier et 10 fichiers directs par dossier sont des adaptations
volontaires des seuils C++ aux projets C#.

Le formatter règle notamment l'indentation de 4 espaces, les fins de ligne LF, les espaces
en fin de ligne, le saut de ligne final, l'ordre des `using` et le placement des accolades.
La limite de 120 caractères est contrôlée par NK001 : `dotnet format` ne coupe pas
automatiquement toutes les expressions longues.

Les règles liées à `main.cpp`, aux modules C++20, aux initialiseurs désignés et à
l'alignement manuel des membres ne sont pas applicables au C#. Le contrôle automatique de
la langue des commentaires n'est pas inclus : une détection fiable aurait besoin d'une
bibliothèque ou d'un service linguistique distinct.

## Tests

```sh
python -m unittest discover -s csharp/tests -v
```
