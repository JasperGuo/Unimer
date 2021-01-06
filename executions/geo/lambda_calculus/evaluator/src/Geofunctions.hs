-- Define functions in Geoquery

module Geofunctions where

import Geobase
import Data.Ord
import Data.List
import Data.Set
import Data.Boolean
import Data.Maybe

get_first_string :: [String] -> String
get_first_string x
    | length x > 0 = head x
    | otherwise = ""

get_first_number :: [Double] -> Double
get_first_number x
    | length x > 0 = head x
    | otherwise = -2

get_first_list :: [[String]] -> [String]
get_first_list x
    | length x > 0 = head x
    | otherwise = []

mkUniq :: Ord a => [a] -> [a]
mkUniq = toList . fromList

is_country :: String -> Bool
is_country cname = (cname == "usa:co")

state :: String -> Bool
state sname = or [(state_name s) == sname | s <- states]

capital :: String -> Bool -- capital:<c,t>
capital cname = or [(state_capital s) == cname | s <- states]

capital2 :: String -> String -- capital:<s,c>
capital2 sname = get_first_string [state_capital s | s <- states, (state_name s) == sname]

is_state_capital :: String -> String -> Bool -- capital:<s,<c,t>>
-- is_state_capital sname cname = elem (sname,cname) [((state_name s),(state_capital s)) | s <- states]
is_state_capital sname cname = or [((state_name s) == sname) && ((state_capital s) == cname) | s <- states]

place :: String -> Bool -- place:<p,t>
place pname = or ([(highest_point h == pname) | h <- highlows] ++ [lowest_point h == pname | h <- highlows])

city :: String -> Bool -- city:<c,t>
city cname = or [city_name c == cname | c <- cities]

town :: String -> Bool -- town:<lo,t>
town tname = city tname

river :: String -> Bool -- river:<r,t>
river rname = or [river_name r == rname | r <- rivers]

lake :: String -> Bool -- lake:<l,t>
lake lname = or [lake_name r == lname | r <- lakes]

mountain :: String -> Bool -- mountain:<m,t>
mountain mname = or [mountain_name m == mname | m <- mountains]

high_point :: String -> String -> Bool -- high_point:<e,<e,t>>
high_point sname pname = or ([((place_state_name h == sname) && (highest_point h == pname)) | h <- highlows])

is_highest_point :: String -> Bool
is_highest_point pname = or [highest_point h == pname | h <- highlows]

is_lowest_point :: String -> Bool
is_lowest_point pname = or [lowest_point h == pname | h <- highlows]

lowest_place :: String -> String
lowest_place sname = get_first_string [lowest_point h | h <- highlows, place_state_name h == sname]
highest_place sname = get_first_string [highest_point h | h <- highlows, place_state_name h == sname]

elevation :: String -> Double -- elevation:<lo,i>
elevation pname =
    let 
        index = fromMaybe (length pname) (elemIndex ':' pname)
        name = Data.List.take index pname
        name1 = name ++ ":p"
    in if is_highest_point name1 
        then get_first_number [highest_elevation h | h <- highlows, (highest_point h) == name1]
        else if is_lowest_point name1 then get_first_number [lowest_elevation h | h <- highlows, (lowest_point h) == name1]
        else if mountain (name ++ ":m") then get_first_number [mountain_length m | m <- mountains, mountain_name m == (name ++ ":m")]
        else -2

is_correct_elevation :: String -> Double -> Bool -- elevation:<lo,<i,t>>
is_correct_elevation pname value = (elevation pname) == value

area :: String -> Double -- area:<lo,i>
area lname 
    | state lname = get_first_number [state_area s | s <- states, (state_name s) == lname]
    | is_country lname = country_area country
    | otherwise = -2

population :: String -> Double -- population:<lo,i>
population lname
    | state lname = get_first_number [state_population s | s <- states, (state_name s) == lname]
    | city lname = get_first_number [city_population c | c <- cities, (city_name c) == lname]
    | is_country lname = country_population country
    | otherwise = -2

is_population :: String -> Double -> Bool -- population:<lo,<i,t>>
is_population lname p = (population lname) == p

len :: String -> Double -- len:<r,i>
len rname = get_first_number [river_length r | r <- rivers, (river_name r) == rname]

size_ :: String -> Double -- size:<lo,i>
size_ lname
    | (state lname) || (is_country lname) = area lname -- state or country
    | city lname = population lname
    | river lname = len lname
    | place lname = elevation lname
    | otherwise = -2

next_to :: String -> String -> Bool -- next_to:<lo,<lo,t>>
next_to sname1 sname2 = elem sname1 (get_first_list [border_states s | s <- borders, (border_state_name s) == sname2])

loc :: String -> String -> Bool -- loc:<lo,<lo,t>>
loc lname1 lname2
    | (river lname1) && (state lname2) = elem lname2 (get_first_list [river_traverse_states r | r <- rivers, (river_name r) == lname1])
    | (lake lname1) && (state lname2) = elem lname2 (get_first_list [lake_traverse_states l | l <- lakes, (lake_name l) == lname1])
    | (mountain lname1) && (state lname2) = elem lname2 [mountain_state_name m | m <- mountains, (mountain_name m) == lname1]
    | (is_highest_point lname1) && (state lname2) = elem lname2 [place_state_name h | h <- highlows, (highest_point h) == lname1]
    | (is_lowest_point lname1) && (state lname2) = elem lname2 [place_state_name h | h <- highlows, (lowest_point h) == lname1]
    | (city lname1) && (state lname2) = elem lname2 [city_state_name c | c <- cities, (city_name c) == lname1]
    | is_country lname2 = True
    | otherwise = False

major :: String -> Bool -- major:<lo,t>
major pname
    | river pname = (len pname) > 750
    | city pname = (population pname) > 150000
    | otherwise = False

density :: String -> Double -- density:<lo,i>
density name
    | (state name || is_country name) = (population name) / (area name)
    | otherwise = -2

is_density :: String -> Double -> Bool -- density:<lo,<i,t>>
is_density name value = (density name) == value

all_caiptals = [state_capital s | s <- states]
all_states = [state_name s | s <- states]
all_cities = [city_name c | c <- cities]
all_lakes = [lake_name r | r <- lakes]
all_places = [highest_point h | h <- highlows] ++ [lowest_point h | h <- highlows]
all_rivers = [river_name r | r <- rivers]
all_mountains = [mountain_name m | m <- mountains]
all_entities = mkUniq (concat [all_states, all_cities, all_lakes, all_places, all_rivers, all_mountains, all_caiptals, [country_name country]])

all_populations = [population e | e <- all_entities, not (population e == -2)]
all_elevations = [elevation e | e <- all_entities, not (elevation e == -2)]
all_areas = [area e | e <- all_entities, not (area e == -2)]
all_densities = [density e | e <- all_entities, not (density e == -2)]
all_numbers = mkUniq (concat [all_populations, all_elevations, all_areas, all_densities])

-- Higher order functions
-- argmax:<<e,t>,<<e,i>,e>>
-- argmax_ fb fv = maximumBy (comparing fv) [e | e <- all_entities, fb e && not (fv e == -1)]
argmax_ :: (String -> Bool) -> (String -> Double) -> String
argmax_ fb fv =
    let candidates = [e | e <- all_entities, fb e && not (fv e == -2)]
    in if (length candidates) > 0 
        then (maximumBy (comparing fv) candidates)
        else ""


-- argmin:<<e,t>,<<e,i>,e>>
argmin_ :: (String -> Bool) -> (String -> Double) -> String
-- argmin_ fb fv = minimumBy (comparing fv) [e | e <- all_entities, fb e && not (fv e == -1)]
argmin_ fb fv =
    let candidates = [e | e <- all_entities, fb e && not (fv e == -2)]
    in if (length candidates) > 0
        then (minimumBy (comparing fv) candidates)
        else ""

-- sum:<<e,t>,<<e,i>,i>>
sum_ fb fv = sum [fv e | e <- all_entities, fb e]

-- forall:<<e,t>,t>
forall_ fb = and [fb e | e <- all_entities]

-- exists:<<e,t>,t>
-- exists_ fb = or [fb e | e <- all_entities]
exists_ fb = not (isNothing (Data.List.find fb all_entities))

-- count:<<e,t>,i>
count_ fb = sum [1 | e <- all_entities, fb e]

equals_ :: String -> String -> Bool -- equals:<e,<e,t>>
equals_ n1 n2 = n1 == n2

last_index :: Int -> String -> String
last_index n s = (reverse . Data.List.take n . reverse) s

process_name :: String -> String
process_name n
    | city n = Data.List.take ((length n) - 5) n  -- _tx:r
    | river n = Data.List.take ((length n) - 8) n -- _river:r
    | otherwise = Data.List.take ((length n) - 2) n

named :: String -> String -> Bool -- named:<e,<n,t>>
named n1 n2  = do
    if last_index 2 n2 == ":n"
        then elem n1 [e | e <- all_entities, (process_name e) ++ ":n" == n2]
        else elem n1 [e | e <- all_entities, e == n2]

lower_than :: Double -> Double -> Bool -- <:<i,<i,t>>
lower_than d1 d2 = d1 < d2

larger_than :: Double -> Double -> Bool -- >:<i,<i,t>> 
larger_than d1 d2 = d1 > d2

num_equals :: Double -> Double -> Bool -- =:<i,<i,t>> 
num_equals d1 d2 = d1 == d2

take_first :: (String -> Bool) -> String -- the:<<e,t>,e>
take_first f = get_first_string [e | e <- all_entities, f e]
