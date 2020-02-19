import torch
import torch.nn.functional as F
import tarfile
import tempfile
from transformers import cached_path
import os

def extractor(file_path):
    tempdir = tempfile.mkdtemp()
    with tarfile.open(file_path, 'r:gz') as archive:
        archive.extractall(tempdir)
    return os.path.join(tempdir, 'model')

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


def nlg(replies, model, tokenizer):
    device = torch.device('cpu')
    eos = [tokenizer.encoder["<|endoftext|>"]]
    num_words = 50

    past = None
    temperature = 0.9
    top_k = -1
    top_p = 0.9

    model.eval()
    prev_input = None

    # context_list = [re.sub('<[^>]+> ', '', m['text']) for m in replies['messages']]
    # print(context_list)
    # context = '<|endoftext|>'.join(context_list)
    context = replies
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