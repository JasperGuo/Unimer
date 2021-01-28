# README

### Project Structure

1. The `data_readers` directory specifies the data readers for each neural semantic parsing approaches. Users can refer to `test_data_reader.py` for details about its arguments.
2. The `grammars` directory specifies the definitions of grammars of meaning representations for each domain. It also contains all the preprocessing and postprocessing code for MRs. For each MR, there are at least two sets of grammar rules. For example, `./grammars/geo/funql_grammar.py` and `./grammars/geo/typed_funql_grammar.py` defines two sets of grammar rules for FunQL in Geo.
3. The `executions` directory specifies the code for calculuating the execution-match metric.
4. The `neural_models` directory specifies the code for implementing neural semantic parsing approaches. The `./model_builder.py` encapsulates the construction of neural models.
5. The `./run_parser.py` is main entry of the project. It specifies the training and evaluations process.
6. The `program_alias_analysis` folder is the code for searching aliases for logical forms.
7. The `nni` folder specifies the configuration of the NNI platform we used.

### How do I get set up?

1. Setup a python 3.6 environment and install third-party packages with command `pip install -r requirements.txt`.
2. Copy the data folder (Submitted as Supplemenatry Materials)
3. To train a model, copy the corresponding script (`.sh`) from the scripts directory to the project directory. For example, to train a seq2seq model (w/ copy) of FunQL in ATIS, copy the script `train_geo_funql_recombination_copy_seq_parsing.sh` to here.
Alter the hyper-parameters in the script if you want, and create a directory specified in the script to save checkpoint.
Then, run the comannd `./train_atis_funql_recombination_copy_seq_parsing.sh $GPU_ID`.
4. To test a pretrained model, copy the corresponding evaluation script from the scripts directory. For the above example, copy the `eval_geo_funql_recombination_copy_seq_parsing.sh` and make the same change as in the train script.
Then, run the comannd `./eval_atis_funql_recombination_copy_seq_parsing.sh $GPU_ID`.
When the evaluation is ended, the script will print the exact-match performance on the terminal.
Moreover, a prediction file, named `predictions.json` will be saved in the checkpoint directory, which can be used to calculuate execution-match.

### Setup Execution-Match Evaluation Environements

#### SQL

1. Install MySQL
2. Restore databases dump with the following commands:
```
mysql -u [username] -p atis < ./executions/atis/atis_mysql.sql
mysql -u [username] -p geo < ./executions/geo/geo_mysql.sql
mysql -u [username] -p job < ./executions/jobs/job_mysql.sql
```

#### Prolog & FunQL

1. Setup a Prolog execution environment, e.g., the **swi-prolog** (https://www.swi-prolog.org/)

Test:
1. Go to the directory `./executions/geo/prolog/`
1. Enter a prolog terminal by command ``swipl''
2. Load the facts and rules defined in GeoQuery with command ```?- [geoquery].```
2. Get the execution result of a prolog query `P` with command ```?- P.```.

For example, for the question, "Give me the cities in Virginia.",
```prolog
?- answer(A,(city(A),loc(A,B),const(B,stateid(virginia)))).
```
which will output 
```
[alexandria,arlington,chesapeake,hampton,lynchburg,'newport news',norfolk,portsmouth,richmond,roanoke,'virginia beach']
```

#### Lambda Calculus

Since we implement the Lambda Calculus execution engine in Geo with Haskell, we need to setup a Haskell programming environment environment, following the instructions in (https://www.haskell.org/downloads/)



### Calculuate Execution-Match Metric

1. Go to the domain directory, e.g., `./executions/geo`
2. Then, run `python ./evaluate_prolog.py --predictions ${PATH_TO predictions.json}`. Please carefully read the instructions in `./evaluate_{prolog|lambda_calculus|funql|sql}.py` for more details about the its arguments.
Some predications require postprocessing before they can be executed.

One exception is the calculation of Execution-Match Metric for Lambda Calculus in Geo.
Since we implement the execution engine of Lambda Calculus in Haskell which is a static functional language, it needs to statically compile before running.
We need the following commands to calculus the metric:

1. `python ./evalaute_lambda_calculus.py --predictions ../../trained_models/geo_lambda_seed_1_predictions.json`
2. `cd ./lambda_calculus/evaluator/`
3. `stack build`. Then, if some grammartical errors are reported, direclty comment out them in `./app/Main.hs` and recompile. (The predictions of neural approaches are not guaranteed to syntatically correct.)
4. `stack exec evaluator-exe > ./lambda_calculus_is_correct_result.log`
5. `cd ../../`
6. `python ./evalaute_lambda_calculus.py --predictions ../../trained_models/geo_lambda_seed_1_predictions.json --measure`, which will show the execution-match metric in the terminal.
