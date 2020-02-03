from flask import Flask, jsonify, request

from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
import torch
import torch.nn.functional as F
import time
from .utils.torch import top_filtering
import slack
import os
import re

gpt2_medium_config = GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16)
print('Instantiating tokenizer...')
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
print('Tokenizer ready!')
model = GPT2LMHeadModel(gpt2_medium_config)
load_start = time.time()
print('Loading model...')
model.load_state_dict(torch.load("/api/api/medium_ft.pkl"), strict=False)
print(f'Model ready! {time.time() - load_start}')

eos = [tokenizer.encoder["<|endoftext|>"]]
num_words = 50
device = torch.device('cpu')
model.to(device)
model.lm_head.weight.data = model.transformer.wte.weight.data

def get_output(replies):
    past = None
    temperature = 0.9
    top_k = -1
    top_p = 0.9

    model.eval()
    prev_input = None

    context_list = [re.sub('<[^>]+> ', '', m['text']) for m in replies['messages']]
    print(context_list)
    context = '<|endoftext|>'.join(context_list)
    user = tokenizer.encode(context)
    prev_input = user
    prev_input = torch.LongTensor(prev_input).unsqueeze(0).to(device)
    _, past = model(prev_input, past=past)
    prev_input = torch.LongTensor([eos]).to(device)
        
    sent = []
    for i in range(500):
        logits, past = model(prev_input, past=past)
        logits = logits[:, -1, :] / temperature
        logits = top_filtering(logits, top_k=top_k, top_p=top_p)

        probs = torch.softmax(logits, dim=-1)

        prev_input = torch.multinomial(probs, num_samples=1)
        prev_word = prev_input.item()

        if prev_word == eos[0]:
            break
        sent.append(prev_word)
    
    prev_input = torch.LongTensor([eos]).to(device)
    _, past = model(prev_input, past=past)
    return tokenizer.decode(sent)
 
def create_app():
    app = Flask(__name__)

    @app.route('/predict', methods=['POST'])
    def predict():
        if request.method == 'POST':

            lines = request.get_json(force=True)
            print(lines)
            tracker = lines['tracker']
            latest_message = tracker['latest_message']
            input_text = latest_message['text']
            events = tracker['events']
            user_event = [e for e in events if e['event'] == 'user']

            thread_ts = user_event[-1]['metadata'].get(
                'thread_ts') if user_event else None
            channel = user_event[-1]['metadata'].get(
                'channel') if user_event else None
            print('Received text!')

            client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
            reply_count = 0
            if thread_ts:
                replies = client.conversations_replies(
                    channel=channel,
                    ts=str(thread_ts),
                    limit=3
                )
                reply_count = replies['messages'][0]['reply_count']
                # print(f'REPLIES: {replies}')
                #print(thread_ts)
            output = f' Reply count: {reply_count}'

            print('Starting inference...')
            time_now = time.time()
            output_text = get_output(replies)
            time_to_predict = time.time() - time_now
            print('Inference done!')

            output = output_text + ' TIME_TO_PREDICT:' + str(time_to_predict)

            # output = 'it is working...'

            return jsonify({
                "text": output,
                "buttons": [],
                "image": None,
                "elements": [],
                "attachments": [],
                "thread_ts": thread_ts
            })


    return app
