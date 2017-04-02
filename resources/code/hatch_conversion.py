import json
import re
from pprint import pprint

with open('dex json/ptu_pokedex_1_05_plus.json') as data_file:
    data = json.load(data_file)
with open('dex json/hatch_rate.json') as data_file:
    hatch_rates = json.load(data_file)
    

    
def check_species(pokemon,  species):
    if pokemon["Species"] == species:
        return True
    for evo in pokemon["EvolutionStages"]:
        if evo["Species"] == species:
            return True
    return False
    
def get_hatch_rate(pokemon):
    p = re.compile('Average Hatch Rate: (.*) Days')
    for species in hatch_rates.keys():
        if check_species(pokemon, species):
            return p.findall(hatch_rates[species])[0]
    
for number in data.keys():
    data[number]["BreedingData"]["HatchRate"] = get_hatch_rate(data[number])
    
with open('data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
    
pprint(data["001"])
