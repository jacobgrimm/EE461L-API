import os
import json
from Charcters import Character


import sqlalchemy

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
                query = "INSERT INTO Issues(Title, Series, ReleaseDate, Description, ImageURL, Authors, Characters) values('{}','{}','{}','{}','{}','{{{}}}','{{{}}}');".format(
                    issueDict['name'], issueDict['series'],issueDict['cover_date'],issueDict['description'],issueDict['image'],'"person_credits": ' + json.dumps(issueDict['person_credits']),
                    '"character_credits": ' +json.dumps(issueDict['character_credits']))
                conn.execute(query)

    
    directories = ['Characters/']

    for directory in directories:
        with db.connect() as conn:
            for jsonFile in  os.listdir(directory):
                importantFile = open(directory + jsonFile)
                characterDict = json.load(importantFile)
                if 'appearance' not in characterDict:
                    characterDict['appearance'] = "none:null"
                if 'alignment' not in characterDict:
                    characterDict['alignment'] = 'null'
                query = "INSERT INTO Characters(HeroName, RealName, Aliases, Alignment, Appearance, Creators, Deck, Description, FirstAppearance, ImageURL) values('{}','{}','{}','{}','{{{}}}','{{{}}}','{}','{}','{}','{}');".format(
                    characterDict['name'],characterDict['real_name'],characterDict['aliases'],characterDict['alignment'],'"appearance": ' + json.dumps(characterDict['appearance']),
                    '"creators": ' +json.dumps(characterDict['creators']),characterDict['deck'],characterDict['description'],characterDict['first_appeared_in_issue'],characterDict['image'])
                conn.execute(query)
                

                #INSERT INTO Characters(HeroName, RealName, Aliases, Alignment, Appearance, Creators, Deck, Description, FirstAppearance, ImageURL) values();

    directories = ['Creators/']

    for directory in directories:
        with db.connect() as conn:
            for jsonFile  in  os.listdir(directory):
                importantFile = open(directory + jsonFile)
                authorDict = json.load(importantFile)
                query = "INSERT INTO Authors(Name, Aliases, Birth, Country, Death, Deck, Description, Hometown, ImageURL) values('{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(
                    authorDict['name'],authorDict['aliases'],authorDict['birth'],authorDict['country'],authorDict['death'],authorDict['deck'],authorDict['description'],authorDict['hometown'],authorDict['image'])
                conn.execute(query)

                #INSERT INTO Authors(Name, Aliases, Birth, Country, Death, Deck, Description, Hometown, ImageURL) values();


