from flask import Flask, jsonify, request

from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import torch.nn.functional as F
import time
from .utils.torch import top_k_top_p_filtering
import slack
import os

num_words = 50
device = torch.device('cpu')


# model.to(device)


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
            next_token_logits = outputs[0][0, -1, :] / \
                                (temperature if temperature > 0 else 1.0)
            for _ in set(generated.view(-1).tolist()):
                next_token_logits[_] /= repetition_penalty
            filtered_logits = top_k_top_p_filtering(
                next_token_logits, top_k=top_k, top_p=top_p)
            if temperature == 0:
                next_token = torch.argmax(filtered_logits).unsqueeze(0)
            else:
                next_token = torch.multinomial(
                    F.softmax(filtered_logits, dim=-1), num_samples=1)
            generated = torch.cat(
                (generated, next_token.unsqueeze(0)), dim=1)
    return generated


tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
model = GPT2LMHeadModel.from_pretrained("distilgpt2")
model.eval()


def get_output(input_text, model=model, tokenizer=tokenizer):
    indexed_tokens = tokenizer.encode(input_text)
    output = sample_sequence(
        model, num_words, indexed_tokens, device=device)
    return tokenizer.decode(
        output[0, 0:].tolist(), clean_up_tokenization_spaces=True,
        skip_special_tokens=True
    )


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
            time_now = time.time()
            output_text = get_output(input_text)
            # output_text = "Super Instant"
            # output_text = 'this is a canned response'
            time_to_predict = time.time() - time_now

            output = output_text + ' TIME_TO_PREDICT:' + str(time_to_predict)

            client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
            reply_count = 0
            if thread_ts:
                replies = client.conversations_replies(
                    channel=channel,
                    ts=str(thread_ts),
                    limit=100
                )
                reply_count = replies['messages'][0]['reply_count']
                #print(replies)
                #print(thread_ts)
            output = output + f' Reply count: {reply_count}'

            return jsonify({
                "text": output,
                "buttons": [],
                "image": None,
                "elements": [],
                "attachments": [],
                "thread_ts": thread_ts
            })

    return app