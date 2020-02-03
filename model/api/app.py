from flask import Flask, jsonify, request

from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
import torch
import torch.nn.functional as F
import time

gpt2_medium_config = GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
print('instantiated tokenizer...')

model = GPT2LMHeadModel(gpt2_medium_config)
print('starting to load model...')
model.load_state_dict(torch.load("/api/api/medium_ft.pkl"), strict=False)
# model.load_state_dict(torch.load("/api/api/GP2-pretrain-step-250.pkl"), strict=False)
print('model loaded!!!!!')

eos = [tokenizer.encoder["<|endoftext|>"]]
num_words = 50
device = torch.device('cpu')
model.to(device)

model.lm_head.weight.data = model.transformer.wte.weight.data

def top_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k, top-p (nucleus) and/or threshold filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k: <=0: no filtering, >0: keep only top k tokens with highest probability.
            top_p: <=0.0: no filtering, >0.0: keep only a subset S of candidates, where S is the smallest subset
                whose total probability mass is greater than or equal to the threshold top_p.
                In practice, we select the highest probability tokens whose cumulative probability mass exceeds
                the threshold top_p.
    """
    # batch support!
    if top_k > 0:
        values, _ = torch.topk(logits, top_k)
        min_values = values[:, -1].unsqueeze(1).repeat(1, logits.shape[-1])
        logits = torch.where(logits < min_values, 
                             torch.ones_like(logits, dtype=logits.dtype) * -float('Inf'), 
                             logits)
    if top_p > 0.0:
        # Compute cumulative probabilities of sorted tokens
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probabilities > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        
        sorted_logits = sorted_logits.masked_fill_(sorted_indices_to_remove, filter_value)
        logits = torch.zeros_like(logits).scatter(1, sorted_indices, sorted_logits)
    
    return logits

model.eval()
prev_input = None

def get_output(input_text):
    past = None
    temperature = 0.9
    top_k = -1
    top_p = 0.9
    
    user = tokenizer.encode(input_text)
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
    output_text = tokenizer.decode(sent)
    prev_input = torch.LongTensor([eos]).to(device)
    _, past = model(prev_input, past=past)
    return output_text

def create_app():
    app = Flask(__name__)

    @app.route('/predict', methods=['POST'])
    def predict():
        if request.method == 'POST':
            lines = request.get_json(force=True)
            print(lines)
            # tracker = lines['tracker']
            # latest_message = tracker['latest_message']
            # input_text = latest_message['text']
            # events = tracker['events']
            # user_event = [e for e in events if e['event'] == 'user']
            # thread_ts = user_event[0].get('thread_ts') if user_event else None
            input_text = lines['input_text']
            time_now = time.time()
            print('received text!!!!')
            print('starting inference......')
            output_text = get_output(input_text)
            time_to_predict = time.time() - time_now
            output = output_text + ' TIME_TO_PREDICT:' + str(time_to_predict)
            # return jsonify({
            #     "text": output,
            #     "buttons": [],
            #     "image": None,
            #     "elements": [],
            #     "attachments": [],
            #     "thread_ts": thread_ts
            # })
            return jsonify({
                'output_text': output
            })

    return app
