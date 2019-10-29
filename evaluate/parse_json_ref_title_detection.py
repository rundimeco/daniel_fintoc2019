import json

test_set = json.load(open('./../data/shared_task_2.test.csv.json', 'r'))

for id in test_set.keys(): 
	for att in test_set[id].keys():
		if att == 'label':
			print(id + '\t' + test_set[id][att])