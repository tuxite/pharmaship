# bugs, problèmes rencontrés

* L'adresse d'enregistrement des backup n'est pas prise en compte, au moins sous MacOS, ça part directement dans le dossier src de pharmaship.
* Vesssel configuration n'est pas exportée / importée pendant le backup (export/import db)
* En dotation, liste d'équipement, il manque une batterie de 9V, en spare, Lithium.
* Sur les pages d'inventaire, fixer la colomne du haut (des titres) pour toujours la voir.
* Dans la coloration orange, faire la même chose que le rouge (colorer les deux colonnes "Expiry" et "Quantity"), pour vérifier visuellement le besoin de recommander, ou non, selon qu'il en restera suffisament.
* ne pas compter les non compliant en stock, sauf s'il n'y a que ça. Peut-être mettre les non compliant entre () genre un 10(20)/30 comme ça visuellement, on sait qu'on en a des bons, et des pas bons, et même combien.
* Ce serait bien de pouvoir dire, pour finir cliquez sur générer le bon de commande et tous les items ci-dessus seront commandés automatiquement... Il ne s'agit pas du module achat, juste de générer la commande en PDF comme l'inventaire.
* Les médicaments devraient être comptés par boites et pas individuellement. Je sors une boite de paracétamol et pas 9 comprimés de paracétamol. (surtout, je ne remets pas une boite entammée...) Donc prise en charge du packaging, de la quantité réglementaire et du nombre de boites, ou grammes...
* Mettre en place une fonction "stock control". Qui permettrait par exemple d'afficher une case à cocher a chaque item, si checker et ok, on décoche la case, si on modifie quelque chose la case se décoche également. Ainsi on peut suivre qu'on a rien oublié de vérifier en faisant l'inventaire et même faire un historique des inventaires réalisés.

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
