# Python : linter et formatter

Cette version garde les limites générales du projet C++ et confie les règles Python courantes à Ruff. Elle utilise l'AST et `tokenize` pour distinguer code, chaînes, docstrings et commentaires.

## Installation

Depuis ce dépôt :

```bash
python -m pip install -e ./python
```

Pour activer la détection de la langue des commentaires, installer l'extra optionnel (Lingua est volumineux) :

```bash
python -m pip install -e "./python[comments]"
```

Depuis un autre projet, une installation non éditable fonctionne aussi : `python -m pip install <chemin-vers-ce-dépôt>/python`. La commande `nk-python` est ensuite disponible dans le même environnement Python. On peut également utiliser `python -m nk_python`.

## Utilisation

```bash
nk-python check Src Tests              # Ruff et règles propres, sans écriture
nk-python format Src Tests             # trie les imports et formate en place
nk-python check fichier.py            # fichier précis
nk-python check . --max-files 10       # seuil de dossier personnalisé
```

Sans chemin, la commande traite le dossier courant. Les sous-dossiers de cache, d'environnement virtuel et de construction sont ignorés. `check` contrôle **aussi** le formatage Ruff et retourne un code non nul si une règle échoue. `format` applique le tri des imports Ruff et `ruff format`; relancer `check` pour les diagnostics qui ne se corrigent pas automatiquement.

Les diagnostics s'affichent sans extraits de code, avec des chemins relatifs au dossier courant.

## Règles

| Code | Contrôle |
| --- | --- |
| `PY001` | Ligne de 120 caractères maximum, commentaires compris. |
| `PY002` | Fichier de 120 lignes maximum. |
| `PY003` | Fonction ou méthode de 40 lignes maximum, signature comprise. |
| `PY004` | Cinq paramètres maximum ; `self` ou `cls` est exclu pour les méthodes. |
| `PY005` | Commentaire de fin de ligne interdit, sauf directive d'outil. |
| `PY006` | Commentaire dans une fonction interdit, sauf directive d'outil ; utiliser une docstring ou clarifier le code. |
| `PY007` | Commentaire qui semble non anglais ; actif si l'extra `comments` est installé. Les textes trop courts ou ambigus sont ignorés. |
| `PY008` | Huit fichiers `.py`/`.pyi` directs maximum dans un dossier parcouru. |

Ruff vérifie en plus les erreurs Python (`E4`, `E7`, `E9`, `F`), l'ordre des imports (`I`), les erreurs fréquentes (`B`), certaines modernisations sûres (`UP`) et la variable créée uniquement pour être retournée (`RET504`). Sa configuration est fournie par l'outil, donc les mêmes règles s'appliquent depuis un autre projet. Le formatter impose une indentation de quatre espaces, des guillemets doubles et des fins de ligne LF. Les règles C++ propres aux accolades, `#include`, modules et initialiseurs désignés ne s'appliquent pas à Python.

Les directives usuelles (`# noqa`, `# type: ignore`, `# pylint:`, `# fmt:`, `# ruff:`, `# isort:` et `# pragma: no cover`) restent permises. Les docstrings ne sont pas des commentaires `#` et restent autorisées dans les fonctions.
