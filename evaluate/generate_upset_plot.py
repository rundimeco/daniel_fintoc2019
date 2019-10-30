import sys
import io
import itertools
from upsetplot import plot
from upsetplot import generate_counts
from upsetplot import from_memberships
from matplotlib import pyplot as plt

def AddModelResults(dic, file_name, sep, id_col, label_col):
	"""A partir d'un nom de fichier, on charge un dico comme :
	clef=id_instance : valeur =dico (clef=model_name, valeur=titre ou non titre)
	"""
	file = io.open(file_name, mode='r', encoding='utf-8')
	line = file.readline()
	while line != '':
		if 'ID' not in line: # On saute la première ligne
			id = line.strip().split(sep)[id_col]
			label = line.strip().split(sep)[label_col]
			if id in dic.keys():
				if file_name not in dic[id].keys():
					dic[id][file_name] = label
			else:
				dic[id] = {}
				dic[id][file_name] = label
		line = file.readline()
	return dic

def GetModelsNames(results):
	"""Cette fonction renvoie tous les noms de modèles qu'on a reçu. 
	"""
	models_names = [] # Initialisation de la liste qui contiendra tous les noms de modèles
	for instance in results.keys():
		for model_name in results[instance].keys():
			if model_name not in models_names: 
				models_names.append(model_name)
	return models_names

def generate_upset_plot(results, label):
	"""Cette fonction permet d'afficher le upset plot.
	:param: results: dictionnaire dans lequel les résultats des modèles sont stockés
	:param: label: string, nom de l'étiquette à laquelle on s'intéresse
	"""
	models_names = GetModelsNames(results) # On récupère tous les noms des modèles de l'étude
	somme = {} # Génération de toutes les combinaisons entre modèles 
	for p in itertools.chain(*(itertools.combinations(models_names, long) for long in range(1, 4))):
		somme[p] = 0

	# Ici, on compte, pour chaque combinaison, combien d'instances ont la propriété d'appartenir à l'ensemble
	# décrit par la combinaison
	for comb in somme.keys():
		models_to_have = list(comb)
		for instance in results.keys():
			flag_ok = True
			for model in models_names:
				# Si le modèle courant fait partie de ceux attendus et que l'étiquette donnée n'est pas bonne, NON
				if model in models_to_have and results[instance][model] != label:
					flag_ok = False
				# Si le modèle courant ne fait pas partie de ceux attendus mais que l'étiquette donnée est bonne, NON
				if model not in models_to_have and results[instance][model] == label:
					flag_ok = False
			if flag_ok == True:
				somme[comb] += 1
	c, d = ([], [])
	for comb in somme.keys(): # Nettoyage des noms de modèles et initialisation des attributs de l'objet from_memberships
		comb_net = []
		for cc in list(comb):
			comb_net.append(cc.split('/')[-1].replace('.txt', ''))
		c.append(comb_net)
		d.append(somme[comb])
	# Réalisation de l'upset plot
	diagram = from_memberships(c, data=d)
	plot(diagram)
	plt.show()


if __name__ == "__main__":
	# Ceci est un exemple d'appel de la fonction generate_upset_plot.
	# Il faut mettre dans le Terminal les chemins vers les fichiers contenant les résultats des modèles 
	# pour que sys.argv[1], sys.argv[2]... les captent bien.

	files = [file for file in sys.argv[1].replace('"', '').split(',')] # Chargement des noms de fichiers
	if 't' not in sys.argv[2]: # Chargement du séparateur, problème avec la tabulation résolue ainsi
		sep = sys.argv[2]
	else:
		sep = '\t'
	id_col = int(sys.argv[3]) # Chargement du numéro de colonne de l'identifiant des instances
	label_col = int(sys.argv[4]) # Chargelent du numéro de colonne de l'identifiant des labels

	# On récupère dans une même structure de données les résultats des modèles
	# instance:
	#	model1: 	label1
	#	model2: 	label2
	results = {} 
	for f in files:
		results = AddModelResults(dic=results, file_name=f, sep=sep, id_col=id_col, label_col=label_col)

	# Appel de la fonction générant le upset plot
	generate_upset_plot(results, label='1')










