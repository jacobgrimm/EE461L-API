import json

from flask import  make_response
from response_functions import sqlToDict, responseFactory


class Issues:
    __instance = None
    __db = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Issues.__instance == None:
            Issues()
        return Issues.__instance
    def __init__(self,db):
        """ Virtually private constructor. """
        if Issues.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Issues.__instance = self
            Issues.__db = db

    def listIssues(self):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT Title FROM Issues;")
        a = sqlToDict(resultproxy)
        issueList = [i['Title'] for i in a]
        resp = {'Response': 'Success', 'Result': issueList}
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def IssuesPagedNEW(self, pageNum, headers):
        if 'filter' in headers:
            return self.__issueFilter(headers,pageNum)
        conn = self.__db.connect()
        if 'sort' in headers:
            answer = 'ASC'
            if headers['sort'] == 'False':
                answer = 'DESC'
            resultproxy = conn.execute("SELECT * FROM Issues ORDER BY Title {}".format(answer))
        else:
            resultproxy = conn.execute("SELECT * FROM Issues")
            
        return responseFactory.NEWpagedRequestRespond(resultproxy,pageNum=pageNum,formatter=self.__issueFormat, headers= headers)

    
    def issue(self, issueName):
        conn = self.__db.connect()
        resultproxy = conn.execute("SELECT * FROM Issues WHERE Title = '{}'".format(issueName))
        return responseFactory.NEWindividualRequestRespond(resultproxy,issueName,self.__issueFormat)



    def __issueFormat(self,SQLresponse):
        SQLresponse['name'] = SQLresponse['Title'].replace('\"','"')
        del(SQLresponse['Title'])
        SQLresponse['cover_date'] = SQLresponse['ReleaseDate']
        del SQLresponse['ReleaseDate']
        SQLresponse['character_credits'] = SQLresponse['Characters'].replace('\"','"')
        SQLresponse['character_credits'] = (json.loads(SQLresponse['character_credits']))['character_credits']
        del SQLresponse['Characters']
        SQLresponse['person_credits'] = SQLresponse['Authors'].replace('\"','"')
        SQLresponse['person_credits'] = (json.loads(SQLresponse['person_credits']))['person_credits']
        del SQLresponse['Authors']
        SQLresponse['image'] = SQLresponse['ImageURL']
        del(SQLresponse['ImageURL'])
        lowered_resp = dict((k.lower(), v) for k,v in SQLresponse.items())
        return lowered_resp


    def __filter_response(self,resultproxy, formatter):
        a = sqlToDict(resultproxy)
        b = []
        for i in a:
            b.append(formatter(i))
        a = b
        return a


    def __issueFilter(self,headers,pageNum):
        conn =self.__db.connect()
        filter_ = headers['filter']
        string1 = "SELECT * FROM Issues WHERE JSON_SEARCH(LOWER(Authors), 'all', LOWER('%%{}%%')) > 1;".format(filter_)
        string2 = "SELECT * FROM Issues WHERE JSON_SEARCH(LOWER(Characters), 'all', LOWER('%%{}%%')) > 1;".format(filter_)
        resultproxy1  = conn.execute(string1)
        a = self.__filter_response(resultproxy1,self.__issueFormat)
        resultproxy2 = conn.execute(string2)
        b = self.__filter_response(resultproxy2, self.__issueFormat)
        resultproxy3 =  conn.execute("""SELECT *, MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE) AS score FROM Issues WHERE MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE);""".format(filter_,filter_))
        c = self.__filter_response(resultproxy3, self.__issueFormat)
        for entry in c:
            del entry['score']
        d = a + b + c
        return responseFactory.constructIssueFilterResponse(d,headers,pageNum)