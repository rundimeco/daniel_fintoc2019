import json
import sys

json_file = sys.argv[1]
test_set = json.load(open(json_file, 'r'))

for id in test_set.keys(): 
	for att in test_set[id].keys():
		if att == 'label':
			print(id + '\t' + test_set[id][att])