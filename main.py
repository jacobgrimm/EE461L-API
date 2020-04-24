# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_render_template]
import datetime
import json
import os
import sqlalchemy

from flask import Flask, render_template, redirect, url_for, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


cloud_sql_connection_name = 'icdb-sql:us-central1:mysql-test'
db_user = 'root'
db_pass = 'icdbmysql'
db_name = 'icdb'
db = sqlalchemy.create_engine(
# Equivalent URL:
# mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
sqlalchemy.engine.url.URL(
    drivername="mysql+pymysql",
    username=db_user,
    password=db_pass,
    database=db_name,

    query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
)
)

@app.route('/')
def root():
    characters = []
    for jsonFile  in  os.listdir('Characters'):
        characters.append(jsonFile.split('.json')[0])
    issues = []
    for jsonFile  in  os.listdir('Issues'):
        issues.append(jsonFile.split('.json')[0])
    creators = []
    for jsonFile  in  os.listdir('Creators'):
        creators.append(jsonFile.split('.json')[0])

    


    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    return render_template(
        'index.html', times=characters, issues = issues, authors = creators)

'''
@app.route('/init')
def init():
    from putInDatabase import start
    start()
    return "sucess!"
'''
@app.route('/listIssues')
def listIssues():
    conn = db.connect()
    resultproxy = conn.execute("SELECT Title FROM Issues;")
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    issueList = [i['Title'] for i in a]
    resp = {'Response': 'Success', 'Result': issueList}
    resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp





@app.route('/listAuthors')
def listAuthors():
    conn = db.connect()
    resultproxy = conn.execute("SELECT Name FROM Authors;")
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    nameList = [i['Name'] for i in a]
    resp = {'Response': 'Success', 'Result': nameList}
    resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp



def sqlToDict(resultproxy):
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    return a


@app.route('/search/<string:term>/<int:pageNum>')
def searchPage(term, pageNum):
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

    
    info = NEWpageBounds(pageNum,len(finalResults))


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


@app.route('/search/<string:term>')
def search(term):
    return searchPage(term,1)
    





@app.route('/listChars')
def listChars():
    conn = db.connect()
    resultproxy = conn.execute("SELECT HeroName FROM Characters;")
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    charList = [i['HeroName'] for i in a]
    resp = {'Response': 'Success', 'Result': charList}
    resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp






@app.route('/characters')
def characters():
    headers = request.headers        
    conn = db.connect()
    if 'sort' in headers:
        #sortdir is true for descending, false for ascensding
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Characters ORDER BY HeroName {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Characters")

    if 'filter' in headers:
        return NEWpagedRequestRespond(resultproxy,1,characterFormat,headers, filterType=charFilter)

    return NEWpagedRequestRespond(resultproxy,1,characterFormat,headers)    


@app.route('/authors')
def authors():
    headers = request.headers        
    conn = db.connect()
    if 'sort' in headers:
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Authors ORDER BY Name {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Authors")
        
    if 'filter' in headers:
        return NEWpagedRequestRespond(resultproxy,1,authorFormat,headers, filterType=authorFilter)

    return NEWpagedRequestRespond(resultproxy,pageNum=1,formatter=authorFormat,headers= headers)


@app.route('/issues')
def issues():
    headers = request.headers        
    conn = db.connect()

    if 'filter' in headers:
        return issueFilter(headers,conn,1)



    if 'sort' in headers:
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Issues ORDER BY Title {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Issues")
        
        

 

    return NEWpagedRequestRespond(resultproxy,pageNum=1,formatter=issueFormat, headers= headers)


@app.route('/issue/<string:issueName>')
def issue(issueName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Issues WHERE Title = '{}'".format(issueName))
    return NEWindividualRequestRespond(resultproxy,issueName,issueFormat)


@app.route('/author/<string:authorName>')
def author(authorName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Authors WHERE Name = '{}'".format(authorName))
    return NEWindividualRequestRespond(resultproxy,authorName,authorFormat)


@app.route('/character/<string:charName>')
def character(charName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Characters WHERE HeroName = '{}'".format(charName))
    return NEWindividualRequestRespond(resultproxy,charName,characterFormat)


@app.route('/authors/<int:pageNum>')
def authorsPagedNEW(pageNum):
    headers = request.headers        
    conn = db.connect()
    if 'sort' in headers:
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Authors ORDER BY Name {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Authors")

    if 'filter' in headers:
        return NEWpagedRequestRespond(resultproxy,pageNum,authorFormat,headers, filterType=authorFilter)


    return NEWpagedRequestRespond(resultproxy,pageNum=pageNum, formatter=authorFormat,headers=headers)


@app.route('/characters/<int:pageNum>')
def charsPagedNEW(pageNum):
    headers = request.headers        
    conn = db.connect()
    if 'sort' in headers:
        #sortdir is true for descending, false for ascensding
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Characters ORDER BY HeroName {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Characters")


    if 'filter' in headers:
        return NEWpagedRequestRespond(resultproxy,pageNum,characterFormat,headers, filterType=charFilter)

    return NEWpagedRequestRespond(resultproxy,pageNum,characterFormat, headers= headers)    


@app.route('/issues/<int:pageNum>')
def issuesPagedNew(pageNum):
    headers = request.headers        
    conn = db.connect()

    if 'filter' in headers:
        return issueFilter(headers,conn,pageNum)


    if 'sort' in headers:
        answer = 'ASC'
        if headers['sort'] == 'False':
            answer = 'DESC'
        resultproxy = conn.execute("SELECT * FROM Issues ORDER BY Title {}".format(answer))
    else:
        resultproxy = conn.execute("SELECT * FROM Issues")

    return NEWpagedRequestRespond(resultproxy,pageNum,issueFormat, headers= headers)


def authorFormat(SQLresponse):
    SQLresponse['image'] = SQLresponse['ImageURL']
    del(SQLresponse['ImageURL'])
    lowered_resp = dict((k.lower(), v) for k,v in SQLresponse.items())
    link_info = linkAuthor(lowered_resp['name'])
    lowered_resp['issues'] = link_info[0]
    lowered_resp['characters'] = link_info[1]

    return lowered_resp


def issueFormat(SQLresponse):
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


def characterFormat(SQLresponse):
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
    link_info = linkCharacter(lowered_resp['name'])
    lowered_resp['issues'] = link_info[0]
    lowered_resp['authors'] = link_info[1]

    return lowered_resp


def filter_response(resultproxy, formatter):
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    b = []
    for i in a:
        b.append(formatter(i))
    a = b
    return a

def charFilter(a, term):
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

def authorFilter(a, term):
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


def issueFilter(headers,conn,pageNum):
    filter_ = headers['filter']
    string1 = "SELECT * FROM Issues WHERE JSON_SEARCH(LOWER(Authors), 'all', LOWER('%%{}%%')) > 1;".format(filter_)
    string2 = "SELECT * FROM Issues WHERE JSON_SEARCH(LOWER(Characters), 'all', LOWER('%%{}%%')) > 1;".format(filter_)
    resultproxy1  = conn.execute(string1)
    a = filter_response(resultproxy1,issueFormat)
    resultproxy2 = conn.execute(string2)
    b = filter_response(resultproxy2, issueFormat)
    resultproxy3 =  conn.execute("""SELECT *, MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE) AS score FROM Issues WHERE MATCH(Title, Series) AGAINST('{}' IN NATURAL LANGUAGE MODE);""".format(filter_,filter_))
    c = filter_response(resultproxy3, issueFormat)
    for entry in c:
        del entry['score']
    d = a + b + c
    if 'sort' in headers:
        reverse = True
        if headers['sort'] == 'False':
            reverse = False
            d = sorted(d, key=lambda k: k['name'], reverse = reverse)
    else:
            d = sorted(d, key=lambda k: k['name'])
    
    #remove duplicates
    temp = []
    prev = 'TEMP_ISSUE'
    for entry in d:
        if prev != entry['name']:
            temp.append(entry)
        prev = entry['name']
    a = temp


    info= NEWpageBounds(pageNum,len(a))

    resp = {'response' : 'Success',
    'page_num' : pageNum,
    'results': ''
    }
    if info == None:
        resp['response'] = 'Invalid Page Request'
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
    bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2]
    final_list = []
    for entry in a[bottomIndex:topIndex]:
        final_list.append((entry))
    resp['results'] = final_list
    resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'filter'
    resp.headers['Access-Control-Request-Method'] = 'GET'
    return resp

        



def NEWpagedRequestRespond(resultproxy, pageNum,formatter, headers,filterType = None):
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    b = []
    for i in a:
        b.append(formatter(i))
    a = b

    if 'filter' in headers:
        a = filterType(a, headers['filter'])

    info= NEWpageBounds(pageNum,len(a))


    resp = {'response' : 'Success',
    'page_num' : pageNum,
    'results': ''
    }
    if info == None:
        resp['response'] = 'Invalid Page Request'
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
    bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2]
    final_list = []
    for entry in a[bottomIndex:topIndex]:
        final_list.append((entry))
    resp['results'] = final_list
    resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'filter'
    resp.headers['Access-Control-Request-Method'] = 'GET'


    return resp


def NEWpageBounds(pageNum, numFiles):
    pageNum -= 1
    filesPerPage = 9
    numPages =  int(numFiles / filesPerPage) 
    if (numFiles % filesPerPage) != 0:
         numPages+=1
    if pageNum <0 or pageNum >numPages:
        return None
        
    bottomIndex = pageNum * filesPerPage
    topIndex = (pageNum+1) * filesPerPage
    return(bottomIndex,topIndex,numPages)


def NEWindividualRequestRespond(resultproxy, resourceName, formatter):
    resp = {'response' : 'Resource {} Not Found'.format(resourceName),
        'results': 'Please Verify desired resource is present in our database and spelled correctly'}

    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

    if a == []:
        resp = make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:    
        resp['results'] =formatter(a[0])
        resp['response'] = 'Success'
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

def linkCharacter(HeroName):
    conn = db.connect()
    resultproxy2 = conn.execute("SELECT Title, Authors FROM Issues WHERE JSON_SEARCH(Characters, 'all', '{}') > 1;".format(HeroName))

    titles =[]
    authors =[]
    for row in resultproxy2:
        titles.append(row[0])
        author = json.loads(row[1])
        authors.extend(author['person_credits'])
    authors = list(dict.fromkeys(authors))
    result = (titles, authors)
    return result

def linkAuthor(Name):
    conn = db.connect()
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


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
