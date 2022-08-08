from email import message
import json
import os

def find_message_file(name):
   for path, current_dir, files in os.walk("./"):
      if 'message_1.json' in files and name in path:
         return path + '/message_1.json'

def load_and_clean(path):
   # Load messages from downloaded JSON
   with open(path) as f:
      data = json.load(f)

   # Sort by sent timesteamp
   messages = sorted(data['messages'], key=lambda d: d['timestamp_ms'])

   # Remove messages that aren't just text
   # This includes photos, videos, call notifications, and reactions
   def is_media(message):
      keys = ['photos', 'videos', 'gifs', 'audio_files', 'files', 'sticker']
      return any(k in message for k in keys)

   def is_call(message):
      return message['type'] == "Call"

   def is_unsent(message):
      return message['is_unsent']

   def is_reaction(message):
      if 'content' not in message.keys():
         return False
      
      return 'Reacted ' in message['content'] and ' to your message' in message['content']
   
   messages = [i for i in messages if not is_media(i) and not is_unsent(i) and not is_reaction(i) and not is_call(i)]

   # Make sure that each message has text
   for message in messages:
      if 'content' not in message.keys():
         print(message)

      assert 'content' in message.keys()

   # Decode emojis from Facebook's wierd scheme
   for message in messages:
      message['content'] = message['content'].encode('latin1').decode('utf8')

   return messages

def make_multiline(messages):
   multiline_messages = []
   for index, message in enumerate(messages):
      if index == 0:
         multiline_messages.append(dict(sender_name=message['sender_name'], content=message['content']))
      
      else:
         if multiline_messages[-1]['sender_name'] == message['sender_name']:
            multiline_messages[-1]['content'] += '\n' + message['content']
         
         else:
            multiline_messages.append(dict(sender_name=message['sender_name'], content=message['content']))
   
   return multiline_messages

def make_jsonl(messages, target, output_path):
   # The first message was either said by me or someone else, so iterate until we find the first message said by me
   start_message = list(i['sender_name'] != target for i in messages).index(True)

   lines = []
   for index in range(start_message, len(messages) - start_message, 2):
      output_dict = dict(prompt=messages[index]['content'], completion=messages[index+1]['content'])
      lines.append(json.dumps(output_dict))
   
   with open(output_path, 'w') as f:
      for line in lines:
         f.write(f"{line}\n")


person = 'firstnamelastname'
messages = make_multiline(load_and_clean(find_message_file(person)))
make_jsonl(messages, 'Fischer Moseley', f'{person}.jsonl')