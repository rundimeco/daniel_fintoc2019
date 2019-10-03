import codecs
import re, os, json

def get_args():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-o", "--output_dir", dest="output_dir",
		  default = "results_simple",
                  help="Output for prediction results", metavar="OUTPUT")
  parser.add_option("-t", "--train", dest="train",
		  default = "json_files/TITLE_train.csv.json",
                  help="train data folder", metavar="DATA")
  parser.add_option("-T", "--test", dest="test", 
		  default = "json_files/TITLE_test.csv.json",
                  help = "test data folder")
  parser.add_option("-v", "--verbose",
                   action="store_true", dest="verbose", default=False,
                   help="print status messages to stdout")
  parser.add_option("-F", "--force",
                   action="store_true", dest="force", default=False,
                   help="Force redoing already done experiments")
  parser.add_option("-f", "--freq",
                   action="store_true", dest="freq", default=False,
                   help="feature relative frequency")
  parser.add_option("-l", "--len",
                   dest="len", default="1,1",
                   help="min length, max length (character model)")
  parser.add_option("-s", "--sup",
                   dest="sup", default="2,100000",
                   help="min support, max support (character model)")
  (options, args) = parser.parse_args()
  return options

def get_args_BL():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-t", "--train", dest="train",
		  default = "json_files/TITLE_train.csv.json",
                  help="train data folder", metavar="DATA")
  parser.add_option("-T", "--test", dest="test", 
		  default = "json_files/TITLE_test.csv.json",
                  help = "test data folder")
  parser.add_option("-v", "--verbose",
                   action="store_true", dest="verbose", default=False,
                   help="print status messages to stdout")
  parser.add_option("-F", "--force",
                   action="store_true", dest="force", default=False,
                   help="Force redoing already done experiments")
  parser.add_option("-m", "--mode",
                   dest="mode", default="all",
                   help="Mode: from B1 to B6 (default: all)")
  (options, args) = parser.parse_args()
  return options

def effectif_from_list(liste):
  dic = {}
  for elem in liste:
    dic.setdefault(elem, 0)
    dic[elem]+=1
  return dic

def mkdirs(path):
  try:
    os.makedirs(path)
  except:
    pass

def get_class(path):
  elems = re.split("/", path)
  return elems[-2]

def open_utf8(path,l=False):
  f = codecs.open(path,'r','utf-8')
  if  l==True:
    out = f.readlines()
    out = [re.sub("\n|\r","",x) for x in out]
  else:
    out = f.read()
  f.close()
  return out

def write_utf8(path,out):
  w = codecs.open(path,'w','utf-8')
  w.write(out)
  w.close()


def format_output(IDs, pred):
  if "not_title" in pred:
    pred = ["0" if x=="not_title" else "1" for x in pred]
#    pred = ["1" for x in pred if x=="is_title"]
  paires = ["ID\tlabel"]
  IDs = [re.split("/", x)[-1] for x in IDs]
  paires += ["%s\t%s"%(IDs[i], pred[i]) for i in range(len(IDs))]
  out = "\n".join(paires)
  return out 

def format_name(train_name, test_name):
  train_name = re.split("/", train_name)[-1]
  test_name = re.split("/", test_name)[-1]
  return "%s--%s"%(train_name, test_name)

def open_json(path):
  f = open(path)
  data = json.load(f)
  f.close()
  return data

def get_score(y_test, y_pred):
  score = [0, 0]
  for i in range(len(y_test)):
    if(y_test[i]==y_pred[i]):
      score[0]+=1
    else:
      score[1]+=1
  return score[0]/(score[0]+score[1])
