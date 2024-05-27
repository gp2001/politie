from flask import Flask, request, jsonify
import spacy
import sqlite3
import json
from datetime import datetime
import re

app = Flask(__name__)
# Load the Dutch SpaCy model
nlp = spacy.load("nl_core_news_sm")

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meldingen (
            id INTEGER PRIMARY KEY,
            source_id TEXT,
            datetime TEXT,
            status TEXT DEFAULT '',
            priority TEXT DEFAULT '',
            description TEXT DEFAULT ''
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS berichten (
            id INTEGER PRIMARY KEY,
            melding_id INTEGER,
            time TEXT,
            content TEXT,
            enrichment TEXT,
            FOREIGN KEY(melding_id) REFERENCES meldingen(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY,
            message_id INTEGER,
            key TEXT,
            value TEXT,
            FOREIGN KEY(message_id) REFERENCES messages(id)
        )
    ''')
    conn.commit()
    conn.close()

# Function to generate source_id for meldingen
def generate_source_id():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM meldingen')
    count = cursor.fetchone()[0]
    conn.close()
    return f'melding {count + 1}'

@app.route('/')
def home():
    return "Welcome to the PoC API!"

# Function to split text based on the custom splitting logic
def split_text(content):
    return content.split("--------------------------------------------------------------")

# Function to extract messages from content
def extract_messages(content):
    matches = re.finditer(r'(\d{1,2}:\d{2})\s(.*?)(?=\s\d{1,2}:\d{2}|$)', content)
    messages = []
    for match in matches:
        time = match.group(1)
        message_text = match.group(2)
        messages.append((time, message_text.strip()))
    return messages

# Function to enrich message using SpaCy
def enrich_message(message):
    time = message[0]
    content = message[1]
    doc = nlp(content)
    return {
        'time': time,
        'content': content,
        'entities': [(ent.text, ent.label_) for ent in doc.ents]
    }

# Function to create a melding in the database
def create_melding_in_database(melding_content, source_id):
    datetime_now = datetime.utcnow().isoformat()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert the melding in the meldingen table
    cursor.execute('''
        INSERT INTO meldingen (source_id, datetime) 
        VALUES (?, ?)
    ''', (source_id, datetime_now))
    melding_id = cursor.lastrowid

    # Extract messages from melding_content
    messages = extract_messages(melding_content)

    # Insert messages in the berichten table
    for time, message_content in messages:
        doc = nlp(message_content)
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        cursor.execute('''
            INSERT INTO berichten (melding_id, time, content, enrichment)
            VALUES (?, ?, ?, ?)
        ''', (melding_id, time, message_content, json.dumps(entities)))

    conn.commit()
    conn.close()

# Endpoint to create melding from a kladblok
@app.route('/meldingen/kladblok', methods=['POST'])
def create_meldingen_from_kladblok():
    data = request.json
    kladblok_content = data.get('kladblok_content')

    # Split the kladblok into individual meldingen
    meldingen = split_text(kladblok_content)

    # Process each melding separately
    for melding_content in meldingen:
        # Generate a new source_id for each melding
        source_id = generate_source_id()
        # Create a new melding in the database
        create_melding_in_database(melding_content, source_id)

    return jsonify({'message': 'Meldingen toegevoegd vanuit kladblok'}), 201

@app.route('/meldingen', methods=['POST'])
def create_melding():
    data = request.json
    melding_content = data.get('melding_content')
    source_id = data.get('source_id')  # Retrieve the source_id from the JSON payload

    # Check if source_id is provided, otherwise generate automatically
    if source_id is None:
        source_id = generate_source_id()

    # Create a new melding
    create_melding_in_database(melding_content, source_id)

    return jsonify({'message': 'Melding toegevoegd'}), 201

@app.route('/meldingen/<int:melding_id>', methods=['GET'])
def get_melding(melding_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Retrieve the melding from the meldingen table
    cursor.execute('SELECT * FROM meldingen WHERE id = ?', (melding_id,))
    melding = cursor.fetchone()

    if melding:
        # Retrieve berichten
        cursor.execute('SELECT * FROM berichten WHERE melding_id = ?', (melding_id,))
        berichten = cursor.fetchall()

        berichten_data = []
        for content in berichten:
            berichten_data.append({
                'id': content[0],
                'melding_id': content[1],  # Add melding_id to the response of each message
                'time': content[2],
                'content': content[3],
                'enrichment': json.loads(content[4]) if content[4] else None
            })

        response = {
            'id': melding[0],
            'source_id': melding[1],
            'datetime': melding[2],
            'status': melding[3],
            'priority': melding[4],
            'description': melding[5],
            'berichten': berichten_data
        }
        return jsonify(response)
    return jsonify({'message': 'Melding not found'}), 404

@app.route('/meldingen/<int:melding_id>', methods=['DELETE'])
def delete_melding(melding_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meldingen WHERE id = ?', (melding_id,))
    cursor.execute('DELETE FROM berichten WHERE melding_id = ?', (melding_id,))
    cursor.execute('DELETE FROM metadata WHERE message_id = ?', (melding_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Melding deleted successfully'})

# Endpoint to update the source_id of a melding
@app.route('/meldingen/<int:melding_id>/source_id', methods=['POST'])
def update_source_id(melding_id):
    data = request.json
    new_source_id = data.get('source_id')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Update the source_id of the melding
    cursor.execute('UPDATE meldingen SET source_id = ? WHERE id = ?', (new_source_id, melding_id))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Source ID updated successfully'})

# POST key-value pairs to a specific melding
@app.route('/meldingen/<int:melding_id>/metadata', methods=['POST'])
def add_metadata(melding_id):
    data = request.json
    key = data.get('key')
    value = data.get('value')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO metadata (message_id, key, value) VALUES (?, ?, ?)', (melding_id, key, value))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Metadata added successfully'}), 201

@app.route('/meldingen/<int:melding_id>', methods=['PUT'])
def update_melding(melding_id):
    data = request.json
    description = data.get('description')
    status = data.get('status')
    priority = data.get('priority')
    berichten = data.get('berichten')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Update the melding fields if provided
    if description:
        cursor.execute('UPDATE meldingen SET description = ? WHERE id = ?', (description, melding_id))
    if status:
        cursor.execute('UPDATE meldingen SET status = ? WHERE id = ?', (status, melding_id))
    if priority:
        cursor.execute('UPDATE meldingen SET priority = ? WHERE id = ?', (priority, melding_id))

    # Update the berichten if provided
    if berichten:
        for bericht in berichten:
            bericht_id = bericht.get('id')
            content = bericht.get('content')
            if bericht_id and content:
                doc = nlp(content)
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                cursor.execute('''
                    UPDATE berichten SET content = ?, enrichment = ? WHERE id = ?
                ''', (content, json.dumps(entities), bericht_id))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Melding updated successfully'})

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
