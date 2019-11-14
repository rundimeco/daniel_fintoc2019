import sys
import io
import json
from tools_karkkainen_sanders import *
from rstr_max import *
from sklearn.metrics import precision_recall_fscore_support 

def Instances_per_doc(dic_json):
  """Cette fonction permet de retourner un dictionnaire tel que :
    - clef : nom du fichier xml
    - valeurs : dictionnaire
                  - clef : ID de l'instance
                  - valeurs : infos
  """
  dic = {}
  for ID, infos in dic_json.items():
    if infos["xmlfile"] not in dic.keys():
      dic[infos["xmlfile"]] = {ID: infos}
    else:
      dic[infos["xmlfile"]].update({ID: infos})
  return dic

def get_rstr(strings):
  """Cette fonction permet de retourner un dictionnaire contenant tous les rstr max trouvés dans les chaines de 
  caractères contenues dans la liste $strings.
  Le dictionnaire est tel que :
    - clef : chaine (chaine totale de l'instance)
    - valeurs : dictionnaire
                - clef : sous chaine rstr_max
                - valeur : set dans id des autres instances dans lesquelles on retrouve la sous chaine considérée
  """
  rstr = Rstr_max() # Création de l'objet permettant la recherche des sous-séquences maximales partagées
  for s in strings: # Ajouts des chaines dans l'objet Rstr_max()
      rstr.add_str(s)
  r = rstr.go() 
  
  res = {} # Structure de données dans laquelle on va mettre toutes les sous-chaines trouvées et les ids des chaines 
           # dans lesquelles la sous-chaine est trouvée
           # clef = chaines dans $strings
           # valeur = dico dans lequel clef = sous-chaine qui y est présente et valeur = liste des id des chaines de strings ou sous-chaine est
  for s in strings:
    res[s] = {}
  for (offset_end, nb), (l, start_plage) in r.items():
    # offset_end : indice du caractère de fin de la sous-chaine dans la concaténation de toutes les chaines dans $strings
    # nb : nombre de fois où la sous-chaine est répétées dans la concaténation de toutes les chaines dans $strings
    # l : longueur de la sous-chaine
    # 
    # AFFICHAGE DES VALEURS DE (offset_end, nb), (l, start_plage)
    # print(str(offset_end-l) + ' : ' +str(offset_end), end=' >> ')
    # ss = rstr.global_suffix[offset_end-l:offset_end]
    # print(ss, end='  :  ')
    # for v in [offset_end, nb, l, start_plage]:
    #   print(v, end=' / ')
    # print('\n')

    # 1. Récupération de la sous-chaine détectée
    ss = rstr.global_suffix[offset_end-l:offset_end]

    # 2. On va mettre dans $string_id les indices des chaines dans lesquelles on trouve la sous-chaine $ss
    string_ids = set()
    for o in range(start_plage, start_plage+nb) :
        string_ids.add(rstr.idxString[rstr.res[o]])

    # 3. Ajout des informations sur cette sous-chaine à la structure de données $res
    for ID in string_ids: 
      res[strings[ID]].update({ss: string_ids})

  return res


def Annotate_instances(file_name, dic_json, dic_rstr):
  """Cette fonction permet d'annoter un corpus selon LA SEULE méthode rstr_max.
  """
  outFile = io.open(file_name+'.txt', mode='w', encoding='utf-8') # Ouverture du flux d'écriture
  outFile.write("ID\tlabel\n") # On écrit l'en-tête
  for x, infos in dic_json.items(): # Pour chaque instance contenu dans le corpus à annoter
    string = infos["text_line"]
    doc = infos["xmlfile"]
    id_net = x.split('/')[-1]
    outFile.write(id_net + '\t') # On écrit l'id de l'instance
    flag_repeated = False # Booléen à Vrai si la condition est respectée (condition = il existe un segment répété ailleurs dans le document)
    for ss, ensemble in dic_rstr[doc][string].items():
      if len(ensemble) == 2 and len(string)/len(ss)>0.6: # Si un sous segment est répété 2 ailleurs dans le document + ration=0.6 => ok
        flag_repeated = True
    if flag_repeated == True: # Ecriture du label
      outFile.write("1\n") 
    else:
      outFile.write("0\n")
  outFile.close()

if __name__ == "__main__": 
  json_path = sys.argv[1]
  f = open(json_path)
  dic_json = json.load(f)
  f.close()

  xml_files = set([dic_json[x]["xmlfile"] for x in dic_json])
  dic_rstr = {}
  for fic in xml_files:
    strings = [infos["text_line"] for x, infos in dic_json.items() if dic_json[x]["xmlfile"] == fic]
    labels = [infos["label"] for x, infos in dic_json.items() if dic_json[x]["xmlfile"] == fic]
    res_rstr = get_rstr(strings)
    dic_rstr[fic] = res_rstr

  Annotate_instances(file_name=json_path.split('.')[0], dic_json=dic_json, dic_rstr=dic_rstr)




