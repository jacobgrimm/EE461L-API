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

from flask import Flask, render_template, redirect, url_for, make_response

app = Flask(__name__)


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

@app.route('/characters')
def characters():
    return pagedRequestRespond('Characters/',1)        

@app.route('/character1/<string:charName>')
def characterFind(charName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Characters WHERE HeroName = '{}'".format(charName))
    return NEWindividualRequestRespond(resultproxy,charName,characterFormat)


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

    return lowered_resp

@app.route('/characters_new')
def characters1():

    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Characters")
    return NEWpagedRequestRespond(resultproxy,1,characterFormat)    


@app.route('/authors_new')
def authors3():

    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Authors")
    return NEWpagedRequestRespond(resultproxy,pageNum=1,formatter=authorFormat)


@app.route('/issues')
def issues():
    return pagedRequestRespond('Issues/',1)


@app.route('/authors')
def authors():
    return pagedRequestRespond('Creators/',1)


def authorFormat(SQLresponse):
    SQLresponse['image'] = SQLresponse['ImageURL']
    del(SQLresponse['ImageURL'])
    lowered_resp = dict((k.lower(), v) for k,v in SQLresponse.items())
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


@app.route('/issues_new')
def issues2():
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Issues")
    return NEWpagedRequestRespond(resultproxy,pageNum=1,formatter=issueFormat)


@app.route('/issue1/<string:issueName>')
def issue3(issueName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Issues WHERE Title = '{}'".format(issueName))
    return NEWindividualRequestRespond(resultproxy,issueName,issueFormat)


@app.route('/author1/<string:authorName>')
def authornew(authorName):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Authors WHERE Name = '{}'".format(authorName))
    return NEWindividualRequestRespond(resultproxy,authorName,authorFormat)


@app.route('/characters/<int:pageNum>')
def charsPaged(pageNum):
    return pagedRequestRespond(directory= 'Characters/',pageNum=pageNum)


@app.route('/authors/<int:pageNum>')
def authorsPaged(pageNum):
    return pagedRequestRespond(directory= 'Creators/',pageNum=pageNum)


@app.route('/issues/<int:pageNum>')
def issuesPaged(pageNum):
    return pagedRequestRespond(directory= 'Issues/',pageNum=pageNum)


@app.route('/authors_new/<int:pageNum>')
def authorsPagedNEW(pageNum):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Authors WHERE Name = '{}'".format(authorName))
    return NEWpagedRequestRespond(resultproxy,pageNum=pageNum, formatter=authorFormat)


@app.route('/characters_new/<int:pageNum>')
def charsPagedNEW(pageNum):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Characters")
    return NEWpagedRequestRespond(resultproxy,pageNum,characterFormat)    


@app.route('/issues_new/<int:pageNum>')
def issuesPagedNew(pageNum):
    conn = db.connect()
    resultproxy = conn.execute("SELECT * FROM Issues")
    return NEWpagedRequestRespond(resultproxy,pageNum,issueFormat)


@app.route('/character/<string:charName>')
def character(charName):
    return individualRequestRespond('Characters/',charName)


@app.route('/issue/<string:issueName>')
def issue(issueName):
    return individualRequestRespond('Issues/',issueName)


@app.route('/author/<string:authorName>')
def author(authorName):
    return individualRequestRespond('Creators/',authorName)


def NEWpagedRequestRespond(resultproxy, pageNum,formatter):
    
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

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
    for author in a[bottomIndex:topIndex]:
        final_list.append(formatter(author))
    resp['results'] = final_list
    resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def pagedRequestRespond(directory, pageNum):
    info = pageBounds(pageNum,directory)
    resp = {'response' : 'Success',
            'page_num' : pageNum,
            'results': ''}
    if info == None:
        resp['response'] = 'Invalid Page Request'
        resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'

        return resp
    
    filesInDir, bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2], info[3]
    
    array = []
    for jsonFile  in  filesInDir[bottomIndex:topIndex]:
        importantFile = open(directory + jsonFile)
        array.append( (json.load(importantFile))  )
    
    resp['results'] = array
    resp = make_response(json.dumps(resp, indent=4, sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def individualRequestRespond(directory, desiredResource):
    resp = {'response' : 'Resource {} Not Found'.format(desiredResource),
            'results': 'Please Verify desired resource is present in our database and spelled correctly'}

    
    for jsonFile  in  os.listdir(directory):
        name = jsonFile.split('.')[0]
        if desiredResource == name:
            resourceFile = open(directory + jsonFile)
            resp['results'] = json.load(resourceFile)
            resp['response'] = 'Success'
            resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        
    resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def NEWpageBounds(pageNum, numFiles):
    pageNum -= 1
    numPages = int(numFiles/5) +1
    filesPerPage = int(numFiles/numPages)
    if pageNum <0 or pageNum >numPages:
        return None
        
    bottomIndex = pageNum * filesPerPage
    topIndex = (pageNum+1) * filesPerPage
    return(bottomIndex,topIndex,numPages+1)


def pageBounds(pageNum, directory):
    pageNum -= 1
    filesInDir = sorted(os.listdir(directory))
    numFiles = len(filesInDir)
    numPages = int(numFiles/5) +1
    filesPerPage = int(numFiles/numPages)
    if pageNum <0 or pageNum >numPages:
        return None
        
    bottomIndex = pageNum * filesPerPage
    topIndex = (pageNum+1) * filesPerPage
    return( filesInDir, bottomIndex,topIndex,numPages+1)
    

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
