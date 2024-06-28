from flask import Flask
import mysql.connector

app = Flask(__name__)
conn = None

class DBManager:
    def __init__(self, database='fut_public_be', host="db", user="root", password=None):
        self.connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor()

    def query_events(self):
        self.cursor.execute('SELECT title FROM fut_events')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec


@app.route("/")
def hello_world():
    global conn
    if not conn:
        pf = open('/run/secrets/db-password', 'r')
        password = pf.read().strip()
        pf.close()
        conn = DBManager(password=password)
    rec = conn.query_events()

    response = '<h1>events</h1>'
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>'
    return response
