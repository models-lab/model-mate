import argparse
import json

import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList

from parse_test_dataset import KEYWORDS


class EndOfFunctionCriteriaToken(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            if decoded_generation.count(' ') <= 1:
                return False
        return True



class EndOfFunctionCriteriaLine(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            dec_split = decoded_generation.split()
            if('<EOL>' not in dec_split):
                return False
        return True

SEP = '<>'


def get_suggestions_next_token(model, tokenizer, input, args):
    sample = tokenizer([input], return_tensors="pt")
    sample["input_ids"] = sample["input_ids"][:, -(args.max_length - args.max_new_tokens):]
    sample["attention_mask"] = sample["attention_mask"][:, -(args.max_length - args.max_new_tokens):]
    with torch.no_grad():
        criteria = EndOfFunctionCriteriaToken(tokenizer, sample["input_ids"].shape[1])
        generated_sequences = model.generate(
            input_ids=sample["input_ids"].cuda(),
            attention_mask=sample["attention_mask"].cuda(),
            do_sample=False,
            max_new_tokens=args.max_new_tokens,
            num_return_sequences=args.n,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            num_beams=args.n,
            stopping_criteria=StoppingCriteriaList([criteria])
        )
    generated_sequences = generated_sequences.cpu().numpy()
    generated_new_tokens = generated_sequences[:, sample["input_ids"].shape[1]:]

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
        gsplit = generated.split(' ')
        if(len(gsplit) >= 2):
            suggestions.append(generated.split(' ')[1])
    return suggestions

def get_suggestions_next_line(model, tokenizer, input, args):
    sample = tokenizer([input], return_tensors="pt")
    sample["input_ids"] = sample["input_ids"][:, -(args.max_length - args.max_new_tokens):]
    sample["attention_mask"] = sample["attention_mask"][:, -(args.max_length - args.max_new_tokens):]
    with torch.no_grad():
        criteria = EndOfFunctionCriteriaLine(tokenizer, sample["input_ids"].shape[1])
        generated_sequences = model.generate(
            input_ids=sample["input_ids"].cuda(),
            attention_mask=sample["attention_mask"].cuda(),
            do_sample=False,
            max_new_tokens=args.max_new_tokens,
            num_return_sequences=args.n,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            num_beams=args.n,
            stopping_criteria=StoppingCriteriaList([criteria])
        )
    generated_sequences = generated_sequences.cpu().numpy()
    generated_new_tokens = generated_sequences[:, sample["input_ids"].shape[1]:]

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
        suggestions.append(generated)
    return suggestions

def main(args):
    with open(args.parsed_test) as f:
        parsed_test = json.load(f)

    model = AutoModelForCausalLM.from_pretrained(args.checkpoint, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint)

    if args.mode == 'token-id':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": [],
            "keyword": []
        }
        for kw in KEYWORDS:
            for input, expected in tqdm(parsed_test[kw], desc=f'KW {kw}'):
                suggestions = get_suggestions_next_token(model, tokenizer, input, args)
                # suggestions = list(OrderedDict.fromkeys(suggestions))
                # print(suggestions, expected)

                final_output["input"].append(input)
                final_output["expected"].append(expected)
                final_output["suggestions"].append(SEP.join(suggestions))
                final_output["keyword"].append(kw)

    elif args.mode == 'token':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        for input, expected in tqdm(parsed_test, desc=f'Inference'):
            suggestions = get_suggestions_next_token(model, tokenizer, input, args)
            # print(suggestions, expected)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(SEP.join(suggestions))
    elif args.mode == 'line':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        for input, expected in tqdm(parsed_test, desc=f'Inference'):
            suggestions = get_suggestions_next_line(model, tokenizer, input, args)
            print(suggestions)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(suggestions)
    else:
        raise ValueError('Not supported')

    pd_results = pd.DataFrame.from_dict(final_output)
    pd_results.to_csv(args.results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token', 'line', 'token-id'])
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--max_length', type=int, default=512)
    parser.add_argument('--max_new_tokens', type=int, default=10)
    parser.add_argument('--parsed_test', default='data/temp/modelset_token/test_parsed_token-id.json')
    parser.add_argument('--checkpoint', default='runs/gpt2-modelset_token-512/best_model')
    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2.csv')
    args = parser.parse_args()
    main(args)
