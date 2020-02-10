import os, time, json, time

import flask
from flask import Flask, jsonify, request

from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import torch.nn.functional as F

import slack

num_words = 50
device = torch.device('cpu')
# model.to(device)

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float("Inf")):
    assert (logits.dim() == 1)
    top_k = min(top_k, logits.size(-1))
    if top_k > 0:
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

def sample_sequence(
    model,
    length,
    context,
    num_samples=1,
    temperature=1,
    top_k=0,
    top_p=0.9,
    repetition_penalty=1.0,
    device="cuda",
):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0).repeat(num_samples, 1)
    generated = context
    with torch.no_grad():
        for _ in range(length):
            inputs = {"input_ids": generated}
            outputs = model(**inputs)
            next_token_logits = outputs[0][0, -1, :] / (temperature if temperature > 0 else 1.0)
            for _ in set(generated.view(-1).tolist()):
                next_token_logits[_] /= repetition_penalty
            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=top_k, top_p=top_p)
            if temperature == 0:
                next_token = torch.argmax(filtered_logits).unsqueeze(0)
            else:
                next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
    return generated

def get_output(model, input_text, tokenizer):
    indexed_tokens = tokenizer.encode(input_text)
    output = sample_sequence(model, num_words, indexed_tokens, device=device)
    return tokenizer.decode(
        output[0, 0:].tolist(), clean_up_tokenization_spaces=True, skip_special_tokens=True
    )

class ScoringService(object):
    model = None
    tokenizer = None

    @classmethod
    def get_model(cls):
        if cls.model == None:
            cls.model = GPT2LMHeadModel.from_pretrained("distilgpt2")
            cls.model.eval()
        return cls.model

    @classmethod
    def get_tokenizer(cls):
        if cls.tokenizer == None:
            cls.tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
        return cls.tokenizer

    @classmethod
    def predict(cls, input_text):
        model = cls.get_model()
        tokenizer = cls.get_tokenizer()

        return get_output(model, input_text, tokenizer)

def create_app():
    app = Flask(__name__)

    @app.route('/ping', methods=['GET'])
    def ping():
        """Determine if the container is working and healthy. In this sample container, we declare
        it healthy if we can load the model successfully."""
        health = ScoringService.get_model() is not None  # You can insert a health check here

        status = 200 if health else 404
        return flask.Response(response='\n', status=status, mimetype='application/json')

    @app.route('/invocations', methods=['POST'])
    def transformation():
        try:
            payload = request.get_json(force=True)
        except:
            return jsonify('The speed cow requires json')
        else:
            # tracker = payload['tracker']
            # latest_message = tracker['latest_message']
            # input_text = latest_message['text']
            # events = tracker['events']
            # user_event = [e for e in events if e['event'] == 'user']

            # thread_ts = user_event[-1]['metadata'].get('thread_ts') if user_event else None
            # channel = user_event[-1]['metadata'].get('channel') if user_event else None

            start = time.time()
            output_text = ScoringService.predict(payload['input_text'])
            time_to_predict = time.time() - start

            # output = output_text + ' TIME_TO_PREDICT:' + str(time_to_predict)

            # client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
            # reply_count = 0
            # if thread_ts:
            #     replies = client.conversations_replies(
            #         channel=channel,
            #         ts=str(thread_ts),
            #         limit=100
            #     )
            #     reply_count = replies['messages'][0]['reply_count']

            # output = output + f' Reply count: {reply_count}'

            # return jsonify({
            #     "text": output,
            #     "buttons": [],
            #     "image": None,
            #     "elements": [],
            #     "attachments": [],
            #     "thread_ts": thread_ts
            # })

            return jsonify({
                "output_text": output_text,
                "time_to_predict": time_to_predict,
            })

            
    return app