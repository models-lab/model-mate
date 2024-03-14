import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList

#import common
#from train_transformer import EOL_TOKEN
#from parse_test_dataset import KEYWORDS

EOL_TOKEN = '<EOL>'
BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
UNK_TOKEN = '<unk>'
KEYWORDS = ["class", "attr", "ref", "extends", "package", "val", "]"]

class CriteriaToken(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            if decoded_generation.count(' ') <= 1:
                return False
        return True


class CriteriaLine(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            dec_split = decoded_generation.split()
            if '<EOL>' not in dec_split:
                return False
        return True


SEP = '<>'



def generate(model, tokenizer, input, cfg, criteria=CriteriaToken, end_token=None):
    sample = tokenizer([input], return_tensors="pt")
    sample["input_ids"] = sample["input_ids"][:,
                          -(cfg['params']['context_length'] - cfg['evaluation']['max_new_tokens']):]
    sample["attention_mask"] = sample["attention_mask"][:,
                               -(cfg['params']['context_length'] - cfg['evaluation']['max_new_tokens']):]
    output_scores = cfg.get('output_scores') or False
    return_dict_in_generate = cfg.get('output_scores') or False

    with torch.no_grad():
        if criteria:
            criteria = criteria(tokenizer, sample["input_ids"].shape[1])
            generated_sequences = model.generate(
                input_ids=sample["input_ids"].cuda(),
                attention_mask=sample["attention_mask"].cuda(),
                do_sample=False,
                max_new_tokens=cfg['evaluation']['max_new_tokens'],
                num_return_sequences=cfg['evaluation']['num_beams'],
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                num_beams=cfg['evaluation']['num_beams'],
                stopping_criteria=StoppingCriteriaList([criteria]),
                output_scores=output_scores,
                return_dict_in_generate=return_dict_in_generate
            )
        else:
            generated_sequences = model.generate(
                input_ids=sample["input_ids"].cuda(),
                attention_mask=sample["attention_mask"].cuda(),
                do_sample=False,
                max_new_tokens=cfg['evaluation']['max_new_tokens'],
                num_return_sequences=cfg['evaluation']['num_beams'],
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.convert_tokens_to_ids(end_token),
                num_beams=cfg['evaluation']['num_beams'],
                output_scores=output_scores,
                return_dict_in_generate=return_dict_in_generate
            )

    def to_tokens(sequences):
        sequences = sequences.cpu().numpy()
        return sequences[:, sample["input_ids"].shape[1]:]

    if output_scores:
        tokens = to_tokens(generated_sequences.sequences)
        scores = generated_sequences.scores
        return tokens, scores
    else:
        return to_tokens(generated_sequences), None




def get_suggestions_next_token(model, tokenizer, input, cfg):
    generated_new_tokens, scores = generate(model, tokenizer, input, cfg)

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
        gsplit = generated.split(' ')
        if len(gsplit) >= 2:
            suggestions.append(generated.split(' ')[1])
    return suggestions


def get_suggestions_next_line(model, tokenizer, input, cfg):
    generated_new_tokens, scores = generate(model, tokenizer, input, cfg, None, EOL_TOKEN)

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True).split(EOL_TOKEN)[0].strip()
        suggestions.append(generated)
    if scores is not None:
        scores = [torch.mean(single_score) for single_score in scores]
        return suggestions, scores
    return suggestions


def get_suggestions_next_block(model, tokenizer, input, cfg):
    generated_new_tokens, scores = generate(model, tokenizer, input, cfg, None, 'Ġ}')

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        suggestions.append(generated)
    return suggestions
