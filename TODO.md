# Interface
* `DateMask`: validation si seulement année-mois (et date à fin de mois)
* Lister les items sans dotation:
  * orphelins si `req_qty` supprimée
  * dotation désactivée
* Traduction de l'interface sous Windows ? (locale)

* Dashboard/Liste des médicaments arrivant à expiration : date (dans xx jours)

# Fonctionnalités
* Export liste des médicaments à commander (txt, xlsx ?)
  * Multi modèle (templates)
* Affichage tableau de bord
  * Histogramme des expirations par mois ?
* Sources officielles

# Code
* Utiliser `log.exception()` lorsque nécessaire
* Écriture des tests unitaires
  * Utilisation de `Cerberus` pour vérifier les résultats
  * Utilisation de `coverage.py` pour vérifier la couverture des tests : https://coverage.readthedocs.io/en/coverage-5.1/
* Docstring des fonctions, modules
* Utilisation `GResource`

* Rescue Bag : si Dotation RescueBagReqQty > Dotation Molecule/Equipment ReqQty alors c'est une erreur et il faut réajuster la Dotation Molecule/Equipment ReqQty pour que RescueBagReqQty <= Molecule/Equipment ReqQty.

# Style
* Raffiner CSS exports PDF

# Installeur
* Modifier automatiquement les fichiers `__init__.py` des modules `WeasyPrint` et `CairoSVG` (voir intro dans `setup.py` de Pharmaship)

* Compilation croisée : https://pypi.org/project/crossroad/
