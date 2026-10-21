# Python : linter et formatter

Cette version garde les limites générales du projet C++ et confie les règles Python courantes à Ruff. Elle utilise l'AST et `tokenize` pour distinguer code, chaînes, docstrings et commentaires.

## Installation

Depuis ce dépôt :

```bash
python -m pip install -e ./python
```

L'installation inclut Ruff et Lingua. La détection de la langue des commentaires est toujours active.

Depuis un autre projet, une installation non éditable fonctionne aussi : `python -m pip install <chemin-vers-ce-dépôt>/python`. La commande `nk-python` est ensuite disponible dans le même environnement Python. On peut également utiliser `python -m nk_python`.

## Publication sur PyPI

Depuis la racine du dépôt :

```bash
cd python
python -m pip install build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/nk_python_style-0.2.5*
```

Remplacer `0.2.5` dans la commande d'upload par la version à publier, définie dans
`pyproject.toml`. Si cette version est déjà publiée sur PyPI, l'incrémenter avant
de reconstruire le paquet. Utiliser un token API PyPI si Twine demande un mot de passe.

## Utilisation

```bash
nk-python check Src Tests              # Ruff et règles propres, sans écriture
nk-python format Src Tests             # trie les imports et formate en place
nk-python check fichier.py            # fichier précis
nk-python check . --max-files 10       # seuil de dossier personnalisé
nk-python check . --similarity-scope project
```

Sans chemin, la commande traite le dossier courant. Les sous-dossiers de cache, d'environnement virtuel et de construction sont ignorés. Cela inclut tous les dossiers dont le nom commence par `.venv`, comme `.venv-cardd` et `.venv-vision`. `check` contrôle **aussi** le formatage Ruff et retourne un code non nul si une règle échoue. `format` applique le tri des imports Ruff et `ruff format`; relancer `check` pour les diagnostics qui ne se corrigent pas automatiquement.

Les sorties de compilation et rapports `bin`, `obj`, `build`, `cmake-build-*`, `dist`, `coverage` et `htmlcov`, les caches et dossiers IDE `.cache`, `.vs`, `.idea`, ainsi que les métadonnées `*.egg-info`, sont exclus à chaque niveau. Ils ne sont ni parcourus ni comptés dans les limites de structure. Les dossiers sources voisins comme `binary`, `objects` ou `build_tools` restent analysés.

Les diagnostics s'affichent sans extraits de code, avec des chemins relatifs au dossier courant.
La sortie de `check` commence par un résumé : fichiers analysés, nombre de warnings du linter (Ruff et règles `PY…`), problèmes d'ordre des imports et fichiers à reformater. Elle présente ensuite les diagnostics du linter, puis une section formatter à la fin : ordre des imports et fichiers à reformater. Cette dernière correspond aux corrections appliquées par `format`. Les autres corrections automatiques proposées par Ruff ne sont pas appliquées par cette commande.
Dans `check` et `format`, le bilan du formatage affiche les totaux sur l'ensemble des fichiers en une seule ligne, même lorsque le traitement se fait par lots de 50.

## Règles

| Code | Contrôle |
| --- | --- |
| `PY001` | Ligne de 120 caractères maximum, commentaires compris. |
| `PY002` | Fichier de 120 lignes maximum. |
| `PY003` | Fonction ou méthode de 40 lignes maximum, signature comprise. |
| `PY004` | Cinq paramètres maximum ; `self` ou `cls` est exclu pour les méthodes. |
| `PY005` | Commentaire de fin de ligne interdit, sauf directive d'outil. |
| `PY006` | Commentaire dans une fonction interdit, sauf directive d'outil ; utiliser une docstring ou clarifier le code. |
| `PY007` | Commentaire qui semble non anglais. Les textes trop courts ou ambigus sont ignorés. |
| `PY008` | Huit fichiers `.py`/`.pyi` directs maximum dans un dossier parcouru. |
| `PY009` | Huit sous-dossiers directs maximum dans chaque dossier parcouru, y compris les sous-dossiers vides, après exclusions. |
| `PY010` | Noms de fichiers similaires : variantes numériques/séparateurs ou similarité ≥ 85 %, sans renommage automatique. |

`PY010` compare les `.py` entre eux et les `.pyi` entre eux, dans chaque dossier par défaut.
`--similarity-scope project` étend les comparaisons à tous les chemins sélectionnés par l'invocation.
Le warning apparaît sur chaque fichier concerné, avec ses correspondances et motifs ; `check`
retourne 1 en présence de warnings. `format` ne renomme aucun fichier. Voir la
[politique commune](../README.md#noms-de-fichiers-similaires) pour la normalisation, les seuils et les limites.

Ruff vérifie en plus les erreurs Python (`E4`, `E7`, `E9`, `F`), l'ordre des imports (`I`), les erreurs fréquentes (`B`), certaines modernisations sûres (`UP`) et la variable créée uniquement pour être retournée (`RET504`). Sa configuration est fournie par l'outil, donc les mêmes règles s'appliquent depuis un autre projet. Le formatter impose une indentation de quatre espaces, des guillemets doubles et des fins de ligne LF. Les règles C++ propres aux accolades, `#include`, modules et initialiseurs désignés ne s'appliquent pas à Python.

Les directives usuelles (`# noqa`, `# type: ignore`, `# pylint:`, `# fmt:`, `# ruff:`, `# isort:` et `# pragma: no cover`) restent permises. Les docstrings ne sont pas des commentaires `#` et restent autorisées dans les fonctions.
