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

def get_liste_classif():
  return [
	["MNB", MultinomialNB()],
#	["MLP", MLPClassifier(solver='lbfgs', alpha=1e-5,
#	                     hidden_layer_sizes=(5, 2), random_state=1)],
#	["DT10", DecisionTreeClassifier(max_depth = 10)], 
#	["GNB", GaussianNB()],
#	["SVM-OVR",OneVsRestClassifier(LinearSVC(random_state=0, max_iter=2000))],
#	["Svm-C1L", svm.SVC(kernel='linear')] 
  ]
def get_desc(chaine, options, dic_desc, test = False):
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
  if test==True:#missing features in test data
    for num_desc in dic_desc.values():
      if num_desc not in X[0]:
        X[0][num_desc] = 0
  dictvectorizer = DictVectorizer()
  X = dictvectorizer.fit_transform(X)
  return X, y, dic_desc, data.keys()

def vectorize(options):
  if options.freq==True: freq_param = "_rel-freq_"
  else: 		 freq_param = "_abs-freq_"
  dataset_name = re.sub("/", "__", options.train+"--"+options.test)
  dic_out = {"train":{}, "test":{}}
  if options.verbose==True:
    print(options)
  desc = {}
  liste_classif_base = get_liste_classif()
  liste_classif = []
  for name_classif, classif in liste_classif_base:
    out_name = "results_simple/%s/out_simple_len=%s_%s%s.txt"%(dataset_name, options.len, name_classif, freq_param)
    if os.path.exists(out_name) and options.force==False:
      print("Already DONE : %s"%out_name)
    else:
      liste_classif.append([name_classif, classif])
  if len(liste_classif)==0:
    exit()
#  liste_train = glob.glob(options.train+"*/*")
#  liste_test = glob.glob(options.test+"*/*")
  X_train, y_train, desc, _ = prepare_data(options.train,{}, options, False)
  X_test, y_test, desc, liste_test = prepare_data(options.test, desc, options, True)

  skf = StratifiedKFold(10, shuffle=False)
  for name_classif, OBJ in liste_classif:
    out_name = "results_simple/%s/out_simple_len=%s_%s%s.txt"%(dataset_name, options.len, name_classif, freq_param)
    try:
      os.makedirs("results_simple/%s/"%(dataset_name))
    except:
      pass

    print("-"*20)
    print(name_classif)
    RES = cv_score(OBJ, X_train,y=y_train, cv=skf, n_jobs=2)
    print(RES)
    accuracy = np.mean(RES)
    y_pred = OBJ.fit(X_train, y_train).predict(X_test)
    
    score = [0, 0]
    for i in range(len(y_test)):
      if(y_test[i]==y_pred[i]):
        score[0]+=1
      else:
        score[1]+=1
    try:
      os.makedirs("results_simple/%s"%dataset_name)
    except:
      pass
    sorted_y_pred = format_output(liste_test, y_pred)
    if options.verbose==True: print(out_name)
    write_utf8(out_name, sorted_y_pred)
    print("Acc. (cross-valid)\t: %f"%accuracy)
    print("Acc. (test)\t\t: %f"%(score[0]/(score[0]+score[1])))
    
options = get_args()
vectorize(options)
