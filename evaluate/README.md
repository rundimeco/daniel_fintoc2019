parse_json_ref_title_detection.py
=================================

Ce programme permet uniquement de transformer un fichier .json sous forme de résultat d'un modèle, comme:
	instance1 	label1
	...			...
	instanceN	labelN

Dans le Terminal, il suffit d'entrer :
```python3 parse_json_ref_title_detection.py chemin/vers/json/file```

evaluate.py
===========

Pour utiliser le programme evaluate.py, il faut disposer du :
- $REF$ : chemin d'accès au fichier contenant la référence ;
- $TEST_DIR$ : chemin d'accès au répertoire contenant tous les résultats des modèles à tester.

Dans le Terminal, il suffit d'entrer :
```python3 evaluate.py $REF$ $TEST_DIR$```

Ensuite, on dispose des fichiers suivants (qu'il convient de renommer et de ranger) :
- performances_models.tsv : contient les performances des modèles à tester (contenu dans $TEST_DIR$...) face à la référence $REF$
- FN_**** --> ces fichiers contiennent toutes les instances faux négatifs 
- FN_all_models --> ce fichier contient toutes les instances faux négatifs pour tous les modèles (aucun modèle n'a réussi à l'étiqueter en Vrai positif).

generate_venn.py
================

Pour utiliser le programme evaluate.py, il faut disposer de :
- nombre de dimensions souhaitées dans pour le diagramme de Venn ;
- les chemins d'accès aux modèles contenant les résultats des modèles (instance  label)
- les noms des modèles à afficher sur le diagramme 
- le caracètre de séparation des instances dans les fichiers contenant les résultats des modèles
- le label que l'on souhaite représenter

Par exemple : ```python3 generate_venn.py "./models/m1.txt,./models/m2.txt,./models/m3.txt" "Model 1, Model 2, Model 3" \\t 1```
(Ici, le caractère de séparation est une tabulation et le label est "1".)