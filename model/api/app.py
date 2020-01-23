from flask import Flask, jsonify, request

from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import torch.nn.functional as F
from tqdm import trange
import time
from .utils.torch import top_k_top_p_filtering

num_words = 50
device = torch.device('cpu')
# model.to(device)



def create_app():
    app = Flask(__name__)

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
            for _ in trange(length):
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

    tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")
    model.eval()

    @app.route('/predict', methods=['POST'])
    def predict():
        if request.method == 'POST':
            lines = request.get_json(force=True)
            input_text = lines['input_text']
            time_now = time.time()
            output_text = get_output(model, input_text, tokenizer)
            time_to_predict = time.time() - time_now
            return jsonify({
                'input_text': input_text,
                'output_text': output_text,
                'prediction_time': time_to_predict
                })

    return app