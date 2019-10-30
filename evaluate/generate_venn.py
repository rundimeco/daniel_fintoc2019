import sys
import io
import venn
import matplotlib
from matplotlib import pyplot as plt


def get_id_instances_title(filename, sep, label):
	"""Cette fonction permet de récupérer, à partir d'un fichier filename, toutes les instances étiquetées comme
	label. Elle donne en sortie une liste des instances.
	:param: filename: chemin d'accès vers le fichier contenant les résultats du modèle (id-instance   label)
	:param: sep: séparateur présent dans filename séparant les id-instance des label
	:label: label que l'on souhaite extraire
	:return: ids: liste de string représentant les instances étiquetées label. 
	"""
	infile = io.open(filename, mode='r', encoding='utf-8')
	ids = []
	line = infile.readline()
	while line != '':
		elm = line.strip().split(sep)
		id_ = elm[0]
		label = elm[1]
		if label == label:
			ids.append(id_)
		line = infile.readline()
	infile.close()
	return ids

def generate_venn_diagram(nb_dim, files, names, sep, label):
	"""Cette fonction fait l'appel du fichier venn.py (qui doit être présent dans le même dossier que generate_venn.py)
	pour générer les diagrammes de Venn.
	:param: nombre de dimensions présent dans le diagramme de Venn (1 < nb_dim <= 6)
	:param: files: liste des chemins d'accès aux fichiers contenant les résultats des modèles
	:param: names: liste des noms des modèles (doit être en adéquation avec la liste des modèles files)
	:param: sep: séparateur présent dans filename séparant les id-instance des label 
	:label: label que l'on souhaite extraire
	"""
	if nb_dim < 2 or nb_dim > 6:
		print('Le diagramme de Venn ne peut être généré que pour un nombre de dimensions supérieur à un et inférieur ou égal à 6.')
	else:
		i = 0
		models = []
		while i < nb_dim:
			models.append(get_id_instances_title(files[i], sep=sep, label=label))
			i += 1

		labels = venn.get_labels(models)
		if nb_dim == 2:
			fig, ax = venn.venn2(labels, names=names)
			plt.show()
		elif nb_dim == 3:
			fig, ax = venn.venn3(labels, names=names)
			plt.show()
		elif nb_dim == 4:
			fig, ax = venn.venn4(labels, names=names)
			plt.show()
		elif nb_dim == 5:
			fig, ax = venn.venn5(labels, names=names)
			plt.show()
		elif nb_dim == 6:
			fig, ax = venn.venn6(labels, names=names)
			plt.show()
		else:
			print('Le diagramme de Venn ne peut être généré que pour un nombre de dimensions supérieur à un et inférieur ou égal à 6.')

if __name__ == '__main__':

	# Ceci est un exemple d'appel de la fonction generate_venn_diagram.
	# Il faut mettre dans le Terminal les chemins vers les fichiers contenant les résultats des modèles 
	# pour que sys.argv[1], sys.argv[2]... les captent bien.
	#generate_venn_diagram(nb_dim=4, files=[sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]],
	#	names=['Référence', 'B1 (DT10)','B2 (DT10)', 'B3 (DT10)'], sep='\t', label='1')
	files = [file for file in sys.argv[1].replace('"', '').split(',')]
	names = [name for name in sys.argv[2].replace('"', '').split(',')]
	if 't' not in sys.argv[3]:
		sep = sys.argv[3]
	else:
		sep = '\t'
	label = sys.argv[4]
	
	generate_venn_diagram(nb_dim=4, files=files, names=names, sep=sep, label=label)







