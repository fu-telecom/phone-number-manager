from flask import Flask, jsonify, request
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

@app.post("/events/<int:event_id>/regs")
def submit_reg(event_id):
    data = request.form
    insert_query = """
    INSERT INTO service_signups (
        fut_event_id, camp_name, camp_lead_name, camp_lead_phone, camp_lead_email,
        submitter_name, submitter_phone, submitter_email, desired_number, desired_callerid,
        own_phone, message
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    own_phone = 1 if data.get("own_phone", "").lower() == "user-provided" else 0
    insert_values = (
        event_id, data.get("camp_name"), data.get("lead_name"), data.get("lead_phone"), data.get("lead_email"),
        data.get("contact_name"), data.get("contact_phone"), data.get("contact_email"), data.get("desired_number"),
        data.get("desired_callerid"), own_phone, data.get("message", "")
    )
    db_conn = get_db_conn()
    db_conn.cursor.execute(insert_query, insert_values)
    db_conn.connection.commit()
    # TODO: add error handling
    return jsonify({
        "message": "success"
    })
