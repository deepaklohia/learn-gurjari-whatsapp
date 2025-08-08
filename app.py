from flask import Flask, request, Response, jsonify
import json
import datetime

app = Flask(__name__)

# Load Gurjari vocabulary
with open('gurjari_data.json', 'r', encoding='utf-8') as f:
    vocabulary = json.load(f)

# Function to find translation
def find_translation(query):
    query = query.lower().strip()
    for entry in vocabulary:
        if query in entry['english'].lower() or query in entry.get('hindi', '').lower():
            return f"Gurjari: {entry['gurjari']}\nPronunciation: {entry['pronunciation']}\nMeaning: {entry['english']}"
    return "Sorry, I couldn't find that word."

# Root route
@app.route('/')
def home():
    return "✅ Gurjari WhatsApp Bot is running!"

# Dialogflow webhook
@app.route('/dialogflow_webhook', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]
    parameters = req["queryResult"].get("parameters", {})
    
    if intent == "TranslateWord":
        word = parameters.get("word", "")
        response = find_translation(word)
    elif intent == "Greet":
        response = "राम राम! 🙏"
    elif intent == "WordOfTheDay":
        today = datetime.datetime.now().day
        word = vocabulary[today % len(vocabulary)]
        response = f"आज का शब्द: {word['english']}\nगुर्जरी: {word['gurjari']}\nउच्चारण: {word['pronunciation']}"
    else:
        response = "माफ़ करना, मैं समझ नहीं पाया।"

    return jsonify({"fulfillmentText": response})

# WhatsApp webhook
@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.form.get('Body')
    response = find_translation(incoming_msg)
    twiml_response = f"""<Response>
        <Message>{response}</Message>
    </Response>"""
    return Response(twiml_response, mimetype='application/xml')

# Daily message endpoint
@app.route('/daily', methods=['GET'])
def daily_word():
    today = datetime.datetime.now().day
    word = vocabulary[today % len(vocabulary)]
    message = f"""आज का शब्द: {word['english']}
गुर्जरी: {word['gurjari']}
उच्चारण: {word['pronunciation']}
अर्थ: {word['english']}"""
    return message

if __name__ == '__main__':
    app.run(debug=True)
