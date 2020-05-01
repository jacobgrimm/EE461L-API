import datetime
import json
import os
import sqlalchemy

from flask import Flask, render_template, redirect, url_for, make_response, request
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

    def listChars(self):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT HeroName FROM Authors;")
        a = sqlToDict(resultproxy)
        charList = [i['HeroName'] for i in a]
        resp = {'Response': 'Success', 'Result': charList}
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def charsPagedNEW(self, pageNum, headers):
        conn = self.__db.connect()
        if 'sort' in headers:
            #sortdir is true for descending, false for ascensding
            answer = 'ASC'
            if headers['sort'] == 'False':
                answer = 'DESC'
            resultproxy = conn.execute("SELECT * FROM Authors ORDER BY HeroName {}".format(answer))
        else:
            resultproxy = conn.execute("SELECT * FROM Authors")


        if 'filter' in headers:
            return responseFactory.NEWpagedRequestRespond(resultproxy,pageNum,self.__characterFormat,headers, filterType=self.__charFilter)

        return responseFactory.NEWpagedRequestRespond(resultproxy,pageNum,self.__characterFormat, headers= headers)    

    
    def character(self, charName):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT * FROM Authors WHERE HeroName = '{}'".format(charName))
        return responseFactory.NEWindividualRequestRespond(resultproxy,charName,self.__characterFormat)



    def __characterFormat(self,SQLresponse):
        SQLresponse['first_appeared_in_issue'] = SQLresponse['FirstAppearance'].replace('\"','"')
        del(SQLresponse['FirstAppearance'])
        SQLresponse['creators'] = SQLresponse['Creators'].replace('\"','"')
        SQLresponse['creators'] = (json.loads(SQLresponse['creators']))['creators']
        del SQLresponse['Creators']
        SQLresponse['appearance'] = SQLresponse['Appearance'].replace('\"','"')
        SQLresponse['appearance'] = (json.loads(SQLresponse['appearance']))['appearance']
        del SQLresponse['Appearance']
        SQLresponse['image'] = SQLresponse['ImageURL']
        del(SQLresponse['ImageURL'])
        lowered_resp = dict((k.lower(), v) for k,v in SQLresponse.items())
        lowered_resp['name']= lowered_resp['heroname']
        del lowered_resp['heroname']
        lowered_resp['real_name']= lowered_resp['realname']
        del lowered_resp['realname']
        link_info = self.__linkCharacter(lowered_resp['name'])
        lowered_resp['issues'] = link_info[0]
        lowered_resp['authors'] = link_info[1]

        return lowered_resp

    def __linkCharacter(self,HeroName):
        conn = self.__db.connect()
        resultproxy2 = conn.execute("SELECT Title, Authors FROM Issues WHERE JSON_SEARCH(Authors, 'all', '{}') > 1;".format(HeroName))

        titles =[]
        authors =[]
        for row in resultproxy2:
            titles.append(row[0])
            author = json.loads(row[1])
            authors.extend(author['person_credits'])
        authors = list(dict.fromkeys(authors))
        result = (titles, authors)
        return result

    def __charFilter(self, a, term):
        b = []
        term = term.lower()
        for entry in a:
            beenAdded = False
            if term in entry['name'].lower():
                b.append(entry)
                beenAdded = True
                continue
            if not beenAdded:
                for author in entry['authors']:
                    if term in author.lower():
                        b.append(entry)
                        beenAdded = True
                        continue
            if not beenAdded:
                for issue in entry['issues']:
                    if term in issue.lower():
                        b.append(entry)
                        continue
        return b


