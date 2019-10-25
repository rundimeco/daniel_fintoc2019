import sys, os
import re, json

data_csv = sys.argv[1]

f = open(data_csv)
lines = f.readlines()
f.close()

dic = {}

attributes = ["text_line", "begins_with_numbering", "is_bold", "is_italic", "is_all_caps", "begins_with_cap", "xmlfile", "page_nb", "label"]
for cpt, l in enumerate(lines[1:]):
  elems = re.split("\t", re.sub("\n", "", l))
  infos = {attributes[i]: elems[i] for i in range(len(attributes))}
  dic[cpt] = infos
w = open("%s.json"%data_csv, "w")
w.write(json.dumps(dic, indent = 2))
w.close()
