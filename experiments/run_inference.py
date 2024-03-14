import json
import logging
import os

import hydra
import pandas as pd
from omegaconf import DictConfig
from tqdm import tqdm

import common
import time

from parse_test_dataset import Language
from inference import ModelInference

import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

SEP = '<>'


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    logging.getLogger().info(
        f"Running inference mode={cfg['evaluation']['mode']}, max_new_tokens={cfg['evaluation']['max_new_tokens']}")

    train_data_folder = common.get_train_data_folder(cfg)
    results_folder = common.get_results_folder(cfg)
    print(results_folder)
    if cfg['evaluation']['sampled_test']:
        print("Using a specific test file:", cfg.evaluation.sampled_test)
        with open(cfg.evaluation.sampled_test) as f:
            # with open(os.path.join(train_data_folder, f"parsed_test_sampled_{cfg['evaluation']['mode']}.json")) as f:
            parsed_test = json.load(f)
    else:
        with open(os.path.join(train_data_folder, f"parsed_test_{cfg['evaluation']['mode']}.json")) as f:
            parsed_test = json.load(f)

    model_inference = ModelInference(cfg['run']['best_model_folder'])

    performance = {
        "time": [],
        "predlen": []
    }
    if cfg['evaluation']['mode'] == 'token-id':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": [],
            "keyword": []
        }

        language = Language(cfg.language)

        for kw in language.token_type_names:
            print("Processing for ", kw)
            for input, expected in tqdm(parsed_test[kw], desc=f'KW {kw}'):
                start_time = time.time()
                suggestions = model_inference.get_suggestions_next_token(input, **cfg)
                end_time = time.time()
                performance["time"].append(end_time - start_time)
                performance["predlen"].append(1)
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
            start_time = time.time()
            suggestions = model_inference.get_suggestions_next_token(input, **cfg)
            end_time = time.time()
            performance["time"].append(end_time - start_time)
            performance["predlen"].append(1)
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
            start_time = time.time()
            suggestions = get_suggestions(input, **cfg)
            end_time = time.time()
            performance["time"].append(end_time - start_time)
            predlen = 0
            for x in suggestions:
                tokenizer = model_inference.tokenizer
                predlen += len(tokenizer([x], return_tensors="pt")["input_ids"])
            performance["predlen"].append(predlen)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(SEP.join(suggestions))
            # print(suggestions, '---', expected)
    else:
        raise ValueError('Not supported')

    pd_results = pd.DataFrame.from_dict(final_output)
    os.makedirs(results_folder, exist_ok=True)
    if cfg['evaluation']['sampled_test']:
        evaluation_result_file = os.path.join(results_folder, f"results_sampled_{cfg['evaluation']['mode']}.csv")
    else:
        evaluation_result_file = e = os.path.join(results_folder, f"results_{cfg['evaluation']['mode']}.csv")

    print("Writing results to: ", evaluation_result_file)
    pd_results.to_csv(evaluation_result_file)

    pd_results2 = pd.DataFrame.from_dict(performance)
    if cfg['evaluation']['sampled_test']:
        pd_results2.to_csv(os.path.join(results_folder, f"performance_sampled_{cfg['evaluation']['mode']}.csv"))
    else:
        pd_results2.to_csv(os.path.join(results_folder, f"performance_{cfg['evaluation']['mode']}.csv"))


if __name__ == '__main__':
    main()
