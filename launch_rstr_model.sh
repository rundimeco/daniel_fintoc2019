for l in `seq 2 10`;
do
	python3 rstr_model.py -o ./results_rstr_model/ -t shared_task_1.train.csv.json -T shared_task_1.test.csv.json -F -l $l -s 1
done