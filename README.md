# phischer_moseley
Uploading my consciousness to the machine, one API call at a time.

# How it Works
## Model creation and fine-tuning
- Facebook messenger data is downloaded as a really big zip file. This contains messages in the `inbox/` folder, which contains a subfolder for each chat. These are named with the actual name of the chat (either the person's name if they're an individual, or the chat name if it's a group. Nicknames are ignored.). Each subfolder contains a `message_1.json` file, which is (nonstandard) JSON that contains the actual messages.
- This gets parsed by `parser.py`, which strips non-text content (such as images, reactions, and call notifications) and merges consecutive messages by the same person into a single message. These get aggregated, and exported to a `.jsonl` file.
- This is then double-checked for formatting by the OpenAI CLI, with `openai tools fine_tunes.prepare_data -f file.jsonl`. Currently the formatting coming out of the parser isn't perfect, so it'll spit out a `file_prepared.jsonl` file. I need to fix the parser so that it doesn't need to suggest any edits.
- A model is then trained with OpenAI, using `openai api fine_tunes.create -t file_prepared.jsonl -m davinci --suffix "contactname"`. Davinci is the most advanced model and seems to be what's required to make this thing actually funny, but it can be replaced with `curie`, `babbage`, or `ada` for cheaper training/running at the expense of less model complexity.
- The fine-tuned model is stored on OpenAI's servers, and once this is done the normal SMS flow can work.

## Model usage + SMS
- Twillio recieves a text at the configured phone number, which calls back to a webhook. This webhook is hosted by Flask on the local machine by running `phischer.py`, and the webhook is exposed to the open net with ngrok.
- This webhook uses the incoming text as the prompt for GPT3, and returns the model's response.


# Requirements
- OpenAI API installed. The python library includes a CLI that's used for preparing the model data before fine-tuning.
- Flask to expose a webhook for the Twillio API to callback to whenever a new message is recieved. Could also use Django for this, but Flask is lighter.
- ngrok to expose the locally-hosted webhook to the open internet so that Twilio's servers can reach it.

Notably, this does not require managing Twillio API keys on the server. Twillio itself is performing the callback, so just make sure to protect your endpoints :)
