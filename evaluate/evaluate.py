import sys
import csv
import io
import os
from sklearn.metrics import precision_recall_fscore_support 

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

def GetModelPredictions(results, model_name):
	"""Cette fonction renvoie sous forme de liste toutes les prédictions associées à un modèle donné. 
	"""
	predictions = []
	for instance in results.keys():
		for model in results[instance].keys():
			if model == model_name:
				predictions.append(results[instance][model])
	return predictions

def Get_P_R_Fm(results, ref_name, labels):
	"""Cette fonction permet d'avoir toutes les performances des modèles à évaluer (utilisation de sklearn.metrics).
	"""
	performances = {} # Structure de données qui contiendra toutes les performances

	models_names = GetModelsNames(results) # On récupère les noms des modèles
	ref = GetModelPredictions(results, ref_name)

	# Pour tous les modèles à tester
	for model_name in models_names:
		if model_name != ref_name: # On ne calcule pas les perf de la ref sur la ref.......
			test = GetModelPredictions(results, model_name)
			res = precision_recall_fscore_support(ref, test, average=None, labels=labels)
			performances[model_name] = {}
			for i in range(0, len(labels)):
				performances[model_name][labels[i]] = [res[0][i], res[1][i], res[2][i], res[3][i]] # Rappel, Précision, F-mesure, Nb occurences dans ref

	return performances

def Print_P_R_Fm(results, ref_name, labels):
	performances = Get_P_R_Fm(results, ref_name, labels) # On récupère les performances
	print('Etiquette\tNb Occurences\tPrécision\tRappel\tF-mesure')
	# Pour tous les modèles à tester
	for model_name in performances:
		print('-------> ' + model_name)
		for label in performances[model_name].keys():
			perf = performances[model_name][label]
			print(label + '\t' + str(perf[3]) + '\t' + str(perf[0]) + '\t' + str(perf[1]) + '\t' + str(perf[2]))

def Write_P_R_Fm(outFile_name, results, ref_name, labels):
	"""Cette procédure permet d'écrire un tableau avec les performances de tous les modèles qu'on veut évaluer.
	"""
	performances = Get_P_R_Fm(results, ref_name, labels) # On récupère les performances
	with open(outFile_name, 'wt') as out_file:
	    tsv_writer = csv.writer(out_file, delimiter='\t')
	    tsv_writer.writerow(['Modèles', 'Étiquettes', 'Nombre d\'occurences', 'Précision', 'Rappel', 'F-mesure'])
	    for model_name in performances.keys():
	    	for label in performances[model_name].keys():
	    		perf = performances[model_name][label]
	    		tsv_writer.writerow([model_name.split('/')[-1].replace('.txt', ''), label, str(perf[3]), str(perf[0]), str(perf[1]), str(perf[2])])
	out_file.close()

def Write_FN(results, ref_name):
	"""Cette procédure crée, pour chaque modèle test, un fichier dans lequel les instances qui ont été des faux négatifs
	sont écrites. On crée aussi un fichier dans lequel les instances qui sont toujours des faux négatifs (peu importe les
	modèles) sont recensées.
	"""
	models_names = GetModelsNames(results)

	# Pour chaque modèle, on crée un fichier dans lequel on recense tous les faux négatifs
	for model_name in models_names: # Pour tous les modèles
		if model_name != ref_name:
			outFile = io.open(model_name.split('/')[-1].replace('.txt', '_FN.txt'), mode='w', encoding='utf-8') # On crée un outFile dans lequel on met tous les faux négatifs
			for instance in results.keys(): # Pour toutes les instances
				for model in results[instance].keys(): # On parcourt les modèles
					if model == model_name: # Si jamais on est dans le modèle qui nous intéresse
						if results[instance][ref_name] == '1' and results[instance][model_name] == '0':
							outFile.write(instance + '\n')
			outFile.close()
	# On écrit un fichier dans lequel on recence toutes les instances qui ont été étiquettées en faux négatifs.
	outFile = io.open('FN_all_models.txt', mode='w', encoding='utf-8')
	for instance in results.keys():
		if results[instance][ref_name] == '1':
			flag_title_detected = False # Booléen qu'on mettre à True si jamais un des modeles arrive à le détecter comme Titre
			for model in results[instance].keys(): # On parcourt les modeles
				if model != ref_name and results[instance][model] == '1': # Si jamais un des modèles trouve que c'est un titre
					flag_title_detected = True # On met le booléen à True
			if flag_title_detected == False: # Si le booléen est toujours à False, ça veut dire qu'on n'a jamais trouvé que c'est un titre
				outFile.write(instance + '\n') # Donc on stocke l'id dans un fichier

def GetResults(ref_results_name, test_results_directory):
	results = {} # Initialisation de la structure de données qui contiendra, pour une istance donnée, les résultats de la réf et des modèles à tester
	results = AddModelResults(results, ref_results_name, sep='\t', id_col=0, label_col=1) # On charge la structure de données des résultats de la reference
	for file_name in os.listdir(test_results_directory): # Pour chaque modele, on ajoute les résultats dans le dico
		if '.txt' in file_name: # On fait bien attention à ne pas passer en revue que les fichiers txt contenant les résultats des modèles
			results = AddModelResults(results, test_results_directory+file_name, sep='\t', id_col=0, label_col=1)
	return results

if __name__ == "__main__":
	ref_results_name = sys.argv[1] # Fichier contenant les résultats de la référence
	test_results_directory = sys.argv[2] # Répertoire contenant tous les fichiers contenant les résulats des modèles à tester

	# 1. Chargement des résultats
	results = GetResults(ref_results_name, test_results_directory)
	# 2. Affichage des précision, rappel et f-mesure
	#Print_P_R_Fm(results, ref_name=ref_results_name, labels=['0', '1'])
	Write_P_R_Fm(outFile_name='performances_models.tsv', results=results, ref_name=ref_results_name, labels=['0', '1'])

	# 3. Écriture des faux négatifs
	Write_FN(results=results, ref_name=ref_results_name)	