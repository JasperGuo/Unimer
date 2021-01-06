# Evaluator

This is a simple haskell project to evaluate an untyped lambda calculus expression for Geoquery.

## Dependency

1. Follow the instructions in (https://www.haskell.org/downloads/Install) to install the compile and execution environemnt of Haskell and its cross-platform build too `stack`.

2. Note that we have to transform the original lambda calculus expressions to a haskell expression before execution. Please refer to the `../transform_lambda_caculus.py`

## Run the project

1. Compile the project with `stack build`
2. Run the Code with `stack exec evaluator-exe`

We can quickly inspect execution result of a lambda calculus with Haskell REPL.

1. Lauch the REPL with command `stack ghci`
2. Load predicate modules, `:load ./src/Geofunctions.hs`
3. Run a lambda calculus expression

