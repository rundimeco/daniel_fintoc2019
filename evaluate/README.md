parse_json_ref_title_detection.py
=================================

Ce programme permet uniquement de transformer un fichier json sous forme de résultat d'un modèle, comme:
	instance 	label

Dans le terminal, il suffit d'entrer :
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