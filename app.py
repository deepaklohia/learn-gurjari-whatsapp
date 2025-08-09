from flask import Flask, request, Response, jsonify
import json
import datetime
import os

app = Flask(__name__)

# Load Gurjari vocabulary
with open('gurjari_data.json', 'r', encoding='utf-8') as f:
    vocabulary = json.load(f)

# Function to find translation
def find_translation(query):
    query = query.lower().strip()
    for entry in vocabulary:
        english = entry.get('english', '').lower()
        hindi = entry.get('hindi', '').lower()
        gurjari = entry.get('gurjari', '').lower()
        if query in english or query in hindi or query in gurjari:
            return f"Gurjari: {entry.get('gurjari', '—')}\nPronunciation: {entry.get('pronunciation', '—')}\nMeaning: {english}"
    return "Sorry, I couldn't find that word."

# Function to get thought of the day
def get_thought_of_the_day():
    thoughts = [
        {"gurjari": "ज्ञान रो दीप जलाओ", "pronunciation": "Gyaan ro deep jalao", "english": "Light the lamp of knowledge"},
        {"gurjari": "सच्चाई री ताकत बड़ी है", "pronunciation": "Sachchai ri taakat badi hai", "english": "Truth is powerful"},
        {"gurjari": "हर दिन एक नई शुरुआत है", "pronunciation": "Har din ek nai shuruaat hai", "english": "Every day is a new beginning"}
    ]
    today = datetime.datetime.now().day
    thought = thoughts[today % len(thoughts)]
    return f"""🧠 Thought of the Day:
Gurjari: {thought['gurjari']}
Pronunciation: {thought['pronunciation']}
Meaning: {thought['english']}"""

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
    elif intent == "ThoughtOfTheDay":
        response = get_thought_of_the_day()
    else:
        response = "माफ़ करना, मैं समझ नहीं पाया।"

    return jsonify({"fulfillmentText": response})

# WhatsApp webhook
@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.form.get('Body', '').strip().lower()
    if incoming_msg in ["thought", "विचार", "सुविचार", "motivation"]:
        response = get_thought_of_the_day()
    else:
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

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
