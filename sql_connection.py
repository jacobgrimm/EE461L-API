import sqlalchemy
import pymysql





cloud_sql_connection_name = 'icdb-sql:us-central1:mysql-test'
db_user = 'root'
db_pass = 'icdbmysql'
db_name = 'icdb'

connection = pymysql.connect(host = '127.0.0.1',
user= db_user,
password = db_pass,
db = db_name)

exit()
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
    ,echo = True
)


with db.connect() as conn:
    #answer = conn.execute('SELECT * FROM *')
    print(None)