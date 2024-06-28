from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

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
        self.cursor = self.connection.cursor(dictionary=True)

    def query_events(self, where = None):
        query = 'SELECT * FROM fut_events'
        if where is not None:
            query += ' WHERE ' + where
        self.cursor.execute(query)
        rec = []
        for c in self.cursor:
            rec.append(c)
        return rec


def get_db_conn():
    global conn
    if not conn:
        pf = open('/run/secrets/db-password', 'r')
        password = pf.read().strip()
        pf.close()
        conn = DBManager(password=password)
    return conn

@app.route("/")
def default_route():
    return 'Invalid path', 400

@app.route("/events")
def list_events():
    rec = get_db_conn().query_events()
    return jsonify(rec)

@app.route("/events/current")
def current_events():
    rec = get_db_conn().query_events(where = 'NOW() BETWEEN reg_start_date AND reg_end_date')
    return jsonify(rec)
