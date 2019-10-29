import sys
import io
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


venn3([set(ref), set(best_model_1), set(best_model_2)], set_labels = ('Ref', 'Best1', 'Best2'))
plt.title('Comparison of 2 best models')