from flask import Flask, jsonify, request

from .utils.funcs import top_filtering, nlg, extractor
from .utils.search import search_for

from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex

import pandas as pd
import random
import torch
import pickle
import time
import slack
import os
import re
import wget

# Stuff for nlg
gpt2_medium_config = GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel(gpt2_medium_config)
model.load_state_dict(torch.load('/datafiles/medium_ft.pkl'), strict=False)
print('Tokenizer and model ready..')

# More stuff for nlg
eos = [tokenizer.encoder["<|endoftext|>"]]
num_words = 50
device = torch.device('cpu')
model.to(device)
model.lm_head.weight.data = model.transformer.wte.weight.data

# Load indexes
bert_annoy = AnnoyIndex(768, 'angular')
bert_annoy.load('/datafiles/dim768-trees13.ann')
tfidf_annoy = AnnoyIndex(100, 'angular')
tfidf_annoy.load('/datafiles/tfidf.ann')
print('Indexes loaded..')

# Load fine-tuned BERT
embedder = SentenceTransformer(extractor('/datafiles/distil-bert-SO.tar.gz'))
embedder.to(device)
print('Embedder loaded..')

# Load tfidf and svd
tfidf_file = open('/datafiles/tfidf.pkl', 'rb')
tfidf = pickle.loads(tfidf_file.read())
svd_file = open('/datafiles/svd.pkl', 'rb')
svd = pickle.loads(svd_file.read())
print('TfidfVectorizer and TruncatedSVD loaded..')

# Read in message ids
hired = pd.read_csv('/datafiles/hired.csv')
choices = hired.p_text.to_list()
tfidf_m_ids = pd.read_csv('/datafiles/tfidf_m_ids.csv')
bert_m_ids = pd.read_csv('/datafiles/bert_m_ids.csv')
print('Everything is ready!')

bot_to_at = os.environ.get("BOT_TO_AT")

def create_app():
    app = Flask(__name__)

    @app.route('/predict_test', methods=['POST'])
    def predict_test():
        lines = request.get_json(force=True)
        replies = lines['input_text']
        # Check if they want to search
        if 'search:' in replies.lower():
            output = search_for(
                replies, tfidf, svd, tfidf_annoy, tfidf_m_ids,
                embedder, bert_annoy, bert_m_ids
                )

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

    @app.route('/predict', methods=['POST'])
    def predict():
        if request.method == 'POST':
            lines = request.get_json(force=True)
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
                    limit=20
                )
                # print('REPLIES:\n' + replies)
                # print('INPUT TEXT' + input_text)
                # reply_texts = [reply.get('text') for reply in replies['messages'] if reply.get('text')]
                # print('REPLY TEXT' + reply_texts)
                # input_text = '<endoftext>'.join(reply_texts + [input_text])
                reply_count = replies['messages'][0]['reply_count']
                # print(reply_count)
                if reply_count > 1:
                    context_list = [re.sub('<[^>]+> ', '', m['text']) for m in replies['messages'][1:]]
                else:
                    context_list = [re.sub('<[^>]+> ', '', m['text']) for m in replies['messages']]
                # print(context_list)
                input_text = '<|endoftext|>'.join(context_list)
                # print(input_text)
                

            # Check if they want to search
            if 'search:' in input_text.lower():
                output = search_for(
                    input_text, tfidf, svd, tfidf_annoy, tfidf_m_ids,
                    embedder, bert_annoy, bert_m_ids
                    )
                output = "Related posts: " + "\n".join(output)

            # Check if they want a celebration post from #hired
            elif 'hired insp' in input_text.lower():
                output = random.choice(choices)

            # Revert to natural language generation
            else:
                now = time.time()
                text = nlg(input_text, model, tokenizer)
                elapsed = time.time() - now
                if reply_count < 20:
                    output = bot_to_at + ' ' + text# + ' ELAPSED TIME:' + str(elapsed)
                else:
                    output = text# + ' ELAPSED TIME:' + str(elapsed)

            return jsonify({
                "text": output,
                "buttons": [],
                "image": None,
                "elements": [],
                "attachments": [],
                "thread_ts": thread_ts
            })

    return app
