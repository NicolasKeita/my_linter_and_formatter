# My Linter and Formatter

Ce dépôt contient des outils indépendants pour quatre familles de langages : un [linter et formatter C++](cpp/formatter_and_linter/README.md), une [configuration ESLint pour JavaScript et TypeScript](typescript/README.md), un [outil Python](python/README.md) et un [outil C#](csharp/README.md). Chaque dossier décrit son installation, ses commandes et les règles adaptées au langage.

Le tableau ci-dessous détaille les règles et transformations **activées par les outils C++ et JavaScript/TypeScript**. `L` signifie qu'une anomalie est signalée par le linter, `F` qu'une correction est faite par le formatter, et `—` que la version ne possède pas cette règle. Dans la colonne TypeScript, les règles de style marquées `L + F` produisent un avertissement avec ESLint et peuvent être corrigées par `eslint --fix`. Côté C++, les mentions `.cpp` désignent la branche utilisée pour les fichiers autres que `.cppm` : un `.hpp` fourni explicitement suit aussi cette branche.

| Catégorie | Règle ou transformation | C++ | JavaScript / TypeScript |
| --- | --- | --- | --- |
| Analyse | Longueur des lignes | **L** : 120 caractères maximum dans les `.cpp`, commentaires compris ; pas de contrôle de longueur dans les `.cppm` | **L** : `max-len`, 140 caractères maximum |
| Analyse | Longueur d'un fichier source | **L** : 120 lignes maximum dans les `.cpp` et `.cppm` | — |
| Analyse | Longueur d'une fonction | **L** : 40 lignes maximum dans les `.cpp` | — |
| Analyse | Nombre de paramètres d'une définition de fonction | **L** : 5 maximum dans les `.cpp` et `.cppm` | — |
| Analyse | Corps des fonctions définies dans une interface de module | **L** : 1 ligne de code effective maximum dans les `.cppm` | — |
| Analyse | Langue des commentaires | **L** : détecte les commentaires non anglais si la bibliothèque Python `lingua` est installée ; ignore les textes trop courts | **L** : `nk/no-french-comments` signale les commentaires détectés comme français d'au moins 20 caractères |
| Analyse | Placement des commentaires | **L** : dans les `.cpp`, refuse les commentaires `//` en fin de ligne et attend les blocs juste avant une fonction ou une déclaration hors fonction ; accepte un commentaire d'en-tête dans les trois premières lignes | — |
| Analyse | Commentaires dans les fonctions et interfaces | **L** : inclus dans le contrôle de placement des commentaires des `.cpp` | **L** : `nk/no-comments-in-functions` interdit les commentaires dans les fonctions et les corps d'interfaces TypeScript |
| Analyse | Plusieurs variables déclarées sur une même ligne | **L** : signale les déclarateurs séparés par une virgule au premier niveau | — |
| Analyse | Déclaration sans initialisation suivie d'affectations de membres | **L** : propose une initialisation directe | — |
| Analyse | Initialisation vide (`Type x{}`) suivie d'affectations de membres | **L** : propose un initialiseur désigné C++20 | — |
| Analyse | Variable initialisée uniquement pour être aussitôt retournée | **L** : signale cette déclaration superflue | — |
| Analyse | Nom du fichier contenant `main()` | **L** : exige `main.cpp` | — |
| Analyse | Ligne vide après les déclarations locales initiales | **L** : contrôle dans les `.cpp` | — |
| Analyse | Usage de `console` | — | **L** : `no-console` |
| Analyse | Fichier vide ou ne contenant que des espaces | — | **L** : `nk/no-empty-file` |
| Analyse | Règles recommandées de JavaScript | — | **L** : ensemble `@eslint/js` `recommended` |
| Analyse | Règles recommandées de TypeScript | — | **L** : ensemble `typescript-eslint` `recommended` |
| Formatage | Espaces en fin de ligne | **F** : suppression dans les `.cpp` et `.cppm` | **L + F** : `@stylistic/no-trailing-spaces` |
| Formatage | Espaces insécables | **F** : remplacement par des espaces ordinaires dans les `.cpp` et `.cppm` | — |
| Formatage | Saut de ligne final | **F** : ajouté à l'écriture du fichier | **L + F** : `@stylistic/eol-last` |
| Formatage | Fins de ligne Unix (`LF`) | — | **L + F** : `linebreak-style` |
| Formatage | Indentation de 2 espaces | — | **L + F** : `@stylistic/indent` |
| Formatage | Points-virgules obligatoires | — | **L + F** : `@stylistic/semi` |
| Formatage | Espaces autour des opérateurs infixes | — | **L + F** : `@stylistic/space-infix-ops` |
| Formatage | Espaces dans les accolades d'objet | — | **L + F** : `@stylistic/object-curly-spacing` |
| Formatage | Virgules : pas d'espace avant, un espace après | — | **L + F** : `@stylistic/comma-spacing` |
| Formatage | Espace avant l'ouverture d'un bloc | — | **L + F** : `@stylistic/space-before-blocks` |
| Formatage | `#include` | **F** : dédoublonne, trie, sépare les en-têtes système et locaux ; place `<windows.h>` en premier | — |
| Formatage | Paramètres des signatures de fonctions | **F** : reformate et aligne les paramètres dans les `.cpp` | — |
| Formatage | `if` courts sur une seule ligne | **F** : répartit condition et instruction sur plusieurs lignes dans les `.cpp` | — |
| Formatage | Accolades des structures de contrôle | **F** : place l'accolade ouvrante sur la ligne de `if`, `else`, `for`, `while`, `switch`, `catch`, `do` ou `try` dans les `.cpp` | — |
| Formatage | Accolades des définitions de fonctions | **F** : place l'accolade ouvrante sur une nouvelle ligne dans les `.cpp` | — |
| Formatage | Espacement autour des fonctions et de leurs commentaires | **F** : retire la ligne vide entre un commentaire et sa fonction et sépare les autres blocs dans les `.cpp` | — |
| Formatage | Lignes vides entre prototypes consécutifs | **F** : les supprime au niveau global ou d'un namespace, dans les `.cpp` et `.cppm` | — |
| Formatage | Bloc initial de déclarations locales | **F** : regroupe les déclarations et ajoute une ligne vide avant les instructions suivantes dans les `.cpp` | — |
| Formatage | Alignement des variables locales initiales | **F** : aligne les noms d'au moins deux déclarations contiguës au début d'une fonction `.cpp` | — |
| Formatage | Alignement des membres | **F** : aligne les noms des membres contigus de `struct`, `class` ou `union` dans les `.cppm` | — |
| Formatage | Instructions C++20 `import` et `module` | **F** : trie et dédoublonne les imports, sépare imports système et locaux et normalise les lignes vides dans les `.cpp` | — |
| Formatage | Déclarations `using` | **F** : les déplace après les prototypes ou les imports concernés dans les `.cpp` | — |
| Formatage | Instructions réparties sur plusieurs lignes | **F** : les fusionne si le résultat tient sur 120 caractères, dans les `.cpp` et `.cppm` | — |
| Formatage | Initialiseurs désignés C++20 trop longs | **F** : répartit leurs champs sur plusieurs lignes au-delà de 120 caractères, dans les `.cpp` et `.cppm` | — |
| Structure | Dossiers contenant trop de fichiers directs | **L** : plus de 8 fichiers `.cpp`/`.cppm` dans `Src`, `Tests` ou `apps` | **L** : plus de 10 fichiers de tout type ; seuil configurable avec `--max-files` |
| Structure | Dossiers vides | — | **L** : `nk-lint-structure` les signale, après exclusion des noms ignorés |
| Structure | Nom des fichiers d'implémentation de module | **L** : `<Module>.cpp` pour une seule implémentation ; `<Module>-<Suffix>.cpp` s'il y en a plusieurs | — |
| Structure | Taille d'un module C++20 | **L** : avertit au-delà de 8 fichiers `.cpp` d'implémentation | — |
| Structure | Longueur des `CMakeLists.txt` | **L** : 300 lignes maximum à la racine et sous `Src`, `Tests` ou `apps` | — |
| Opération supplémentaire | Nommage des fichiers de `Src` | **F** : lors d'un traitement explicite de fichiers, convertit notamment les noms en minuscules ou `snake_case` des `.cpp`, `.hpp` et `.h` vers PascalCase ; `main` est exclu | — |

Les contrôles C++ de **structure** sont lancés avec `--check` ou `-r`, depuis le dossier du projet à analyser, sur `Src`, `Tests` et `apps`. Le contrôle TypeScript des dossiers est une commande distincte d'ESLint : `nk-lint-structure <dossier>`. Elle ignore par défaut `.git`, `.next`, `node_modules`, `dist`, `build` et `coverage` ; `--ignore` ajoute un nom à ignorer et `--strict` rend les avertissements bloquants.

Le formatter C++ s'utilise avec `python formatter_and_linter.py -i fichier.cpp` depuis `cpp` (sans `-i`, il écrit `output.cpp`). Le renommage indiqué dans le tableau n'est pas une validation générale des noms : un nom déjà en camelCase peut rester inchangé. `--check` formate le code **en mémoire** avant de lancer le linter : il ne signale donc pas à lui seul un fichier dont le seul écart est le formatage.

Côté JavaScript et TypeScript, `eslint <dossier>` signale les règles et `eslint <dossier> --fix` applique les corrections disponibles. Les ensembles `recommended` viennent des dépendances ESLint et peuvent évoluer avec leurs versions ; les autres lignes du tableau correspondent aux règles explicitement configurées ici. Les détails d'installation et d'utilisation se trouvent dans les README [C++](cpp/formatter_and_linter/README.md) et [TypeScript](typescript/README.md).

## Versions Python et C#

Les deux versions reprennent les contrôles généraux du C++ (taille du code, nombre de paramètres, commentaires et structure des dossiers), avec des seuils et des exceptions adaptés à chaque langage. Leurs `check` vérifient aussi le formatage **sans modifier les fichiers** ; leurs commandes `format` écrivent les corrections disponibles.

| Langage | Installation et commandes principales | Règles principales |
| --- | --- | --- |
| [Python](python/README.md) | `python -m pip install -e ./python`, puis `python -m nk_python check <chemin>` ou `python -m nk_python format <chemin>` | Ruff et contrôles AST/tokenize : 120 caractères et 120 lignes par fichier, 40 lignes par fonction, 5 paramètres, placement des commentaires, 8 fichiers Python directs par dossier. La détection de langue des commentaires est optionnelle. |
| [C#](csharp/README.md) | `dotnet build csharp/NkLint.csproj`, puis `dotnet run --project csharp/NkLint.csproj -- check <projet.csproj>`. Les sous-commandes `init` et `format` configurent et corrigent le projet. | Roslyn et `dotnet format` : 120 caractères et 400 lignes par fichier, 40 lignes par corps de fonction, 5 paramètres, déclarations et commentaires, 10 fichiers C# directs par dossier. SDK .NET 10 requis. |

Les règles de modules C++20, de renommage vers PascalCase et de fichier `main.cpp` ne sont pas transposées. Les règles et exceptions exactes figurent dans les README [Python](python/README.md) et [C#](csharp/README.md).
