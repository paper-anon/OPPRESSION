#! /usr/bin/env bash

tsp python3 node_id_eval.py 2 --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 3 --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 5 --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 10 --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 15 --temp $1 --res $2 --pickle $3 --texts $4 -j 20

tsp python3 node_id_eval.py 2 --long --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 3 --long --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 5 --long --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 10 --long --temp $1 --res $2 --pickle $3 --texts $4 -j 20
tsp python3 node_id_eval.py 15 --long --temp $1 --res $2 --pickle $3 --texts $4 -j 20

tsp python3 match_length_eval.py --temp $1 --res $2 --pickle $3 --texts $4 -j 20