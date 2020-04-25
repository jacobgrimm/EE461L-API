import json
import requests
import os
import re


headers = {
'User-Agent': 'EE461L',
#'From': 'youremail@domain.com'  # This is another valid field
}
paramsDict = {
    'api_key': '9df7c108bb78e94a0b082fc87c2c8ce8e116b73c',
    'format': 'json',
    'limit' :'1',
    'resources' : 'character'
    }

field_list = ['aliases', 'creators', 'deck','description', 'first_appeared_in_issue', 'image', 'name', 'real_name', 'api_detail_url']

searchurl = "http://comicvine.gamespot.com/api/search/"

char_list = open("char_list.txt")

def main():
    OUTPUT_DIR = 'Characters'
    for superhero in char_list:
        charDict = {}
        paramsDict['query'] = superhero
        rt = requests.get(url = searchurl, headers = headers, params= paramsDict)
        rt = json.loads(rt.text)['results'][0]
        detail_url = rt['api_detail_url'] #can comment
        resp = requests.get(url = detail_url, params=paramsDict, headers = headers) ####
        try:
            resp = json.loads(resp.text)
        except:
            print(superhero)
            continue
        if resp['error'] != 'OK':
            continue
        resp = resp['results']

        for field in field_list:
                try:
                    charDict[field] = resp[field]
                    if field == 'description':
                        charDict[field] = remove_tags(charDict[field])
                        
                except:
                    charDict[field] = 'null'
        image_selector(charDict)
        get_bio(superhero, charDict)
        creatorList = []
        for creator in charDict['creators']:
            name = creator['name']
            creatorUrl = creator['api_detail_url']
            get_creator(creatorUrl,name)
            creatorList.append(name)

        charDict['creators'] = creatorList
        issueInfo = charDict['first_appeared_in_issue']
        get_issue(issueInfo['api_detail_url'], issueInfo['name'])
        charDict['first_appeared_in_issue'] = issueInfo['name']


        write_json_to_filesystem(OUTPUT_DIR,superhero,charDict)




def get_creator(url,name):
    creatorDict = {}
    creatorDict['name'] = name
    url = url.replace("creator", "person")
    params = {'api_key': '9df7c108bb78e94a0b082fc87c2c8ce8e116b73c',
    'format': 'json',
    'limit' :'1'
 }
    response = requests.get(url, headers = headers, params= params)
    try:
        resp = response.json()['results']
    except:
        print(name)
        return
             
    trait_list = ['aliases', 'birth', 'country','death','deck','description','hometown','image']
    for trait in trait_list:
        try:
            creatorDict[trait] = resp[trait]
        except:
            creatorDict[trait] = 'null'
    try:
        if creatorDict['death'] != 'null':
            creatorDict['death'] = resp['death']['date']
    except:
        creatorDict['death'] = 'null'

    creatorDict['description'] = remove_tags(creatorDict['description'])
    image_selector(creatorDict)
    OUTPUT_DIR = 'Creators'
    write_json_to_filesystem(OUTPUT_DIR,name,creatorDict)


def get_issue(url,name):
    issueDict = {}
    params = {'api_key': '9df7c108bb78e94a0b082fc87c2c8ce8e116b73c',
    'format': 'json',
    'limit' :'1'
    }
    url = url.replace("first_appeared_in_issue", "issue")
    response = requests.get(url, headers = headers, params= params)
    resp = response.json()['results']
    trait_list = ['cover_date', 'description', 'image','person_credits','character_credits','name','volume']
    for trait in trait_list:
        try:
            issueDict[trait] = resp[trait]
        except:
            issueDict[trait] = 'null'


    issueDict['description'] = remove_tags(issueDict['description'])
    tempList = []
    for character in issueDict['character_credits']:
        tempList.append(character['name'])
    issueDict['character_credits'] = tempList

    tempList2 = []
    for person in issueDict['person_credits']:
        tempList2.append(person['name'] + ":" + person['role'])
    issueDict['person_credits'] = tempList2
    try:
        issueDict['series'] = issueDict['volume']['name']
    except:
        issueDict['series'] = 'null'
    del issueDict['volume']

    image_selector(issueDict)
    OUTPUT_DIR = 'Issues'
    comic_name = name#issueDict['name']
    if comic_name == None:
        issueDict['name'] = name
    write_json_to_filesystem(OUTPUT_DIR,issueDict['name'],issueDict)





def clean_json(dictionary, traits):
    for trait in traits:
        
        if dictionary['trait'] is list:
            newList = []
        elif dictionary['trait'] is str:
            dictionary['trait'] = dictionary['trait'].replace("'","''")
            


def get_bio(heroName,charDict):
    ####superhero_API_Token = '2853740524719777'        
    super_url = 'https://superheroapi.com/api/2853740524719777/search/{}'.format(heroName)
    response = requests.get(super_url)
    try:
        response = response.json()
    except:
        print(heroName)
        return None
    if response['response'] == 'error':
        newName = heroName.replace("-", " ")
        super_url = 'https://superheroapi.com/api/2853740524719777/search/{}'.format(heroName)
        response = requests.get(super_url)
        try:
            response = response.json()
        except:
            print(heroName)
            return None
        if response['response'] == 'error':
            return None
    
        
    charInfo = response['results'][0]
    try:
        charDict['alignment'] = charInfo['biography']['alignment']
    except:
        charDict['alighment'] = 'null'
    
    try:
        charDict['appearance'] = charInfo['appearance']
    except:
        charDict['appearance'] = 'null'
    
    try:
        charDict['image'] = charInfo['image']['url']
    except:
        'donothing'


TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    try:
        string =  TAG_RE.sub('', text)[0:1000]
        string.replace("'", "''")
        return string
    except:
        return 'null'
    

def write_json_to_filesystem(OUTPUT_DIR_NAME,fileName, dictionary):
    try:
        fileName = fileName.replace("/", "-")
        author_file_path = os.path.join(OUTPUT_DIR_NAME,'{}.json'.format(fileName))
        with open(author_file_path, 'w+') as out_file:
            out_file.write(json.dumps(dictionary, sort_keys=True, indent=4 * ' '))
    except:
        return


def image_selector(imgDictionary):
    try:
        imgDictionary['image']= imgDictionary['image']['medium_url']
    except:
        try:
            imgDictionary['image'] = imgDictionary['image']['original_url']
        except:
            return
    
main()