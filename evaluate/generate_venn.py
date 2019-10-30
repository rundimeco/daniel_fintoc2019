import sys
import io
import venn
import matplotlib
from matplotlib import pyplot as plt
from matplotlib_venn import venn3, venn3_circles


def get_id_instances_title(filename, sep):
	infile = io.open(filename, mode='r', encoding='utf-8')
	ids = []
	line = infile.readline()
	while line != '':
		elm = line.strip().split(sep)
		id_ = elm[0]
		label = elm[1]
		if label == '1':
			ids.append(id_)
		line = infile.readline()
	infile.close()
	return ids


ref = get_id_instances_title(sys.argv[1], sep='\t')
best_model_1 = get_id_instances_title(sys.argv[2], sep='\t')
best_model_2 = get_id_instances_title(sys.argv[3], sep='\t')


v = venn3([set(ref), set(best_model_1), set(best_model_2)], set_labels = ('Référence', '1<n<3 (MNB)', '1<n<4 (MNB)'))
plt.title('Comparison de deux méthodes n-grams (MNB)')
plt.show()

""" Venn... plus de trois ensembles...
model1 = get_id_instances_title(sys.argv[1], sep='\t')
model2 = get_id_instances_title(sys.argv[2], sep='\t')
model3 = get_id_instances_title(sys.argv[3], sep='\t')
model4 = get_id_instances_title(sys.argv[4], sep='\t')
model5 = get_id_instances_title(sys.argv[5], sep='\t')
#model6 = get_id_instances_title(sys.argv[6], sep='\t')

labels = venn.get_labels([model1, model2, model3, model4, model5])
fig, ax = venn.venn5(labels, names=['ngrams1-1', 'ngrams1-2', 'ngrams1-3', 'ngrams1-4', 'ngrams1-5', 'ngrams1-6'])
plt.show()
"""
