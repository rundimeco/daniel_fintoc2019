Description des éléments présents dans le dossier
=================================================

- ./test_set_with_labels/ : il s’agit du jeu de test labellisé par les modèles (et la référence)
- ./res_evaluation/ : résultat des évaluations (selon les méthodes) :
	- les faux négatifs par modèle ;
	- les faux négatifs de tous les modèles ;
	- un tableau rassemblant les précision, rappel et f-mesure (un tableau = une méthode)
- ./venn/ : images de certains diagrammes de Venn
- parse_json_ref_title_detection.py —> script qui permet de transformer le json rassemblant le jeu de test labellisé dans un format similaire aux sorties de tes modèles (instance_id  tabulation  label)
- evaluate.py —> script qui permet de générer les résultats rangés dans ./res_evaluation/ (pour le lancer : voir ci-après)
- generate_venn.py —> script qui permet de faire des diagrammes de Venn (de 3 à 6 dimensions) (pour le lancer : voir ci-après)
- venn.py —> script pour faire à proprement les diagrammes de Venn, trouvé ici : https://github.com/tctianchi/pyvenn/blob/master/venn.py



parse_json_ref_title_detection.py
=================================

Ce programme permet uniquement de transformer un fichier .json sous forme de résultat d'un modèle, comme:

	instance1 	label1

	...		...

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
- le nombre de dimensions du diagramme (= le nombre de cercles)

Par exemple : ```python3 generate_venn.py "./models/m1.txt,./models/m2.txt,./models/m3.txt" "Model 1, Model 2, Model 3" \\t 1 3```
(Ici, le caractère de séparation est une tabulation, le label est "1" et le diagramme comporte 3 dimensions.)

generate_upset_plot.py
======================

Pour utiliser le programme generate_upset_plot.py, il suffit de disposer de :
- les chemins d'accès aux modèles contenant les résultats des modèles (instance  label)
- le caracètre de séparation des instances dans les fichiers contenant les résultats des modèles
- l'indice de l'identifiant des instances dans les fichiers contenant les résultats modèles
- l'indice des labels dans les fichiers contenant les résultats modèles

Par exemple : ```python3 generate_upset_plot.py "model1.txt,model2.txt,modele3.txt,reference.txt" \\t 0 1``` (Ici, le caractère de séparation est une tabulation, l'indice des instances est "0" et l'indice des labels est "1"). 