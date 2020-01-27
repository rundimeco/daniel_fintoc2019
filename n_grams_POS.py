from tools import *
import re, glob, os, sys 
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
import json
import numpy as np
import spacy # python3 -m spacy download en_core_web_sm
import pickle

uni_pos = ['SYM', 'PUNCT', 'ADJ', 'CCONJ', 'NUM', 'DET', 'PRON', 'ADP', 'VERB', 'NOUN', 'PROPN', 'PART', 'ADV', 'INTJ', 'X', 'SPACE']

def get_liste_classif():
  return [
	["MNB", MultinomialNB()],
	["DT10", DecisionTreeClassifier(max_depth = 10)], 
  ]

def vector_ngrams_pos(options, nlp, text):
	doc = nlp(text)
	text_pos = [token.pos_ for token in nlp(text)]
	vec = []
	for pos in uni_pos:
		if pos in text_pos:
			if options.rel == True:
				vec.append(text_pos.count(pos)/len(uni_pos))
			else:
				vec.append(text_pos.count(pos))
		else:
			vec.append(0)
	return vec


def prepare_data(options, json_path):
	#  settings = open_json("settings.json")#for tagging (deprecated)
	dic_json = open_json(json_path)
	instances = dic_json
	X, y , L_IDS = [], [], []
	nlp = spacy.load("en_core_web_sm")
	for ID, infos in dic_json.items():
		X.append(vector_ngrams_pos(options, nlp, infos["text_line"]))
		y.append(infos["label"])
		L_IDS.append(ID)
	return X, y, L_IDS

def vectorize(options):
	if options.verbose==True:  print(options)

	# Pour chaque type de modèle à apprendre et tester...
	# Création des ensembles de train et de test
	dic_out = {"train":{}, "test":{}}
	desc = {}
	X_train, y_train, IDs_train = prepare_data(options, options.train)
	X_test, y_test, IDs_test = prepare_data(options, options.test)

	# On récupère les classifieurs à utiliser (ils sont instanciés dans la fonction get_liste_classif())
	liste_classif = get_liste_classif()
	# Cross-validation
	skf = StratifiedKFold(10, shuffle=False)
	# Info et dossier nécessaire à la suite
	dataset_name = format_name(options.train, options.test)
	mkdirs("results_POS_final/%s/"%(dataset_name))

	# Pour chaque classifieur...
	for name_classif, OBJ in liste_classif:
		print("%s%s%s"%("-"*10,name_classif,"-"*10))
		config = "%s__%s"%('n_grams_POS_',name_classif)
		if options.rel == True:
			config += '__freqRel.txt'
		else:
			config += '.txt'
		out_name ="results_POS_final/%s/%s"%(dataset_name, config)
		if os.path.exists(out_name) and options.force==False: # Si on a déjà fait le travail (et qu'on n'a pas -f en argument), on passe
			print("Already DONE")
			continue

		# Accuracy sur l'ensemble TRAIN en cross validation
		accuracy = np.mean(cv_score(OBJ, X_train,y=y_train, cv=skf, n_jobs=2))

		# Apprentissage du classifieur sur le TRAIN et métrique sur le TEST
		model = OBJ.fit(X_train, y_train) # apprentissage
		y_pred = model.predict(X_test) # prédiction sur le test
		model_name = "models/%s.sav"%config
		pickle.dump(model, open(model_name, 'wb')) # Sauvegarde du modèle
		# Récupération des performances
		score_test = get_score(y_test, y_pred)
		if options.verbose==True: print(out_name)
		y_pred_out = format_output(IDs_test, y_pred)

		# Ecriture et affichage des performances du modèle
		write_utf8(out_name, (y_pred_out))
		print("Acc. (cross-valid)\t: %f"%accuracy)
		print("Acc. (test)\t\t: %f"%(score_test))

if __name__ == "__main__":    
	options = get_args_ngrams_pos() # Parse des arguments
	vectorize(options) # Appel de la fonction principale avec les options demandées en ligne de commande
