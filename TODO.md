# Interface
* `DateMask`: validation si seulement année-mois (et date à fin de mois ---> Non !)
* Lister les items sans dotation:
  * orphelins si `req_qty` supprimée
  * dotation désactivée
  * et si emplacement supprimé ?
  
* Traduction de l'interface sous Windows ? (locale)

* Vessel settings
  * ajouter fonction responsable des soins à bord
  * + son nom
  * ajout de signature (png ou electronique ?)
  
* Dashboard/Liste des médicaments arrivant à expiration : date (dans xx jours)

* Add theme for MACOS under GTK+ 'cause it is ugly on a MBP

# Fonctionnalités
* Export liste des médicaments à commander (txt, xlsx ?)
  * Multi modèle (templates)
  
* Affichage tableau de bord
  * Histogramme des expirations par mois ?

* Histogramme des durées moyennes de péremption
  * Durée de validité normal
  * taux de remplacement
  * taux de consommation
  * durée effective de péremption
  -> but voir si on nous envoie des presque périmés systématiquement
  -> voir quels sont les médicaments effectivement consommés

* Afficher les contacts CCMM

* ajouter une interface web : la possibilité de broadcaster en réseau l'application, et de modifier les inventaires
  -> analyser au préalable les risques de modifs involontaires, vérrouillage des accès config, identification...
  
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
