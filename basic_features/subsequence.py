import sys
from tools_karkkainen_sanders import *
from rstr_max import *

def get_rstr(strings, is_title):
  rstr = Rstr_max()
  for s in strings:
      rstr.add_str(s)
  r = rstr.go()
  out = {}
  cpt=0
  for (offset_end, nb), (l, start_plage) in r.items():
      cpt+=1
      ss = rstr.global_suffix[offset_end-l:offset_end]
      s_occur = set()
      for o in range(start_plage, start_plage+nb) :
          s_occur.add(rstr.idxString[rstr.res[o]])
      for ID in s_occur:
        out.setdefault(ID, {"chaine": "", "intersections":set()})
        if len(ss)>len(out[ID]["chaine"]):
          out[ID]["chaine"] = ss
          out[ID]["intersections"] = s_occur
      if cpt==1000:break
  toto = []
  for ID, infos in out.items():
    ratio = len(infos["chaine"])/len(strings[ID])
#    if ratio >0.5 and len(infos["intersections"])==2 and len(infos["chaine"])<100:
    if 1:
      toto.append([is_title[ID], ratio, ID, strings[ID], infos])
  for titi in sorted(toto):
    print(titi)
import json

json_path = sys_argv[1]
f = open(json_path)
instances = json.load(f)
f.close()

xml_files = set([instances[x]["xmlfile"] for x in instances])
for fic in xml_files:
  texts = [infos for x, infos in instances.items() if instances[x]["xmlfile"] == fic]
  strings = [infos["text_line"] for infos in texts]
  is_title = [infos["label"] for infos in texts]
  get_rstr(strings, is_title)
