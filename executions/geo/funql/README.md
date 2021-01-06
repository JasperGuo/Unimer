### Evaluate the correctness of a synthesized funql query

#### Requirements
1. Setup a Prolog execution environment, e.g., the **swi-prolog** (https://www.swi-prolog.org/)


#### Execution
1. Enter a prolog terminal by command ``swipl''
2. Load the facts and rules defined in GeoQuery with command 
```prolog
?- [geobase].
?- [geoquery].
?- [eval].
```
3. Get the execution result of a funql query `f` with command

```prolog
?- execute_funql_query(f,U).
```
For example, for a funql query, "answer(city(loc_2(stateid('kansas'))))", 

```prolog
?- execute_funql_query(answer(city(loc_2(stateid('virginia')))),U).
```
which will output 
```
[cityid(alexandria, va), cityid(arlington, va), cityid(chesapeake, va), cityid(hampton, va), cityid(lynchburg, va), cityid('newport news', va), cityid(norfolk, va), cityid(portsmouth, va), cityid(..., ...)|...]
```

4 d. Evaluate the correctness of a synthesized funql query and its golden standard with command:
```?- eval([0,0,F1,F2]).```.
where `F1` is the golden standard funql query, and `F2` is the prediction.

For example, for the question, "Give me the cities in Virginia.", 
```prolog
?- eval([0,0,answer(city(loc_2(stateid('virginia')))),answer(city(loc_2(stateid('kansas'))))]).
```
which will output 
```
0' '0' y' # y indicates that the execution result is as same as the golden standard
```