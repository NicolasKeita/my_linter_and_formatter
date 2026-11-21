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
| Structure | Nombre de sous-dossiers directs | **L** : 8 maximum par dossier dans `Src`, `Tests` ou `apps` | **L** : 8 maximum par dossier parcouru, après exclusions |
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

Les quatre outils limitent chaque dossier parcouru à **8 sous-dossiers directs**, y compris les sous-dossiers vides, après application de leurs exclusions habituelles. Les descendants ne sont pas additionnés au parent : chaque niveau est contrôlé séparément. En C#, ce contrôle part du dossier analysé ou de la racine du projet ou de la solution ; un fichier source isolé ne déclenche pas les contrôles de structure.

| Langage | Installation et commandes principales | Règles principales |
| --- | --- | --- |
| [Python](python/README.md) | `python -m pip install -e ./python`, puis `python -m nk_python check <chemin>` ou `python -m nk_python format <chemin>` | Ruff et contrôles AST/tokenize : 120 caractères et 120 lignes par fichier, 40 lignes par fonction, 5 paramètres, placement et langue des commentaires, 8 fichiers Python directs par dossier. Ruff et Lingua sont installés par défaut. |
| [C#](csharp/README.md) | `dotnet build csharp/NkLint.csproj`, puis `dotnet run --project csharp/NkLint.csproj -- check <projet.csproj>`. Les sous-commandes `init` et `format` configurent et corrigent le projet. | Roslyn et `dotnet format` : 120 caractères et 400 lignes par fichier, 40 lignes par corps de fonction, 5 paramètres, déclarations et commentaires, 10 fichiers C# directs par dossier. SDK .NET 10 requis. |

Les règles de modules C++20, de renommage vers PascalCase et de fichier `main.cpp` ne sont pas transposées. Les règles et exceptions exactes figurent dans les README [Python](python/README.md) et [C#](csharp/README.md).

## Noms de fichiers similaires

Les quatre outils signalent les noms suggérant un découpage artificiel : `Utility_1`,
`Utility-02`, `UtilityPart3`, `Utility__`, `Utility-`, ainsi que les petites fautes comme
`Utiliy`. Un fichier seul ne déclenche pas ce contrôle. Aucun renommage n'est automatique.
Chaque fichier concerné reçoit un warning regroupant ses correspondances directes et leurs motifs.

Le contrôle compare les noms sans extension, après normalisation Unicode NFKC, mise en minuscules,
retrait des caractères invisibles usuels et normalisation des séparateurs `_`, tirets et espaces.
Les numéros terminaux (avec éventuellement `part`, `chunk` ou `split`) sont retirés de manière
répétée ; les chiffres internes restent significatifs. Une base normalisée identique déclenche
un warning, même si elle est courte. Sinon, pour deux bases d'au moins six caractères, le seuil
inclusif est de **85 %**, selon `1 - distance / longueur_maximale`. La distance de
Damerau-Levenshtein tient compte de l'ordre et des inversions adjacentes : `course` / `source`
obtient 66,7 % et ne déclenche aucun warning. Les décisions utilisent le score non arrondi.

Pour les ressemblances approximatives, chaque mot différent doit aussi atteindre **85 %**.
Les mots sont délimités par les séparateurs et les transitions camelCase/PascalCase, y compris
les acronymes (`TestMLTracking` donne `test`, `ml`, `tracking`). Les mots sont comparés dans
l'ordre, à nombre de mots égal : les mots identiques ne compensent pas un mot trop différent.
Un mot ajouté, retiré ou déplacé ne suffit donc pas à déclencher ce warning. Ce filtre ne change
pas la détection des bases identiques après normalisation, notamment les suffixes numériques.

Ainsi, `test_ml_tracking` / `test_ml_training` ne déclenche plus de warning : malgré 85,7 %
globalement, `tracking` / `training` n'obtient que 75 %. En revanche, `test_ml_tracking` /
`test_ml_trakcing` reste signalé (87,5 % sur le mot différent), ainsi que `Utility` / `Utiliy`
(85,7 %) et `Utility_1` / `Utility_2`. Le diagnostic précise que les seuils global et par mot passent.

Par défaut, les comparaisons restent dans chaque dossier. `--similarity-scope project` compare
tous les fichiers retenus dans une même invocation, y compris entre sous-dossiers. Les chemins
répétés sont dédoublonnés ; deux noms strictement identiques dans des dossiers différents restent
autorisés (par exemple deux `index.ts`). Les correspondances ne sont pas transitives.

Chaque extension est comparée séparément : les couples `.cpp` / `.cppm`, `.py` / `.pyi` et
`.ts` / `.js` restent autorisés. En JavaScript/TypeScript, `.test`, `.spec`, `.stories` et `.d`
définissent aussi des rôles séparés ; deux variantes numériques du même rôle restent contrôlées.
Les fichiers non sources et les exclusions habituelles de chaque outil ne participent pas.
En C++, les fichiers `.cpp` et `.cppm` sont contrôlés sous `Src`, `Tests` et `apps` ; pour deux
implémentations déclarant le même module, son préfixe `<Module>-` ne gonfle pas le score approximatif.
En C#, la sélection MSBuild et les exclusions de fichiers générés restent appliquées.

Cette règle est une heuristique de nommage, pas une preuve de duplication ou d'intention.
Des variantes légitimes comme `Sha256` / `Sha512` ou des mots très proches peuvent être signalées.
Un nom tout en minuscules sans séparateur reste un seul mot : ses responsabilités ne sont pas
déduites d'un dictionnaire ou du contenu du fichier.
Des fichiers renommés avec des noms différents peuvent lui échapper. Le mode projet est plus
large et peut produire davantage de faux positifs. Les codes de sortie habituels sont conservés :
écart bloquant dans les outils C++, Python et C#, warning non bloquant en TypeScript sauf avec `--strict`.
