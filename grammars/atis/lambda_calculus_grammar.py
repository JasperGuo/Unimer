# coding=utf8

ROOT_RULE = 'statement -> [expression]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(expression ws)']
GRAMMAR_DICTIONARY['expression'] = [
    '(constant)', '(application)', '(abstraction)', '(variable)']
GRAMMAR_DICTIONARY['abstraction'] = [
    '("(" ws "_lambda" wsp variable_definition wsp expression ws ")")']
GRAMMAR_DICTIONARY['application'] = ['("(" ws function ws ")")']
GRAMMAR_DICTIONARY['function'] = [
    '("_month_arrival" wsp expression wsp expression)',
    '("_stop_arrival_time" wsp expression)',
    '("_stops" wsp expression wsp expression)',
    '("_stops" wsp expression)',
    '("_weekday" wsp expression)',
    '("_day_number" wsp expression wsp expression)',
    '("_meal:_t" wsp expression wsp expression)',
    '("_meal:_t" wsp expression)',
    '("_meal" wsp expression wsp expression)',
    '("_meal" wsp expression)',
    '("_approx_return_time" wsp expression wsp expression)',
    '("_booking_class:_t" wsp expression)',
    '("_booking_class" wsp expression wsp expression)',
    '("_booking_class" wsp expression)',
    '("_approx_arrival_time" wsp expression wsp expression)',
    '("_fare" wsp expression wsp expression)',
    '("_fare" wsp expression)',
    '("_flight" wsp expression)',
    '("_the" wsp expression wsp expression)',
    '("_aircraft_basis_type" wsp expression wsp expression)',
    '("_aircraft_code:_t" wsp expression)',
    '("_aircraft_code" wsp expression wsp expression)',
    '("_aircraft_code" wsp expression)',
    '("_economy" wsp expression)',
    '("_has_stops" wsp expression)',
    '("_minutes_distant" wsp expression wsp expression)',
    '("_minutes_distant" wsp expression)',
    '("_>" wsp expression wsp expression)',
    '("_departure_time" wsp expression wsp expression)',
    '("_departure_time" wsp expression)',
    '("_ground_fare" wsp expression)',
    '("_oneway" wsp expression)',
    '("_airport" wsp expression wsp expression)',
    '("_airport" wsp expression)',
    '("_=" wsp expression wsp expression)',
    '("_named" wsp expression wsp expression)',
    '("_taxi" wsp expression)',
    '("_flight_number" wsp expression wsp expression)',
    '("_flight_number" wsp expression)',
    '("_loc:_t" wsp expression wsp expression)',
    '("_airline" wsp expression wsp expression)',
    '("_airline" wsp expression)',
    '("_during_day" wsp expression wsp expression)',
    '("_arrival_month" wsp expression wsp expression)',
    '("_manufacturer" wsp expression wsp expression)',
    '("_fare_basis_code" wsp expression wsp expression)',
    '("_fare_basis_code" wsp expression)',
    '("_approx_departure_time" wsp expression wsp expression)',
    '("_rapid_transit" wsp expression)',
    '("_arrival_time" wsp expression wsp expression)',
    '("_arrival_time" wsp expression)',
    '("_tonight" wsp expression)',
    '("_max" wsp expression wsp expression)',
    '("_min" wsp expression wsp expression)',
    '("_services" wsp expression wsp expression)',
    '("_next_days" wsp expression wsp expression)',
    '("_not" wsp application)',
    '("_or" wsp application wsp polyvariadic_expression)',
    '("_and" wsp application wsp polyvariadic_expression)',
    '("_from" wsp expression wsp expression)',
    '("_today" wsp expression)',
    '("_argmax" wsp variable wsp expression wsp expression)',
    '("_argmin" wsp variable wsp expression wsp expression)',
    '("_connecting" wsp expression)',
    '("_overnight" wsp expression)',
    '("_airline:_e" wsp expression)',
    '("_restriction_code" wsp expression)',
    '("_<" wsp expression wsp expression)',
    '("_round_trip" wsp expression)',
    '("_stop" wsp expression wsp expression)',
    '("_year" wsp expression wsp expression)',
    '("_day_after_tomorrow" wsp expression)',
    '("_sum" wsp variable wsp expression wsp expression)',
    '("_day_return" wsp expression wsp expression)',
    '("_discounted" wsp expression)',
    '("_time_zone_code" wsp expression)',
    '("_equals" wsp expression wsp expression)',
    '("_limousine" wsp expression)',
    '("_daily" wsp expression)',
    '("_class_type" wsp expression wsp expression)',
    '("_day_arrival" wsp expression wsp expression)',
    '("_during_day_arrival" wsp expression wsp expression)',
    '("_days_from_today" wsp expression wsp expression)',
    '("_from_airport" wsp expression wsp expression)',
    '("_to_city" wsp expression wsp expression)',
    '("_has_meal" wsp expression)',
    '("_minimum_connection_time" wsp expression wsp expression)',
    '("_minimum_connection_time" wsp expression)',
    '("_tomorrow" wsp expression)',
    '("_tomorrow_arrival" wsp expression wsp expression)',
    '("_tomorrow_arrival" wsp expression)',
    '("_day_number_arrival" wsp expression wsp expression)',
    '("_aircraft" wsp expression wsp expression)',
    '("_aircraft" wsp expression)',
    '("_capacity" wsp expression)',
    '("_month" wsp expression wsp expression)',
    '("_cost" wsp expression)',
    '("_day_number_return" wsp expression wsp expression)',
    '("_rental_car" wsp expression)',
    '("_day" wsp expression wsp expression)',
    '("_equals:_t" wsp expression wsp expression)',
    '("_airline_name" wsp expression)',
    '("_before_day" wsp expression wsp expression)',
    '("_exists" wsp variable wsp expression)',
    '("_jet" wsp expression)',
    '("_count" wsp variable wsp expression)',
    '("_miles_distant" wsp expression wsp expression)',
    '("_miles_distant" wsp expression)',
    '("_city" wsp expression)',
    '("_class_of_service" wsp expression wsp expression)',
    '("_class_of_service" wsp expression)',
    '("_turboprop" wsp expression)',
    '("_to" wsp expression wsp expression)',
    '("_time_elapsed" wsp expression wsp expression)',
    '("_time_elapsed" wsp expression)',
    '("_abbrev" wsp expression)',
    '("_month_return" wsp expression wsp expression)',
    '("_ground_transport" wsp expression)',
    '("_nonstop" wsp expression)',
    '("_after_day" wsp expression wsp expression)',
    '("_meal_code" wsp expression wsp expression)',
    '("_meal_code" wsp expression)',
    '("_air_taxi_operation" wsp expression)',
]

GRAMMAR_DICTIONARY['polyvariadic_expression'] = [
    '(application ws polyvariadic_expression)', '""']


GRAMMAR_DICTIONARY['variable_definition'] = [
    '(variable ":e")', '(variable ":i")']
GRAMMAR_DICTIONARY['variable'] = ['"$v0"', '"$v1"', '"$v2"', '"$v3"']

GRAMMAR_DICTIONARY['constant'] = ['(do)', '(city)', '(al)', '(time)',
                                  '(meal)', '(fn)', '(ap)', '(rc)', '(cl)', '(ac)', '(da)', '(dn)',
                                  '"9:_hr"', '"boeing:_mf"', '"sa:_dc"', '(mn)', '(yr)', '(pd)', '(fb)', '(st)', '(i)', '(bat)']
GRAMMAR_DICTIONARY['do'] = ['"100:_do"', '"1000:_do"', '"466:_do"', '"416:_do"', '"124:_do"', '"329:_do"', '"1100:_do"', '"415:_do"',
    '"200:_do"', '"150:_do"', '"932:_do"', '"500:_do"', '"1288:_do"', '"300:_do"', '"400:_do"', '"1500:_do"']
GRAMMAR_DICTIONARY['city'] = ['"nashville:_ci"', '"indianapolis:_ci"', '"san_diego:_ci"', '"long_beach:_ci"', '"atlanta:_ci"', '"kansas_city:_ci"', '"miami:_ci"', '"st_louis:_ci"', '"columbus:_ci"', '"toronto:_ci"', '"las_vegas:_ci"', '"burbank:_ci"', '"cleveland:_ci"', '"tacoma:_ci"', '"st_petersburg:_ci"', '"memphis:_ci"', '"denver:_ci"', '"dallas:_ci"', '"detroit:_ci"', '"oakland:_ci"', '"baltimore:_ci"', '"pittsburgh:_ci"', '"philadelphia:_ci"', '"milwaukee:_ci"', '"salt_lake_city:_ci"', '"san_jose:_ci"', '"tampa:_ci"', '"orlando:_ci"', '"chicago:_ci"', '"seattle:_ci"', '"new_york:_ci"', '"san_francisco:_ci"', '"boston:_ci"', '"washington:_ci"', '"cincinnati:_ci"', '"charlotte:_ci"', '"newark:_ci"', '"westchester_county:_ci"', '"los_angeles:_ci"', '"fort_worth:_ci"', '"minneapolis:_ci"', '"ontario:_ci"', '"montreal:_ci"', '"st_paul:_ci"', '"houston:_ci"', '"phoenix:_ci"']
GRAMMAR_DICTIONARY['al'] = ['"wn:_al"', '"ml:_al"', '"cp:_al"', '"nw:_al"', '"yx:_al"', '"ac:_al"', '"dl:_al"', '"kw:_al"', '"delta:_al"', '"as:_al"', '"tw:_al"',
                              '"co:_al"', '"ff:_al"', '"ea:_al"', '"ua:_al"', '"canadian_airlines_international:_al"', '"hp:_al"', '"lh:_al"', '"nx:_al"', '"usair:_al"', '"aa:_al"', '"us:_al"']
GRAMMAR_DICTIONARY['time'] = ['"1200:_ti"', '"1628:_ti"', '"1830:_ti"', '"823:_ti"', '"1245:_ti"', '"1524:_ti"', '"200:_ti"', '"1615:_ti"', '"1230:_ti"', '"705:_ti"', '"1045:_ti"', '"1700:_ti"', '"1115:_ti"', '"1645:_ti"', '"1730:_ti"', '"815:_ti"', '"0:_ti"', '"500:_ti"', '"1205:_ti"', '"1940:_ti"', '"2000:_ti"', '"1400:_ti"', '"1130:_ti"', '"2200:_ti"', '"645:_ti"', '"718:_ti"', '"2220:_ti"', '"600:_ti"', '"630:_ti"', '"800:_ti"', '"838:_ti"', '"1330:_ti"', '"845:_ti"', '"1630:_ti"', '"1715:_ti"', '"2010:_ti"', '"1000:_ti"', '"1619:_ti"',
                              '"2100:_ti"', '"1505:_ti"', '"2400:_ti"', '"1923:_ti"', '"1:_ti"', '"1145:_ti"', '"2300:_ti"', '"1620:_ti"', '"2023:_ti"', '"2358:_ti"', '"1500:_ti"', '"1815:_ti"', '"1425:_ti"', '"720:_ti"', '"1024:_ti"', '"1600:_ti"', '"100:_ti"', '"1310:_ti"', '"1300:_ti"', '"700:_ti"', '"650:_ti"', '"1800:_ti"', '"1110:_ti"', '"1410:_ti"', '"1030:_ti"', '"1900:_ti"', '"1017:_ti"', '"1430:_ti"', '"1850:_ti"', '"900:_ti"', '"1930:_ti"', '"1133:_ti"', '"1220:_ti"', '"2226:_ti"', '"1100:_ti"', '"819:_ti"', '"755:_ti"', '"2134:_ti"', '"555:_ti"']
GRAMMAR_DICTIONARY['meal'] = ['"snack:_me"',
                              '"lunch:_me"', '"dinner:_me"', '"breakfast:_me"']
GRAMMAR_DICTIONARY['fn'] = ['"838:_fn"', '"1059:_fn"', '"417:_fn"', '"323:_fn"', '"311:_fn"', '"137338:_fn"', '"315:_fn"', '"825:_fn"', '"345:_fn"', '"270:_fn"', '"271:_fn"', '"4400:_fn"', '"296:_fn"', '"1765:_fn"', '"343:_fn"', '"1222:_fn"', '"217:_fn"', '"459:_fn"', '"279:_fn"', '"1083:_fn"', '"324:_fn"', '"746:_fn"', '"281:_fn"', '"269:_fn"', '"98:_fn"',
                            '"212:_fn"', '"505:_fn"', '"852:_fn"', '"82:_fn"', '"352:_fn"', '"928:_fn"', '"19:_fn"', '"139:_fn"', '"415:_fn"', '"539:_fn"', '"3357:_fn"', '"813:_fn"', '"257:_fn"', '"297:_fn"', '"1055:_fn"', '"405:_fn"', '"201:_fn"', '"71:_fn"', '"1291:_fn"', '"402:_fn"', '"771:_fn"', '"106:_fn"', '"1039:_fn"', '"210:_fn"', '"2153:_fn"', '"3724:_fn"', '"1209:_fn"', '"21:_fn"']
GRAMMAR_DICTIONARY['ap'] = ['"ewr:_ap"', '"jfk:_ap"', '"pit:_ap"', '"oak:_ap"', '"bur:_ap"', '"las:_ap"', '"lga:_ap"', '"den:_ap"', '"mco:_ap"', '"dallas:_ap"', '"dfw:_ap"', '"phx:_ap"', '"slc:_ap"', '"iad:_ap"', '"sfo:_ap"', '"ont:_ap"',
                            '"iah:_ap"', '"ord:_ap"', '"mia:_ap"', '"cvg:_ap"', '"phl:_ap"', '"tpa:_ap"', '"dtw:_ap"', '"yyz:_ap"', '"ind:_ap"', '"atl:_ap"', '"mke:_ap"', '"hou:_ap"', '"bos:_ap"', '"dal:_ap"', '"bwi:_ap"', '"bna:_ap"', '"stapelton:_ap"', '"lax:_ap"']
GRAMMAR_DICTIONARY['rc'] = ['"b:_rc"', '"ap_55:_rc"', '"ap_57:_rc"', '"s_:_rc"', '"sd_d:_rc"',
                            '"ap_80:_rc"', '"d_s:_rc"', '"ap_58:_rc"', '"ls:_rc"', '"ap:_rc"', '"s:_rc"', '"ap_68:_rc"']
GRAMMAR_DICTIONARY['cl'] = ['"thrift:_cl"',
                            '"business:_cl"', '"first:_cl"', '"coach:_cl"']
GRAMMAR_DICTIONARY['ac'] = ['"dc10:_ac"', '"j31:_ac"', '"734:_ac"', '"73s:_ac"', '"72s:_ac"', '"100:_ac"', '"757:_ac"', '"d9s:_ac"',
    '"d10:_ac"', '"727:_ac"', '"m80:_ac"', '"747:_ac"', '"f28:_ac"', '"737:_ac"', '"733:_ac"', '"767:_ac"']
GRAMMAR_DICTIONARY['da'] = ['"monday:_da"', '"thursday:_da"', '"saturday:_da"', '"friday:_da"',
    '"sunday:_da"', '"wednesday:_da"', '"tuesday:_da"']
GRAMMAR_DICTIONARY['dn'] = ['"12:_dn"', '"18:_dn"', '"19:_dn"', '"31:_dn"', '"7:_dn"', '"20:_dn"', '"27:_dn"', '"6:_dn"', '"26:_dn"', '"17:_dn"', '"11:_dn"', '"10:_dn"', '"15:_dn"', '"23:_dn"',
                            '"1:_dn"', '"24:_dn"', '"25:_dn"', '"14:_dn"', '"13:_dn"', '"29:_dn"', '"3:_dn"', '"28:_dn"', '"8:_dn"', '"5:_dn"', '"2:_dn"', '"9:_dn"', '"30:_dn"', '"16:_dn"', '"4:_dn"', '"22:_dn"', '"21:_dn"']
GRAMMAR_DICTIONARY['mn'] = ['"january:_mn"', '"february:_mn"', '"december:_mn"', '"june:_mn"', '"august:_mn"',
                            '"april:_mn"', '"october:_mn"', '"november:_mn"', '"july:_mn"', '"may:_mn"', '"march:_mn"', '"september:_mn"']
GRAMMAR_DICTIONARY['yr'] = ['"1991:_yr"', '"1993:_yr"', '"1992:_yr"']
GRAMMAR_DICTIONARY['pd'] = ['"mealtime:_pd"', '"breakfast:_pd"', '"late:_pd"', '"afternoon:_pd"', '"late_evening:_pd"',
                            '"daytime:_pd"', '"pm:_pd"', '"late_night:_pd"', '"evening:_pd"', '"morning:_pd"', '"early:_pd"']
GRAMMAR_DICTIONARY['fb'] = ['"y:_fb"', '"qx:_fb"', '"m:_fb"', '"fn:_fb"', '"b:_fb"', '"q:_fb"',
                            '"bh:_fb"', '"qo:_fb"', '"h:_fb"', '"c:_fb"', '"qw:_fb"', '"k:_fb"', '"f:_fb"', '"yn:_fb"']
GRAMMAR_DICTIONARY['st'] = ['"minnesota:_st"', '"florida:_st"',
                            '"nevada:_st"', '"california:_st"', '"arizona:_st"']
GRAMMAR_DICTIONARY['i'] = ['"2:_i"', '"3:_i"', '"1:_i"']
GRAMMAR_DICTIONARY['bat'] = ['"737:_bat"', '"767:_bat"']

GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY["wsp"] = ['~"\s+"i']


COPY_TERMINAL_SET = {'do', 'city', 'al', 'time',
                     'meal', 'fn', 'ap', 'rc', 'cl', 'ac', 'da', 'dn',
                     'mn', 'yr', 'pd', 'fb', 'st', 'i', 'bat'}