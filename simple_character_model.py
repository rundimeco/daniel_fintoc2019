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

def get_liste_classif():
  return [
	["MNB", MultinomialNB()],
#	["MLP", MLPClassifier(solver='lbfgs', alpha=1e-5,
#	                     hidden_layer_sizes=(5, 2), random_state=1)],
	["DT10", DecisionTreeClassifier(max_depth = 10)], 
#	["GNB", GaussianNB()],
#	["SVM-OVR",OneVsRestClassifier(LinearSVC(random_state=0, max_iter=2000))],
#	["Svm-C1L", svm.SVC(kernel='linear')] 
  ]
def get_desc(chaine, options, dic_desc, test = False):
  chaine = "$$%s^^"%chaine
  m, M = [int(x) for x in re.split(",", options.len)]
  occs = {}
  for deb in range(len(chaine)):
    for i in range(m, M+1):
      desc = chaine[deb:deb+i]
      if test==True:
        if desc not in dic_desc:
          continue
      else:
        dic_desc.setdefault(desc, len(dic_desc))
      occs.setdefault(dic_desc[desc], 0)
      if options.freq==False:
        occs[dic_desc[desc]]+=1
      else:
        occs[dic_desc[desc]]+=1/float(len(chaine))
  return occs,dic_desc

def prepare_data(path_data, dic_desc, options, test=False):
  X, y = [], []
  f = open(path_data)
  data = json.load(f)
  f.close()
  for cle, infos in data.items():
    if test==True:
      classe="no_title"
    else:
      classe = infos["label"]
    occs, dic_desc = get_desc(infos["text_line"], options, dic_desc, test)
    X.append(occs)
    y.append(classe)
  if test==True:#compléter les traits absents dans le test
    for num_desc in dic_desc.values():
      if num_desc not in X[0]:
        X[0][num_desc] = 0
  dictvectorizer = DictVectorizer()
  X = dictvectorizer.fit_transform(X)
  return X, y, dic_desc, data.keys()

def filter_classif_done(options, freq_param, dataset_name):
  liste_classif_base = get_liste_classif()
  liste_classif = []
  for name_classif, classif in liste_classif_base:
    config ="len=%s_%s%s.txt"%(options.len, name_classif, freq_param)
    out_name = "%s/%s/%s"%(options.output_dir, dataset_name, config)
    if os.path.exists(out_name) and options.force==False:
      print("Already DONE : %s"%out_name)
    else:
      liste_classif.append([name_classif, classif])
  return liste_classif

def vectorize(options):
  freq_param = "_rel-freq_" if options.freq==True else "_abs-freq_"
  dataset_name = format_name(options.train,options.test)
  dic_out = {"train":{}, "test":{}}
  if options.verbose==True:  print(options)
  desc = {}
  liste_classif = filter_classif_done(options, freq_param, dataset_name)
  if len(liste_classif)==0:
    print("No experiments to perform, check %s"%options.output_dir)
    exit()
  X_train, y_train, desc, _ = prepare_data(options.train,{}, options, False)
  X_test,y_test,desc,liste_test =prepare_data(options.test, desc, options, True)

  skf = StratifiedKFold(10, shuffle=False)
  for name_classif, OBJ in liste_classif:
    config ="len=%s_%s%s.txt"%(options.len, name_classif, freq_param)
    out_name = "%s/%s/%s"%(options.output_dir, dataset_name, config)
    mkdirs("%s/%s"%(options.output_dir, dataset_name))

    print("%s%s%s"%("-"*10,name_classif,"-"*10))
    RES = cv_score(OBJ, X_train,y=y_train, cv=skf, n_jobs=2)
    print(RES)
    accuracy = np.mean(RES)
    model = OBJ.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    model_name = "models/%s.sav"%config
    pickle.dump(model, open(model_name, 'wb')) 

    score_test = get_score(y_test, y_pred)
    
    sorted_y_pred = format_output(liste_test, y_pred)
    if options.verbose==True: print(out_name)
    write_utf8(out_name, sorted_y_pred)
    print("Acc. (cross-valid)\t: %f"%accuracy)
    print("Acc. (test)\t\t: %f"%(score_test))

if __name__=="__main__":    
  options = get_args()
  vectorize(options)
