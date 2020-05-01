import json

from flask import  make_response
from response_functions import sqlToDict, responseFactory


class Authors:
    __instance = None
    __db = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Authors.__instance == None:
            Authors()
        return Authors.__instance
    def __init__(self,db):
        """ Virtually private constructor. """
        if Authors.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Authors.__instance = self
            Authors.__db = db

    def listAuthors(self):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT Name FROM Authors;")
        a = sqlToDict(resultproxy)
        nameList = [i['Name'] for i in a]
        resp = {'Response': 'Success', 'Result': nameList}
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def authorsPagedNEW(self, pageNum, headers):
        conn = self.__db.connect()
        if 'sort' in headers:
            answer = 'ASC'
            if headers['sort'] == 'False':
                answer = 'DESC'
            resultproxy = conn.execute("SELECT * FROM Authors ORDER BY Name {}".format(answer))
        else:
            resultproxy = conn.execute("SELECT * FROM Authors")

        if 'filter' in headers:
            return responseFactory.NEWpagedRequestRespond(resultproxy,pageNum,self.__authorFormat,headers, filterType=self.__authorFilter)


        return responseFactory.NEWpagedRequestRespond(resultproxy,pageNum=pageNum, formatter=self.__authorFormat,headers=headers)

    
    def author(self, authorName):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT * FROM Authors WHERE Name = '{}'".format(authorName))
        return responseFactory.NEWindividualRequestRespond(resultproxy,authorName,self.__authorFormat)



    def __authorFormat(self,SQLresponse):
        SQLresponse['image'] = SQLresponse['ImageURL']
        del(SQLresponse['ImageURL'])
        lowered_resp = dict((k.lower(), v) for k,v in SQLresponse.items())
        link_info = self.__linkAuthor(lowered_resp['name'])
        lowered_resp['issues'] = link_info[0]
        lowered_resp['characters'] = link_info[1]

        return lowered_resp

    def __linkAuthor(self, Name):
        conn = self.__db.connect()
        resultproxy2 = conn.execute("SELECT Title, Characters FROM Issues WHERE JSON_SEARCH(Authors, 'all', '{}%%') > 1;".format(Name))

        titles =[]
        characters =[]
        for row in resultproxy2:
            titles.append(row[0])
            character = json.loads(row[1])
            characters.extend(character['character_credits'])
        characters = list(dict.fromkeys(characters))
        result = (titles, characters)
        return result

    def __authorFilter(self, a, term):
        b = []
        term = term.lower()
        for entry in a :
            beenAdded = False
            if term in entry['name'].lower():
                b.append(entry)
                beenAdded = True
            if not beenAdded:
                for character in entry['characters']:
                    if term in character.lower():
                        b.append(entry)
                        beenAdded = True
                        continue
            if not beenAdded:
                for issue in entry['issues']:
                    if term in issue.lower():
                        b.append(entry)
                        continue
        return b

