import json
import urllib.request
from urllib.request import *
import shutil
import os.path
import re

BASE_PATH = os.path.join(os.path.dirname(__file__), "../")

with open(BASE_PATH + '/json/ptu_pokedex_1_05_plus.json', encoding='utf-8') as data_file:
    data = data_file.read().replace(u'\\u00c9', "\\\\'{E}").replace(u'\\u00e9', "\\\\'{e}")
    regex = re.compile(r'"(\d\d\d):(..?.?)"')
    data = regex.sub(r'"\1-\2"', data)
    data = json.loads(data)
    
with open(BASE_PATH + '/json/moves.json', encoding='utf8') as move_file:
    moves = json.load(move_file)

def forme(num):
    if "710" in num or "711" in num or "555" in num:
        return num[0:3]
    return {
        '386-A':'386_f2', 
        '386-D':'386_f3', 
        '386-S':'386_f4', 
        '413-S':'413_f2', 
        '413-T':'413_f3', 
        '479-H':'479_f2', 
        '479-W':'479_f3',
        '479-Fr':'479_f4',
        '479-Fa':'479_f5',
        '479-M':'479_f6',
        '487-O':'487_f2',
        '492-S':'492_f2',
        '645-T':'645_f2',
        '642-T':'642_f2',
        '641-T':'641_f2',
        '646-Z':'646_f3',
        '646-R':'646_f2',
        '648-S':'648_f2', 
        '678-F':'678_f2', 
        '720-U':'720_f2'
    }[num]


flattened_info = {}

def dump_to_file(filename):
    dump_file = open(BASE_PATH + "/out/" + filename,  "w+")
    base_string = "%<*{0}>{1}%</{0}>"
    for key in flattened_info:
        dump_file.write(base_string.format(key,  flattened_info[key]))
        
    dump_file.close()
    
def get_type(move):
    if "can" in move and "any" in move:
        return ""
    elif move == "Hyperspace Hole":
        return "Psychic"
    elif move == "Hyperspace Fury":
        return "Dark"
    else:
        return moves[move]["Type"]
        
def on_type(move):
    type = get_type(move)
    if "Hyperspace" not in move and (type == "" or moves[move]["Class"] == "Status"):
        return False
    return type in flattened_info["types"]
    
def is_first_stage(pokemon):
    species = pokemon["Species"]
    for evo in pokemon["EvolutionStages"]:
        if evo["Species"] == species and evo["Stage"] == 1:
            return True
    return False
    
def flatten_stats(stats):
    flattened_info["hp"] = stats["HP"]
    flattened_info["atk"] = stats["Attack"]
    flattened_info["def"] = stats["Defense"]
    flattened_info["spa"] = stats["SpecialAttack"]
    flattened_info["spd"] = stats["SpecialDefense"]
    flattened_info["spe"] = stats["Speed"]
    
def flatten_abilities(abilities):
    ability_count = {"Basic": 0,  "Advanced": 0,  "High": 0}
    for ability in abilities:
        ability_count[ability["Type"]] += 1
    
    ability_used_count = {"total":1, "Basic": 1,  "Advanced": 1,  "High": 1}    
    ability_str="{0} Ability {1}: {2}"
    for ability in abilities:
        type = ability["Type"]
        ability_number = "" if ability_count[type] == 1 else ability_used_count[type]
        flattened_info["abi"+str(ability_used_count["total"])] = ability_str.format(type,  ability_number,  ability["Name"])
        ability_used_count["total"] += 1
        ability_used_count[type] += 1
        
def flatten_height(height):
    height_string = "{0}'{1}\" / {2}m ({3})"
    feet = height["Imperial"]["Minimum"]["Feet"]
    inches = height["Imperial"]["Minimum"]["Inches"]
    meters = height["Metric"]["Minimum"]["Meters"]
    size = height["Category"]["Minimum"]
    flattened_info["height"] = height_string.format(feet,  inches,  meters,  size)
        
def flatten_weight(weight):
    weight_string = "{0} lbs. / {1} kg ({2})"
    pounds = weight["Imperial"]["Minimum"]["Pounds"]
    kilos = weight["Metric"]["Minimum"]["Kilograms"]
    wc = weight["WeightClass"]["Minimum"]
    flattened_info["weight"] = weight_string.format(pounds, kilos, wc)
    
def flatten_breeding(breeding):
    if breeding["HasGender"]:
        gender_string = "{0}\\% M / {1}\\% F"
        male = breeding["MaleChance"]*100
        female = breeding["FemaleChance"]*100
        flattened_info["gender"] = gender_string.format(male, female)
    else:
        flattened_info["gender"] = "No Gender"
        
    flattened_info["eggGroups"] = " / ".join(breeding["EggGroups"])
    
    flattened_info["eggHatch"] = breeding["HatchRate"]
    
def flatten_environment(environment):
    flattened_info["habitat"] = ", ".join(environment["Habitats"])
    flattened_info["diet"] = ", ".join(environment["Diet"])
    
def flatten_biological(pokemon):
    flatten_height(pokemon["Height"])
    flatten_weight(pokemon["Weight"])
    flatten_breeding(pokemon["BreedingData"])
    flatten_environment(pokemon["Environment"])
    
def flatten_skills(skills):
    for skill in skills:
        name = skill["SkillName"].lower()
        flattened_info[name] = skill["DiceRank"]
    
def flatten_capabilities(capabilities):
    capability_list = []
    for capability in capabilities:
        cap_string = capability["CapabilityName"]
        value = capability["Value"]
        if value != "":
            if any(char.isdigit() for char in value):
                cap_string += " " + value
            else:
                cap_string += " (" + value + ")"
        capability_list += [cap_string]
        
    flattened_info["capabilities"] = ", ".join(capability_list)
    
def flatten_level_up(level_ups):
    level_up_list = []
    level_up_base ="\\indent\\indent{0} {1} - {2}\\\\"
    
    for level_up in level_ups:
        learned = level_up["LevelLearned"]
        name = level_up["Name"]
        type = get_type(name)
        level_up_string = level_up_base.format(learned, name, type)
        if on_type(name):
            level_up_string = "\\textbf{" + level_up_string + "}"
        level_up_list += [level_up_string]
    flattened_info["levelUp"] = " ".join(level_up_list)
    
def flatten_tms(tms):
    tm_list = []
    for tm in tms:
        tm_string = tm["TechnicalMachineId"]
        tm_string += " " + tm["Name"]
        if on_type(tm["Name"]):
            tm_string = "\\textbf{" + tm_string + "}"
        
        tm_list += [tm_string]
        
    tm_out = ""
    if tm_list != []:
        tm_out = "\\noindent TM/HM Move List\\\\\\indent\\indent {0}\\\\"
        tm_out = tm_out.format(", ".join(tm_list))
    flattened_info["tms"] = tm_out
    
def flatten_egg(eggs):
    egg_list = []
    for egg in eggs:
        egg_string = egg["Name"]
        if on_type(egg_string):
            egg_string = "\\textbf{" + egg_string + "}"
        egg_list += [egg_string]
        
    egg_out = ""
    if egg_list != []:
        egg_out = "\\noindent Egg Move List\\\\\\indent\\indent {0}\\\\"
        egg_out = egg_out.format(", ".join(egg_list))
    flattened_info["eggMoves"] = egg_out
    
def flatten_tutor(tutors):
    tutor_list = []
    for tutor in tutors:
        tutor_string = tutor["Name"]
        if "Natural" in tutor and tutor["Natural"]:
            tutor_string += "(N)"
        if on_type(tutor["Name"]):
            tutor_string = "\\textbf{" + tutor_string + "}"
        tutor_list += [tutor_string]
    
    tutor_out = ""
    if tutor_list != []:
        tutor_out = "\\noindent Tutor Move List\\\\\\indent\\indent {0}\\\\"
        tutor_out = tutor_out.format(", ".join(tutor_list))
    flattened_info["tutor"] = tutor_out
    
def flatten_moves(pokemon):
    flatten_level_up(pokemon["LevelUpMoves"])
    flatten_tms(pokemon["TmHmMoves"])
    flatten_egg(pokemon["EggMoves"])
    flatten_tutor(pokemon["TutorMoves"])
    
def flatten_evolution(evolutions):
    evo_list = []
    for evo in evolutions:
        evo_string = "{0} - {1} {2}"
        evo_list += [evo_string.format(evo["Stage"],  evo["Species"],  evo["Criteria"])]
        
    flattened_info["evolutions"] = "\\\\".join(evo_list)
    
def flatten_pokemon(pokemon):
    flattened_info["name"] = pokemon["Species"].upper() + " " + ("" if pokemon["Form"] == "Standard" else pokemon["Form"])
    flattened_info["types"] = " / ".join(pokemon["Types"])
    flatten_stats(pokemon["BaseStats"])
    flatten_abilities(pokemon["Abilities"])
    flatten_biological(pokemon)
    flatten_skills(pokemon["Skills"])
    flatten_capabilities(pokemon["Capabilities"])
    flatten_moves(pokemon)
    flatten_evolution(pokemon["EvolutionStages"])
  
def prep_for_tex(number):
    flatten_pokemon(data[number])
    if not os.path.isfile(BASE_PATH + "/images/" + number +".png"):
        pic = forme(number) if "-" in number else number
        url = "http://assets.pokemon.com/assets/cms2/img/pokedex/full/"+pic+".png"
        with urllib.request.urlopen(Request(url, headers={'User-Agent': 'Mozilla'})) as response, open(BASE_PATH + "/images/" + number +".png", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    dump_to_file(number + ".out")
    
#prep_for_tex("648-S")

