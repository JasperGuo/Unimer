### Evaluate the correctness of a synthesized prolog query

#### Requirements
1. Setup a Prolog execution environment, e.g., the **swi-prolog** (https://www.swi-prolog.org/)


#### Execution
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