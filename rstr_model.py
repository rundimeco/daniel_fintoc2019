from tools import *
import re, glob, os, sys
sys.path.append('./rstr_max/')
from rstr_max import Rstr_max # Objet contenu dans le fichier rstr_max.py contenu dans le dossier sys.path.append('./rstr_max/')
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import cross_val_score as cv_score
from sklearn.model_selection import StratifiedKFold 
from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier 
from sklearn import neighbors
from sklearn.neural_network import MLPClassifier
from numpy import array
import scipy.sparse as sp
import json
import io
import numpy as np
import pickle

def get_liste_classif():
	return [
	["MNB", MultinomialNB()],
# ["MLP", MLPClassifier(solver='lbfgs', alpha=1e-5,
#                      hidden_layer_sizes=(5, 2), random_state=1)],
	["DT10", DecisionTreeClassifier(max_depth = 10)], 
# ["Svm-C1L", svm.SVC(kernel='linear')] 
# ["GNB", GaussianNB()],
	]

def get_matrix_rstr(options, dic_json, desc_arg=None):
	texts = [infos["text_line"] for x, infos in dic_json.items()]
	
	rstr = Rstr_max()
	X = [] 
	for s in texts:
  		rstr.add_str(s)
  		X.append({})
	r = rstr.go()

	cpt_str = 0
	desc = []
	for (offset_end, nb), (l, start_plage) in r.items():
		ss = rstr.global_suffix[offset_end-l:offset_end]
		list_occur = []
		for o in range(start_plage, start_plage+nb):
			id_text = rstr.idxString[rstr.res[o]]
			list_occur.append(id_text)
		set_occur = set(list_occur)
		# Ici, il y a un souci dans les dimensions puisque tous les descripteurs ne sont pas
		# forcément présents. Donc dans certains cas on n'a rien pour une instance donnée. 
		if desc_arg is not None and ss not in desc_arg:  # Test
			continue
		if len(set_occur) > 1:
			if len(ss) < int(options.lenmax) and len(set_occur) < float(options.supportmax)*len(texts):
				for id_text in list_occur:
					X[id_text].setdefault(cpt_str, 0)
					X[id_text][cpt_str] += 1
				if desc_arg is None: # corpus train = on ajoute le descripteur
					desc.append(ss)
				cpt_str += 1

	# Ajout d'une instance virtuelle pour garantir l'homogénéite dans les dimensions des matrices de train et test
	if desc_arg is None: # Train
		descriptors = desc
	else: # test
		descriptors = desc_arg
	dic = {}
	for d in descriptors:
		dic[descriptors.index(d)] = 1
	X.append(dic)

	# --------------------> Ici qu'il faut intervenir pour changer les valeurs de la matrice en tf-idf ou Okapi.

	return desc, X


def prepare_data(options, desc=None):
	if desc is None: # Corpus de train
		dic_json = open_json(options.train)
		desc, matrix = get_matrix_rstr(options, dic_json)
	else: # Corpus de test
		dic_json = open_json(options.test)
		_, matrix = get_matrix_rstr(options, dic_json, desc)

	v = DictVectorizer()
	X = v.fit_transform(matrix)
	y, L_IDS = [], []
	for ID, infos in dic_json.items():
		y.append(infos["label"])
		L_IDS.append(ID)
	
	y.append('0')
	L_IDS.append('-1')

	return X, y, L_IDS, desc

def vectorize(options):
	if options.verbose==True:  
		cprint(options)
	# Création des ensembles de train et de test
	dic_out = {"train":{}, "test":{}}

	X_train, y_train, IDs_train, desc_t = prepare_data(options)
	X_test, y_test, IDs_test, _ = prepare_data(options, desc=desc_t)




	# On récupère les classifieurs à utiliser (ils sont instanciés dans la fonction get_liste_classif())
	liste_classif = get_liste_classif()
	# Cross-validation
	skf = StratifiedKFold(10, shuffle=False)
	# Info et dossier nécessaire à la suite
	dataset_name = format_name_rstr(options)
	mkdirs("results_final_rstr/%s/"%(dataset_name))

	# Pour chaque classifieur...
	for name_classif, OBJ in liste_classif:
		print("%s%s%s"%("-"*10,name_classif,"-"*10))

		model_name = name_classif + '__len=' + options.lenmax + '_sup=' + options.supportmax + '.txt' 
		path_model = options.output_dir + 'models/' + model_name
		path_test_set = options.output_dir + 'data/' + model_name
		
		if os.path.exists(path_model) and options.force==False: # Si on a déjà fait le travail (et qu'on n'a pas -f en argument), on passe
			print("Already DONE")
			continue

 		# 1. Cross-valisation
		accuracy = np.mean(cv_score(OBJ, X_train, y=y_train, cv=skf, n_jobs=2))

		# 2. Train et Test sets
		model = OBJ.fit(X_train, y_train) # apprentissage
		y_pred = model.predict(X_test) # prédiction sur le test
		# Récupération des performances
		score_test = get_score(y_test, y_pred)
		if options.verbose==True: 
			print(out_name)
		y_pred_out = format_output(IDs_test, y_pred)

		# Ecriture et affichage des performances du modèle
		file_res = io.open(path_test_set, mode='w', encoding='utf-8')
		file_res.write(y_pred_out)
		file_res.close()

		pickle.dump(model, open(path_model, 'wb')) # Sauvegarde du modèle

		print("Acc. (cross-valid)\t: %f"%accuracy)
		print("Acc. (test)\t\t: %f"%(score_test))

if __name__ == "__main__":    
	options = get_args_rstr() # Parse des arguments
	vectorize(options) # Appel de la fonction principale avec les options demandées en ligne de commande



# A FAIRE
# Fichier d'options + faire varier les options 
#   -> récupérer le modèle et bien gérer son noms pour pas de confusion
#   -> récupérer le y_pred (pour calcul plus tard des matrices de confusion etc.)
# 

