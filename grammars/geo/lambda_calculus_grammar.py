# coding=utf8

ROOT_RULE = 'statement -> [expression]'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY['statement'] = ['(expression ws)']
GRAMMAR_DICTIONARY['expression'] = ['(application)', '(abstraction)', '(constant)', '(variable)']
GRAMMAR_DICTIONARY['abstraction'] = ['("(" ws "lambda" wsp variable_definition wsp expression ws ")")']
GRAMMAR_DICTIONARY['application'] = ['("(" ws function ws ")")']
GRAMMAR_DICTIONARY['function'] = [
    '("capital:<c,t>" wsp expression)',
    '("capital:<s,c>" wsp expression)',
    '("high_point:<e,<e,t>>" wsp expression wsp expression)',
    '("capital:<s,<c,t>>" wsp expression wsp expression)',
    '("argmax:<<e,t>,<<e,i>,e>>" wsp expression wsp expression)',
    '("city:<c,t>" wsp expression)',
    '("the:<<e,t>,e>" wsp expression)',
    '("size:<lo,i>" wsp expression)',
    '("area:<lo,i>" wsp expression)',
    '("high_point:<e,l>" wsp expression)',
    '("argmin:<<e,t>,<<e,i>,e>>" wsp expression wsp expression)',
    '("population:<lo,i>" wsp expression)',
    '("state:<s,t>" wsp expression)',
    '("sum:<<e,t>,<<e,i>,i>>" wsp expression wsp expression)',
    '("town:<lo,t>" wsp expression)',
    '("lake:<l,t>" wsp expression)',
    '("river:<r,t>" wsp expression)',
    '("population:<lo,<i,t>>" wsp expression wsp expression)',
    '("forall:<<e,t>,t>" wsp expression)',
    '("mountain:<m,t>" wsp expression)',
    '("elevation:<lo,i>" wsp expression)',
    '("next_to:<lo,<lo,t>>" wsp expression wsp expression)',
    '("place:<p,t>" wsp expression)',
    '("=:<i,<i,t>>" wsp expression wsp expression)',
    '("<:<i,<i,t>>" wsp expression wsp expression)',
    '(">:<i,<i,t>>" wsp expression wsp expression)',
    '("count:<<e,t>,i>" wsp expression)',
    '("exists:<<e,t>,t>" wsp expression)',
    '("loc:<lo,<lo,t>>" wsp expression wsp expression)',
    '("elevation:<lo,<i,t>>" wsp expression wsp expression)',
    '("capital2:<s,<c,t>>" wsp expression wsp expression)',
    '("equals:<e,<e,t>>" wsp expression wsp expression)',
    '("density:<lo,i>" wsp expression)',
    '("density:<lo,<i,t>>" wsp expression wsp expression)',
    '("named:<e,<n,t>>" wsp expression wsp expression)',
    '("len:<r,i>" wsp expression)',
    '("major:<lo,t>" wsp expression)',
    '("in:<lo,<lo,t>>" wsp expression wsp expression)',
    '("and:<t*,t>" wsp application wsp polyvariadic_expression)',
    '("or:<t*,t>" wsp application wsp polyvariadic_expression)',
    '("not:<t,t>" wsp expression)',
]
GRAMMAR_DICTIONARY['polyvariadic_expression'] = ['(application ws polyvariadic_expression)', '""']
GRAMMAR_DICTIONARY['variable'] = ['"$0"', '"$1"', '"$2"', '"$3"', '"$4"']
GRAMMAR_DICTIONARY['variable_definition'] = ['"$0:e"', '"$1:e"', '"$2:e"', '"$3:e"', '"$4:e"', '"$0:i"']
GRAMMAR_DICTIONARY['constant'] = ['(state)', '(city)', '(river)', '("death_valley:lo")',
                                  '(names)', '(place)', '(mountain)', '("usa:co")', '("0:i")']
GRAMMAR_DICTIONARY['state'] = ['"oklahoma:s"', '"mississippi:s"', '"west_virginia:s"', '"arkansas:s"', '"virginia:s"', '"vermont:s"', '"maine:s"', '"nevada:s"', '"maryland:s"', '"wisconsin:s"', '"new_york:s"', '"arizona:s"', '"ohio:s"', '"missouri:s"', '"tennessee:s"', '"pennsylvania:s"', '"massachusetts:s"', '"texas:s"', '"hawaii:s"', '"south_dakota:s"', '"illinois:s"', '"utah:s"', '"kentucky:s"', '"alabama:s"', '"new_hampshire:s"', '"new_mexico:s"', '"colorado:s"', '"rhode_island:s"', '"south_carolina:s"', '"delaware:s"', '"michigan:s"', '"new_jersey:s"', '"louisiana:s"', '"florida:s"', '"minnesota:s"', '"alaska:s"', '"north_dakota:s"', '"california:s"', '"georgia:s"', '"iowa:s"', '"idaho:s"', '"indiana:s"', '"north_carolina:s"', '"oregon:s"', '"montana:s"', '"kansas:s"', '"nebraska:s"', '"washington:s"', '"wyoming:s"']
GRAMMAR_DICTIONARY['city'] = ['"kalamazoo_mi:c"', '"san_diego_ca:c"', '"denver_co:c"', '"portland_me:c"', '"san_francisco_ca:c"', '"flint_mi:c"', '"tempe_az:c"', '"austin_tx:c"', '"des_moines_ia:c"', '"springfield_il:c"', '"springfield_mo:c"', '"baton_rouge_la:c"', '"atlanta_ga:c"', '"columbus_oh:c"', '"rochester_ny:c"', '"springfield_sd:c"', '"tucson_az:c"', '"boulder_co:c"', '"salem_or:c"', '"sacramento_ca:c"', '"detroit_mi:c"', '"san_jose_ca:c"', '"indianapolis_in:c"', '"erie_pa:c"', '"san_antonio_tx:c"', '"pittsburgh_pa:c"', '"albany_ny:c"', '"portland_or:c"', '"dallas_tx:c"', '"dover_de:c"', '"boston_ma:c"', '"scotts_valley_ca:c"', '"riverside_ca:c"', '"chicago_il:c"', '"montgomery_al:c"', '"seattle_wa:c"', '"new_orleans_la:c"', '"new_york_ny:c"', '"minneapolis_mn:c"', '"fort_wayne_in:c"', '"miami_fl:c"', '"spokane_wa:c"', '"san_franciso_ca:c"', '"houston_tx:c"', '"washington_dc:c"']
GRAMMAR_DICTIONARY['river'] = ['"potomac_river:r"', '"mississippi_river:r"', '"colorado_river:r"', '"north_platte_river:r"', '"rio_grande_river:r"', '"red_river:r"', '"missouri_river:r"', '"ohio_river:r"', '"delaware_river:r"', '"chattahoochee_river:r"']
GRAMMAR_DICTIONARY['mountain'] = ['"mount_mckinley:m"', '"mount_whitney:m"', '"guadalupe_peak:m"']
GRAMMAR_DICTIONARY['place'] = ['"mount_mckinley:p"', '"mount_whitney:p"']
GRAMMAR_DICTIONARY['names'] = ['"austin:n"', '"springfield:n"', '"dallas:n"', '"salt_lake_city:n"', '"portland:n"', '"rochester:n"', '"plano:n"', '"durham:n"', '"colorado:n"']
GRAMMAR_DICTIONARY["ws"] = ['~"\s*"i']
GRAMMAR_DICTIONARY["wsp"] = ['~"\s+"i']

COPY_TERMINAL_SET = {'state', 'city', 'river', 'mountain',
                     'place', 'names'}
