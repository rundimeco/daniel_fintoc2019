import codecs
import re

def get_args():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-t", "--train", dest="train",
		  default = "shared_task_1.train.csv.json",
                  help="train data JSON", metavar="DATA")
  parser.add_option("-T", "--test", dest="test", 
		  default = "shared_task_1.test.csv.json",
                  help = "test data JSON")
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
                   help="min length, max length")
  parser.add_option("-s", "--sup",
                   dest="sup", default="2,100000",
                   help="min support, max support")
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
