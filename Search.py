from response_functions import sqlToDict, responseFactory
#import sqlalchemy
from flask import make_response
import json
def searchFor(db,term, pageNum):
    resp = {'response' : 'Success',
    'page_num' : pageNum,
    'results': ''
    }

    conn = db.connect()

    issueResultproxy = conn.execute("""SELECT Title, MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE) AS score FROM Issues WHERE MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE);""".format(term,term))
    issueResults = sqlToDict(issueResultproxy)
    for issueDict in issueResults:
        issueDict['type'] = 'issue'
        issueDict['name'] = issueDict['Title'].replace('\"','"')
        del(issueDict['Title'])

        
    charResultproxy = conn.execute("""SELECT HeroName, MATCH(HeroName, RealName, Aliases) AGAINST('{}' IN NATURAL LANGUAGE MODE) AS score FROM Characters WHERE MATCH(HeroName, RealName, Aliases) AGAINST('{}' IN NATURAL LANGUAGE MODE);""".format(term,term))
    charResults = sqlToDict(charResultproxy)
    for charDict in charResults:
        charDict['type'] = 'character'
        charDict['name']= charDict['HeroName']
        del charDict['HeroName']


    authorResultproxy = conn.execute("""SELECT Name, MATCH(Name, Aliases) AGAINST('{}' IN NATURAL LANGUAGE MODE) AS score FROM Authors WHERE MATCH(Name, Aliases) AGAINST('{}' IN NATURAL LANGUAGE MODE);""".format(term,term))
    authorResults = sqlToDict(authorResultproxy)
    for authorDict in authorResults:
        authorDict['type'] = 'author'
        authorDict['name']= authorDict['Name']
        del authorDict['Name']

    
    results = issueResults + charResults + authorResults

    if len(results) == 0 :
        resp['response'] = "term '{}' not found in database".format(term)
        resp['result'] = 'null'
        resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    finalResults = sorted(results, key=lambda k: k['score'], reverse = True) 

    
    info = responseFactory.NEWpageBounds(pageNum,len(finalResults))


    if info == None:
        resp['response'] = 'Invalid Page Request'
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
    bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2]
    final_list = []
    for entry in finalResults[bottomIndex:topIndex]:
        del(entry['score'])
        final_list.append(entry)
    resp['results'] = final_list
    resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

