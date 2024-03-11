import os.path

import evaluate
import hydra
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from omegaconf import DictConfig
from tqdm import tqdm

import common
from parse_test_dataset import KEYWORDS, SPECIAL_TOKEN_IGNORE
from run_inference import SEP


def get_atts_block(sample):
    tokens = sample.split(' ')
    atts = []
    for j, t in enumerate(tokens):
        if t == ';':
            atts.append(tokens[j - 1].lower())
    return atts


def compute_single_result(cfg, result_file):
    results = pd.read_csv(result_file)
    if cfg['evaluation']['mode'] == 'token-id':

        for kw in KEYWORDS:
            results_filtered = results[results["keyword"] == kw]

            rrs = []
            for _, row in results_filtered.iterrows():
                expected = row["expected"]
                suggestions = row["suggestions"].split(SEP)

                rr = 0
                for j, suggestion in enumerate(suggestions):
                    if expected.lower() == suggestion.lower():
                        rr = 1 / (j + 1)
                        break
                rrs.append(rr)

            print(f'MRR for kw {kw}: {np.mean(rrs) * 100:.2f}')

    elif cfg['evaluation']['mode'] == 'token':
        hits = 0
        for idx, row in results.iterrows():
            expected = row["expected"]
            if type(row["suggestions"]) is not str:
                print(idx, row["suggestions"])
                continue

            suggestions = row["suggestions"].split(SEP)
            if expected.lower() == suggestions[0].lower():
                hits += 1
        accuracy = (hits / len(results)) * 100
        print(f'Accuracy: {accuracy:.2f}')
        return {'accuracy': accuracy}
    elif cfg['evaluation']['mode'] == 'line':
        hits = 0
        edit_sim = 0.0
        for _, row in results.iterrows():
            expected = row["expected"]
            suggestion = row["suggestions"].split(SEP)[0]
            if expected.lower() == suggestion.lower():
                hits += 1
            edit_sim += fuzz.ratio(suggestion.lower(), expected.lower())
        print(f'EM: {(hits / len(results)) * 100:.2f}')
        print(f'Edit Similarity: {edit_sim / len(results):.2f}')
    elif cfg['evaluation']['mode'] == 'block':
        all_bleus_k = []
        all_bleus = []
        recall_att_names = []
        for _, row in tqdm(results.iterrows(), total=len(results)):
            expected = row["expected"]
            expected_atts = get_atts_block(expected)
            suggestions = row["suggestions"].split(SEP)
            pred_atts = get_atts_block(suggestions[0])
            if len(expected_atts) != 0:
                hits = set([att for att in expected_atts if att in pred_atts])
                alls = set(expected_atts)
                recall_att_names.append(len(hits) / len(alls))

            expected = [s.lower() for s in expected.split() if s not in SPECIAL_TOKEN_IGNORE]
            bleus_temp = []
            for suggestion in suggestions:
                suggestion = [s.lower() for s in suggestion.split() if s not in SPECIAL_TOKEN_IGNORE]

                bleus_temp.append(sentence_bleu([expected], suggestion,
                                                smoothing_function=SmoothingFunction().method4))
            all_bleus_k.append(max(bleus_temp))
            all_bleus.append(sentence_bleu([expected], [s.lower() for s in suggestions[0].split()
                                                        if s not in SPECIAL_TOKEN_IGNORE],
                                           smoothing_function=SmoothingFunction().method4))

        print(f'BLEU: {np.mean(all_bleus) * 100:.2f}')
        print(f'BLEU best k: {np.mean(all_bleus_k) * 100:.2f}')
        print(f'Recall attrs: {np.mean(recall_att_names) * 100:.2f}')


def compute_several_results(args, result_folder):
    from os import listdir
    from os.path import isfile, join

    files = [join(result_folder, f) for f in listdir(result_folder) if isfile(join(result_folder, f))]

    rows = []
    for f in files:
        print(f)
        if not f.endswith('csv'):
            continue

        print("Processing ", f)
        result = compute_single_result(args, f)
        result['name'] = os.path.basename(f)
        rows.append(result)

    import pandas as pd
    df = pd.DataFrame(rows)
    print(df)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    train_data_folder = common.get_train_data_folder(cfg)
    compute_single_result(cfg, os.path.join(train_data_folder, f"results_{cfg['evaluation']['mode']}.csv"))


if __name__ == '__main__':
    main()
