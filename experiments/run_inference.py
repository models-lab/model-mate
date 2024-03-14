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
from inference import ModelInference
from train_transformer import EOL_TOKEN
from parse_test_dataset import KEYWORDS

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

SEP = '<>'

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    logging.getLogger().info(f"Running inference mode={cfg['evaluation']['mode']}")

    train_data_folder = common.get_train_data_folder(cfg)
    results_folder = common.get_results_folder(cfg)
    with open(os.path.join(train_data_folder, f"parsed_test_{cfg['evaluation']['mode']}.json")) as f:
        parsed_test = json.load(f)

    model_inference = ModelInference(cfg['run']['best_model_folder'])

    if cfg['evaluation']['mode'] == 'token-id':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": [],
            "keyword": []
        }
        for kw in KEYWORDS:
            for input, expected in tqdm(parsed_test[kw], desc=f'KW {kw}'):
                suggestions = model_inference.get_suggestions_next_token(input, **cfg)
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
            suggestions = model_inference.get_suggestions_next_token(input, **cfg)
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
        get_suggestions = model_inference.get_suggestions_next_line \
            if cfg['evaluation']['mode'] == 'line' else model_inference.get_suggestions_next_block

        for input, expected in tqdm(parsed_test, desc=f'Inference'):
            suggestions = get_suggestions(input, **cfg)
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
