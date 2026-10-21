# Instructions du dépôt

## Conformité Python obligatoire des linters et formatters

Pour chaque tâche future concernant un linter ou formatter de ce dépôt, rendre aussi
le code Python de l'outil concerné conforme au linter et au formatter Python du dépôt
avant de considérer la tâche comme réussie.

- Cette obligation s'applique aux outils C++ (`cpp/`), Python (`python/`),
  JavaScript/TypeScript (`typescript/`) et C# (`csharp/`). Si plusieurs outils sont
  concernés, vérifier chacun de leurs périmètres.
- Contrôler tous les fichiers Python (`.py` et `.pyi`) propres à l'outil concerné :
  implémentation, points d'entrée, utilitaires, tests et scripts. Ne pas limiter le
  contrôle aux fichiers modifiés pendant la tâche. Les dépendances, caches,
  environnements virtuels et fichiers générés restent hors périmètre selon les
  exclusions habituelles de l'outil Python.
- Si un outil ne contient aucun fichier Python, signaler que cette validation est
  sans objet et effectuer ses validations natives habituelles.
- Utiliser le linter/formatter Python de ce checkout, dans `python/nk_python/`, avec
  ses dépendances et sa configuration. Vérifier la provenance du module chargé ;
  utiliser une installation éditable ou ajouter le dossier `python/` du dépôt au
  `PYTHONPATH` pour éviter une ancienne copie installée.
- Depuis la racine du dépôt, pour chaque dossier d'outil concerné, exécuter :

  ```sh
  python -m nk_python format <dossier-outil>
  python -m nk_python check <dossier-outil>
  ```

- Le `check` final doit retourner le code 0, sans diagnostic du linter ni correction
  de formatage restante. Ruff seul ne suffit pas : les règles Python propres au
  dépôt, dont les limites de taille et de structure des dossiers, doivent aussi passer.
- Corriger les écarts détectés dans ce périmètre, y compris les écarts préexistants.
  Refactoriser si nécessaire, en préservant le comportement du linter/formatter, puis
  relancer les tests pertinents de l'outil concerné et le `check` Python final.
- Ne pas contourner la conformité en désactivant des règles, en ajoutant des
  suppressions ou exclusions artificielles, ni en augmentant les seuils, notamment
  avec `--max-files`. Une modification des règles doit être demandée par l'utilisateur.
- Si la validation ne peut pas aboutir, indiquer précisément le blocage et les
  diagnostics restants ; ne pas annoncer la conformité ni la réussite de la tâche.
- Dans le rapport final, préciser le périmètre Python vérifié, les commandes de
  validation et leurs résultats, ainsi que les validations natives pertinentes.

## Versioning automatique obligatoire

- Dans tout repository, relever d'abord la version applicative, le langage et le
  build ; respecter les conventions existantes.
- Source unique : `pyproject.toml` statique en Python, `package.json` en JS/TS,
  mécanisme conventionnel ailleurs ; à défaut, initialiser `VERSION` à `0.1.0`, sans
  packaging inutile.
- Sources actuelles des outils indépendants : `cpp/VERSION`,
  `python/pyproject.toml`, `typescript/package.json` et `csharp/NkLint.csproj`.
- Après chaque tâche réussie (code, tests, documentation, configuration, linting,
  refactoring) et validations pertinentes réussies, incrémenter automatiquement une
  seule fois PATCH, dernier composant numérique (`0.1.9` → `0.1.10`), sans
  confirmation. MAJOR/MINOR uniquement sur demande explicite.
- Préserver le versioning dynamique (Git/outils), employer sa méthode compatible,
  sans source indépendante supplémentaire ; synchroniser uniquement les dérivés
  nécessaires. Signaler toute incompatibilité.
- Vérifier l'enregistrement ; inclure la version dans les modifications et
  l'éventuel commit selon les conventions Git, comme partie intégrante de la tâche.
- Aucun incrément en cas d'échec ou d'analyse explicitement en lecture seule ; aucun
  changement des versions de dépendances, tag Git, release GitHub ou déploiement
  automatique, dépendance superflue ou système complexe de release.
- Rapport final : ancienne → nouvelle version, fichier source, résultat des validations.
