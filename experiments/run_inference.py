import json
import logging
import os

import hydra
import pandas as pd
import torch
from omegaconf import DictConfig
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList

import common
from train_transformer import EOL_TOKEN
from parse_test_dataset import KEYWORDS


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
                stopping_criteria=StoppingCriteriaList([criteria])
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
                num_beams=cfg['evaluation']['num_beams']
            )
    generated_sequences = generated_sequences.cpu().numpy()
    generated_new_tokens = generated_sequences[:, sample["input_ids"].shape[1]:]
    return generated_new_tokens


def get_suggestions_next_token(model, tokenizer, input, cfg):
    generated_new_tokens = generate(model, tokenizer, input, cfg)

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
        gsplit = generated.split(' ')
        if len(gsplit) >= 2:
            suggestions.append(generated.split(' ')[1])
    return suggestions


def get_suggestions_next_line(model, tokenizer, input, cfg):
    generated_new_tokens = generate(model, tokenizer, input, cfg, None, EOL_TOKEN)

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True).split(EOL_TOKEN)[0].strip()
        suggestions.append(generated)
    return suggestions


def get_suggestions_next_block(model, tokenizer, input, cfg):
    generated_new_tokens = generate(model, tokenizer, input, cfg, None, 'Ġ}')

    suggestions = []
    for k, new_tokens in enumerate(generated_new_tokens):
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        suggestions.append(generated)
    return suggestions


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    logging.getLogger().info(f"Running inference mode={cfg['evaluation']['mode']}")

    #train_data_folder = common.get_train_data_folder(cfg)
    train_data_folder = os.path.join(cfg.run.train_data_folder, "modelset_token")
    results_folder = common.get_results_folder(cfg)
    if cfg['evaluation']['sampled_test']:
        with open(os.path.join(train_data_folder, f"parsed_test_sampled_{cfg['evaluation']['mode']}.json")) as f:
            parsed_test = json.load(f)
    else:
        with open(os.path.join(train_data_folder, f"parsed_test_{cfg['evaluation']['mode']}.json")) as f:
            parsed_test = json.load(f)

    model = AutoModelForCausalLM.from_pretrained(os.path.join(common.get_trained_model_folder(cfg),
                                                              cfg['run']['best_model_folder']),
                                                 device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(common.get_trained_model_folder(cfg),
                                                           cfg['run']['best_model_folder']))

    if cfg['evaluation']['mode'] == 'token-id':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": [],
            "keyword": []
        }
        for kw in KEYWORDS:
            for input, expected in tqdm(parsed_test[kw], desc=f'KW {kw}'):
                suggestions = get_suggestions_next_token(model, tokenizer, input, cfg)
                # suggestions = list(OrderedDict.fromkeys(suggestions))
                # print(suggestions, expected)

                final_output["input"].append(input)
                final_output["expected"].append(expected)
                final_output["suggestions"].append(SEP.join(suggestions))
                final_output["keyword"].append(kw)

    elif cfg['evaluation']['mode'] == 'token':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        for input, expected in tqdm(parsed_test, desc=f'Inference'):
            suggestions = get_suggestions_next_token(model, tokenizer, input, cfg)
            # print(suggestions, expected)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(SEP.join(suggestions))
    elif cfg['evaluation']['mode'] == 'line' or cfg['evaluation']['mode'] == 'block':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        get_suggestions = get_suggestions_next_line \
            if cfg['evaluation']['mode'] == 'line' else get_suggestions_next_block

        for input, expected in tqdm(parsed_test, desc=f'Inference'):
            suggestions = get_suggestions(model, tokenizer, input, cfg)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(SEP.join(suggestions))
            # print(suggestions, '---', expected)
    else:
        raise ValueError('Not supported')

    pd_results = pd.DataFrame.from_dict(final_output)
    os.makedirs(results_folder, exist_ok=True)
    pd_results.to_csv(os.path.join(results_folder, f"results_{cfg['evaluation']['mode']}.csv"))


if __name__ == '__main__':
    main()
