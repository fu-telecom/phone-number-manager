from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import mysql.connector
import re
import requests

#### static config ####
# Maximum length (adjust as needed)
caller_id_max_length = 16

RESERVED_NUMBERS = [
    "0",
    "1",
    "100",
    "1000",
    "101",
    "105",
    "111",
    "120",
    "123",
    "2",
    "222",
    "22222222221",
    "2278",
    "3",
    "321",
    "333",
    "3802",
    "3803",
    "3804",
    "3805",
    "3806",
    "3882278",
    "4",
    "4383858",
    "4444",
    "5",
    "500",
    "5454",
    "6",
    "6369",
    "7",
    "76382533",
    "8",
    "878685",
    "9",
    "900",
    "902",
    "911"
]

# load secrets
with open('/run/secrets/recaptcha-secret', 'r') as file:
    recaptcha_secret_key = file.read().strip()


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

    def query_regs(self, event_id):
        query = 'SELECT * FROM service_signups WHERE fut_event_id = %s'
        values = [event_id]
        self.cursor.execute(query, values)
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


def verify_recaptcha(recaptcha_response):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    params = {'secret': recaptcha_secret_key, 'response': recaptcha_response}
    response = requests.post(url, params=params, verify=True)
    data = json.loads(response.text)
    return data['success']


def validate_cnam(caller_id_name):
    """Validates a caller ID name based on basic CNAM standards.
    Args:
    caller_id_name: The caller ID name to be validated.
    Returns:
    A tuple containing:
        - A boolean indicating whether the name is valid.
        - A suggested caller ID name if invalid, otherwise the original name.
    """
    suggested_name = None
    if re.match(r'^[a-zA-Z0-9 -]+$', caller_id_name):
        suggested_name = caller_id_name
    else:
        # Remove invalid characters
        suggested_name = re.sub(r'[^a-zA-Z0-9 -]', '', caller_id_name).strip()
    # check max length
    if len(suggested_name) > caller_id_max_length:
        suggested_name = suggested_name[:caller_id_max_length]  # Truncate if too long
    return (caller_id_name == suggested_name), suggested_name


def text_to_phone_number(text):
    """Converts a string of text into its phone number equivalent using phone keypad mappings.
    Args:
    text: The input text string.
    Returns:
    A string representing the phone number equivalent.
    """
    phone_keypad = {
        '2': 'abc',
        '3': 'def',
        '4': 'ghi',
        '5': 'jkl',
        '6': 'mno',
        '7': 'pqrs',
        '8': 'tuv',
        '9': 'wxyz'
    }
    phone_number = ''
    for char in text.lower():
        if char.isdigit():
            phone_number += char
        elif char.isalpha():
            for key, values in phone_keypad.items():
                if char in values:
                    phone_number += key
                    break
    return phone_number


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

@app.get("/events/<int:event_id>/regs")
def list_regs(event_id):
    rec = get_db_conn().query_regs(event_id)
    return jsonify(rec)


@app.post("/events/<int:event_id>/regs")
def submit_reg(event_id):
    data = request.form
    invalid_reasons = []

    # validate CAPTCHA
    recaptcha_response = data.get('g-recaptcha-response')
    if not verify_recaptcha(recaptcha_response):
        invalid_reasons.append('Invalid reCAPTCHA')

    # validate desired caller ID
    desired_caller_id = data.get("desired_callerid")
    valid_caller_id, suggested_caller_id = validate_cnam(desired_caller_id)
    if not valid_caller_id:
        invalid_reasons.append(f"Who wants a caller ID like '{desired_caller_id}' ? It would be much better to use '{suggested_caller_id}'")

    # validate desired number
    desired_phone_number = text_to_phone_number(data.get("desired_number"))
    if desired_phone_number in RESERVED_NUMBERS:
        invalid_reasons.append(f"You can't have the number {desired_phone_number}, it's already taken.")

    # final validity check
    if invalid_reasons:
        return jsonify({'success': False, 'message': '; '.join(invalid_reasons)}), 400
    # proceed with submission
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
        data.get("contact_name"), data.get("contact_phone"), data.get("contact_email"), desired_phone_number,
        desired_caller_id, own_phone, data.get("message", "")
    )
    db_conn = get_db_conn()
    db_conn.cursor.execute(insert_query, insert_values)
    db_conn.connection.commit()
    # TODO: add error handling
    return jsonify({
        "success": True,
        "message": "success"
    })
