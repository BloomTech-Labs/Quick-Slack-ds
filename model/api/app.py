from flask import Flask, jsonify, request

from .utils.funcs import top_filtering, nlg
from .utils.search import search_for

from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
import pandas as pd 
import random
import torch
import pickle
import time
import slack
import os
import re
import wget

# Root path
root = '/api/api/'

# Hired skill stuff
hired = pd.read_csv(root + 'hired.csv')
choices = hired.p_text.to_list()

# Stuff for nlg
gpt2_medium_config = GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16)
print('Instantiating tokenizer...')
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
print('Configuring model...')
model = GPT2LMHeadModel(gpt2_medium_config)
print('Downloading nlg from s3...')
nlg_url = 'https://model-2.s3.us-east-2.amazonaws.com/medium_ft.pkl'
pkl_file = wget.download(nlg_url)
load_start = time.time()
print('Loading model...')
model.load_state_dict(torch.load(pkl_file), strict=False)
# model.load_state_dict(torch.load(root + 'medium_ft.pkl'), strict=False)
print(f'Model ready! {time.time() - load_start}')

# More stuff for nlg
eos = [tokenizer.encoder["<|endoftext|>"]]
num_words = 50
device = torch.device('cpu')
model.to(device)
model.lm_head.weight.data = model.transformer.wte.weight.data

# Search stuff
annoy_url = 'https://model-2.s3.us-east-2.amazonaws.com/annoy.ann'
print('Downloading index from s3...')
annoy_file = wget.download(annoy_url)
print('Config index...')
annoy = AnnoyIndex(100, 'angular')
print('Loading index...')
annoy.load(annoy_file)

tfidf_url = 'https://model-2.s3.us-east-2.amazonaws.com/tfidf.pkl'
print('Downloading tfidf from s3...')
tfidf_file = wget.download(tfidf_url)
print('Loading tfidf...')
tfidf = pickle.load(tfidf_file)

svd_url = 'https://model-2.s3.us-east-2.amazonaws.com/svd.pkl'
print('Downloading svd from s3...')
svd_file = wget.download(svd_url)
print('Loading svd...')
svd = pickle.load(svd_file)

hired_url = 'https://model-2.s3.us-east-2.amazonaws.com/hired.csv'
print('Downloading message ids...')
hired_csv = wget.download(hired_url)
message_ids = pd.read_csv(hired_csv)
print('Everything is ready!')

 
def create_app():
    app = Flask(__name__)

    @app.route('/predict', methods=['POST'])
    def predict():
        if request.method == 'POST':

            lines = request.get_json(force=True)
            # tracker = lines['tracker']
            # latest_message = tracker['latest_message']
            # input_text = latest_message['text']
            # events = tracker['events']
            # user_event = [e for e in events if e['event'] == 'user']

            # thread_ts = user_event[-1]['metadata'].get(
            #     'thread_ts') if user_event else None
            # channel = user_event[-1]['metadata'].get(
            #     'channel') if user_event else None
            # print('Received text!')


            # client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
            # reply_count = 0
            # if thread_ts:
            #     replies = client.conversations_replies(
            #         channel=channel,
            #         ts=str(thread_ts),
            #         limit=3
            #     )
            #     reply_count = replies['messages'][0]['reply_count']
                # print(f'REPLIES: {replies}')
                #print(thread_ts)
            # output = f' Reply count: {reply_count}'
            print(lines)
            replies = lines['input_text']

            # Check if they want to search
            if 'search:' in replies.lower():
                output = search_for(replies, tfidf, svd, annoy, message_ids)
            
            # Check if they want a celebration post from #hired
            elif 'hired insp' in replies.lower():
                output = random.choice(choices)
            
            # Revert to natural language generation
            else:
                now = time.time()
                text = nlg(replies, model, tokenizer)
                elapsed = time.time() - now
                output = text + ' ELAPSED TIME:' + str(elapsed)

            return jsonify({'output_text': output})

            # return jsonify({
            #     "text": output,
            #     "buttons": [],
            #     "image": None,
            #     "elements": [],
            #     "attachments": [],
            #     "thread_ts": thread_ts
            # })


    return app
