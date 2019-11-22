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
from scipy import sparse
import json
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

def get_matrix_rstr(json_path):
  dic_json = open_json(json_path)
  texts = [infos["text_line"] for x, infos in dic_json.items()]
  rstr = Rstr_max()
  X = [] 
  for s in texts:
    rstr.add_str(s)
    X.append({})
  r = rstr.go()
  cpt_str=0
  l_str = []
  for (offset_end, nb), (l, start_plage) in r.items():
    ss = rstr.global_suffix[offset_end-l:offset_end]
    l_str.append(ss)
    set_occur = set()
    for o in range(start_plage, start_plage+nb) :
      id_text = rstr.idxString[rstr.res[o]]
      set_occur.add(id_text)
    if len(set_occur)>1:
      for id_text in set_occur:
        X[id_text].setdefault(cpt_str, 0)
        X[id_text][cpt_str]+=1
    cpt_str +=1
  return l_str, X 

def vector_rstr(infos, m_tokens):
  txt = infos["text_line"]
  vec = []
  for token in m_tokens:
    vec.append(txt.count(token))
  return sparse.csr_matrix(np.array(vec))


def prepare_data(json_path, m_tokens):
  dic_json = open_json(json_path)
  texts = [infos["text_line"] for x, infos in dic_json.items()]
  X, y , L_IDS = [], [], []
  for ID, infos in dic_json.items():
    X.append(vector_rstr(infos, m_tokens)) # X.append()
    y.append(infos["label"])
    L_IDS.append(ID)
  return X, y, L_IDS

def vectorize(options):
  if options.verbose==True:  print(options)
  # Création des ensembles de train et de test
  dic_out = {"train":{}, "test":{}}
  desc = {}
  matrix = {}
  m_tokens, matrix = pickle.load(open(options.matrix, 'rb'))
  X_train, y_train, IDs_train = prepare_data(json_path=options.train, m_tokens=m_tokens)
  X_test, y_test, IDs_test = prepare_data(json_path=options.test, m_tokens=m_tokens)

  """
  # On récupère les classifieurs à utiliser (ils sont instanciés dans la fonction get_liste_classif())
  liste_classif = get_liste_classif()
  # Cross-validation
  skf = StratifiedKFold(10, shuffle=False)
  # Info et dossier nécessaire à la suite
  dataset_name = format_name(options.train, options.test)
  mkdirs("results_final_rstr/%s/"%(dataset_name))

  # Pour chaque classifieur...
  for name_classif, OBJ in liste_classif:
    print("%s%s%s"%("-"*10,name_classif,"-"*10))
    config = "%s.txt"%(name_classif)
    out_name ="results_B_final/%s/%s"%(dataset_name, config)
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
  """
if __name__ == "__main__":    
	options = get_args_rstr() # Parse des arguments
	if options.mode == 'matrix_generation':
		m_tokens, matrix = get_matrix_rstr(options.train)
		pickle.dump((m_tokens, matrix), open(options.output_dir + 'matrix.pickle', 'wb'))
	else:
		vectorize(options) # Appel de la fonction principale avec les options demandées en ligne de commande
