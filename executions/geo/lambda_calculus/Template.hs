module Main where

import Lib
import Geobase
import Geofunctions
import System.Environment


main :: IO ()
main = do
    putStrLn "Execute Lambda Calculus"
    let predicted_result = (count_ (\x -> (and [(river x), (loc x "texas:s")])))
    let truth_result = (count_ (\x -> (and [(river x), (loc x "texas:s")])))
    let compare_result = predicted_result == truth_result
    let results = [compare_result]

    let total = length results
    let correct = length . filter (\x -> x == True) $ results

    putStrLn "Results: "
    print total
    print correct
