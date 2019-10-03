from tools import *
import re, glob, os
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
import pickle

def get_stylo(chaine):
  liste_patts = [",", ";", "_", "-", "\(", "\)", "\.", "[A-Z]","[0-9]"]
  L = [len(re.findall(patt, chaine)) for patt in liste_patts]
  return L 

def get_liste_classif():
  return [
	["MNB", MultinomialNB()],
#	["MLP", MLPClassifier(solver='lbfgs', alpha=1e-5,
#	                     hidden_layer_sizes=(5, 2), random_state=1)],
	["DT10", DecisionTreeClassifier(max_depth = 10)], 
#	["Svm-C1L", svm.SVC(kernel='linear')] 
#	["GNB", GaussianNB()],
  ]

def vector_baseline(infos, mode):
  features_base = ["begins_with_numbering", "is_italic","is_all_caps", "begins_with_cap", "page_nb"]
  vec = [] 
  #B1:feat base, B2:base + longueur
  #B3:stylo, B4: stylo + base, B5:stylo+longueur 
  #B6:stylo+base+longueur 
  if mode!="B3" and mode !="B5":
    for feat in features_base:
      vec.append(int(infos[feat]))
  if mode =="B2" or mode=="B5" or mode =="B6":
    vec.append(len(infos["text_line"]))
  texte = infos["text_line"]
  if mode!="B1" and mode!="B2":
    stylos = get_stylo(texte)
    for feat_style in stylos:
      vec.append(feat_style)
  return vec
 
def prepare_data(json_path, mode):
#  settings = open_json("settings.json")#for tagging (deprecated)
  dic_json = open_json(json_path)

  X, y , L_IDS = [], [], []
  for ID, infos in dic_json.items():
    X.append(vector_baseline(infos, mode))
    y.append(infos["label"])
    L_IDS.append(ID)
  return X, y, L_IDS

def vectorize(options):
  if options.verbose==True:  print(options)
  liste_modes = ["B1", "B2", "B3", "B4", "B5", "B6"]
  if options.mode!="all":
    liste_modes = [options.mode]
  for mode in liste_modes:
    dic_out = {"train":{}, "test":{}}
    desc = {}

    X_train, y_train, IDs_train = prepare_data(options.train, mode)
    X_test, y_test, IDs_test = prepare_data(options.test, mode)
    liste_classif = get_liste_classif()
    skf = StratifiedKFold(10, shuffle=False)

    print("%s--mode: %s--%s"%("="*10, mode, "="*10))
    dataset_name = format_name(options.train, options.test)
    mkdirs("results_B_final/%s/"%(dataset_name))

    for name_classif, OBJ in liste_classif:
      print("%s%s%s"%("-"*10,name_classif,"-"*10))
      config = "%s__%s.txt"%(mode,name_classif)
      out_name ="results_B_final/%s/%s"%(dataset_name, config )
      if os.path.exists(out_name) and options.force==False:
        print("Already DONE")
        continue

      accuracy = np.mean(cv_score(OBJ, X_train,y=y_train, cv=skf, n_jobs=2))
      model = OBJ.fit(X_train, y_train)
      y_pred = model.predict(X_test)
      
      model_name = "models/%s.sav"%config
      pickle.dump(model, open(model_name, 'wb')) 

      score_test = get_score(y_test, y_pred)
      if options.verbose==True: print(out_name)
      y_pred_out = format_output(IDs_test, y_pred)
      write_utf8(out_name, (y_pred_out))
      print("Acc. (cross-valid)\t: %f"%accuracy)
      print("Acc. (test)\t\t: %f"%(score_test))

if __name__=="__main__":    
  options = get_args_BL()
  vectorize(options)
