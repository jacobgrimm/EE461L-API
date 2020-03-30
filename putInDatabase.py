import os
import json


import sqlalchemy

directory = 'Issues/'
for jsonFile  in  os.listdir(directory):
    importantFile = open(directory + jsonFile)
    issueDict = json.load(importantFile)
    newList = []
    for i in issueDict['character_credits']:
        newList.append(i.replace("'",""))
    issueDict['character_credits'] = newList
    newList2 = []
    for i in issueDict['person_credits']:
        newList2.append(i.replace("'",""))
    issueDict['person_credits'] = newList2

    issueDict['name'] = issueDict['name'].replace("'","")
    issueDict['series'] = issueDict['series'].replace("'","")
    issueDict['cover_date'] = issueDict['cover_date'].replace("'","")
    issueDict['description'] = issueDict['description'].replace("'","")


    with open(directory+jsonFile, 'w+') as out_file:
        out_file.write(json.dumps(issueDict, sort_keys=True, indent=4 * ' '))


print("INSERT INTO Issues(Title, Series, ReleaseDate, Description, ImageURL, Authors, Characters) values('{}','{}','{}','{}','{}','{{ {} }}','{{ {} }}');".format(
                    issueDict['name'], issueDict['series'],issueDict['cover_date'],issueDict['description'],issueDict['image'],json.dumps(issueDict['person_credits']),
                    json.dumps(issueDict['character_credits'])))




def start():
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



    directories = ['Issues/']

    for directory in directories:
        with db.connect() as conn:
            for jsonFile  in  os.listdir(directory):
                importantFile = open(directory + jsonFile)
                issueDict = json.load(importantFile)
                conn.execute("INSERT INTO Issues(Title, Series, ReleaseDate, Description, ImageURL, Authors, Characters) values('{}','{}','{}','{}','{}','{{ {} }}','{{ {} }}');".format(
                    issueDict['name'], issueDict['series'],issueDict['cover_date'],issueDict['description'],issueDict['image'],json.dumps(issueDict['person_credits']),
                    json.dumps(issueDict['character_credits']))
                
    )