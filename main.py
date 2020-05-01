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

from flask import Flask, request
from flask_cors import CORS

from Characters import Characters
from Authors import Authors
from Issues import Issues
from response_functions import responseFactory, sqlToDict
from database import database
from Search import searchFor

app = Flask(__name__)
CORS(app)


db = database.getInstance()
Characters(db)
Authors(db)
Issues(db)


@app.route('/listIssues')
def listIssues():
    issueObj = Issues.getInstance()
    return issueObj.listIssues()



@app.route('/listAuthors')
def listAuthors():
    authorObj = Authors.getInstance()
    return authorObj.listAuthors()


@app.route('/search/<string:term>/<int:pageNum>')
def searchPage(term, pageNum):
    return searchFor(db,term,pageNum)

@app.route('/search/<string:term>')
def search(term):
    return searchFor(db,term,1)
    
@app.route('/listChars')
def listChars():
    characterObj = Characters.getInstance()
    return characterObj.listChars()

@app.route('/characters')
def characters():
    headers = request.headers        
    characterObj = Characters.getInstance()
    return characterObj.charsPagedNEW(pageNum = 1, headers = headers)


@app.route('/authors')
def authors():
    headers = request.headers
    authorObj = Authors.getInstance()
    return authorObj.authorsPagedNEW(1,headers)  


@app.route('/issues')
def issues():
    headers = request.headers   
    issueObj = Issues.getInstance()
    return issueObj.IssuesPagedNEW(1, headers)

@app.route('/issue/<string:issueName>')
def issue(issueName):
    issueObj = Issues.getInstance()
    return issueObj.issue(issueName)


@app.route('/author/<string:authorName>')
def author(authorName):
    authorObj = Authors.getInstance()
    return authorObj.author(authorName)


@app.route('/character/<string:charName>')
def character(charName):
    characterObj = Characters.getInstance()
    return characterObj.character(charName)


@app.route('/authors/<int:pageNum>')
def authorsPagedNEW(pageNum):
    headers = request.headers 
    authorObj = Authors.getInstance()
    return authorObj.authorsPagedNEW(pageNum,headers)  



@app.route('/characters/<int:pageNum>')
def charsPagedNEW(pageNum):
    headers = request.headers        
    characterObj = Characters.getInstance()
    return characterObj.charsPagedNEW(pageNum, headers)


@app.route('/issues/<int:pageNum>')
def issuesPagedNew(pageNum):
    headers = request.headers    
    issueObj = Issues.getInstance()
    return issueObj.IssuesPagedNEW(pageNum,headers)


@app.route('/issue/Spider-Man! / The Bell Ringer / The Man in the Mummy Case / There are Martians Among Us')
def specialTempCase():
    issueName = 'Spider-Man! / The Bell Ringer / The Man in the Mummy Case / There are Martians Among Us'
    return issue(issueName)

@app.route('/issue/Tales of Suspense ')
def specialCase():
    issueName = 'Tales of Suspense #41 The Stronghold Of Dr. Strange!'
    return issue(issueName)


@app.route('/')
def root():
    return "Welcome to icdb API \n \n We are happy to have you!"
    
'''
@app.route('/init')
def init():
    from putInDatabase import start
    start()
    return "sucess!"
'''

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
