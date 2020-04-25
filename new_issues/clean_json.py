import os
import json

def clean_json(dictionary, traits):
    for trait in traits:  
        if type(dictionary[trait]) is list:
            newList = []
            for i in dictionary[trait]:
                newList.append(i.replace("'","''"))
            dictionary[trait] = newList
        elif type(dictionary[trait]) is str :
            dictionary[trait] = dictionary[trait].replace("'","''")


trait_list1 = ['cover_date', 'description', 'image','person_credits','character_credits','name','series']
field_list = ['aliases', 'creators', 'deck','description', 'first_appeared_in_issue', 'image', 'name', 'real_name', 'api_detail_url']
trait_list = ['aliases', 'birth', 'country','death','deck','description','hometown','image']


directorys = {'Issues/':trait_list1, 'Characters/':field_list, 'Creators/':trait_list}


for directory,traits in directorys.items():
    for jsonFile  in  os.listdir(directory):
        importantFile = open(directory + jsonFile)
        issueDict = json.load(importantFile)
        clean_json(issueDict,traits)
        if directory == 'Characters/':
            if 'appearance' in issueDict:
                clean_json(issueDict['appearance'],['height'])

        with open(directory+jsonFile, 'w+') as out_file:
            out_file.write(json.dumps(issueDict, sort_keys=True, indent=4))
