from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import openai
from json import load

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    # Get GPT prompt and origin phone number from request.
    prompt = request.values.get('Body', None)
    origin_phone_number = request.values.get('From', None)

    # Route the incoming phone number to the correct model.
    # routing.json is user-provided and .gitignored since it contains phone numbers in plaintext.
    routing = load(open('routing.json'))
    if origin_phone_number in routing.keys():
        model = routing[origin_phone_number]
    
    else:
        model = routing['default']

    # Generate response from GPT3.
    response = openai.Completion.create(
        model=model,
        prompt=prompt+'\n\n###\n\n',
        stop=' END',
        temperature=0.7,
        max_tokens = 256,
        top_p=1)

    text = response.to_dict_recursive()['choices'][0]['text'][1:]

    resp = MessagingResponse()
    resp.message(text)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
