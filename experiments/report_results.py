import argparse
import os.path

import numpy as np
import pandas as pd

from parse_test_dataset import KEYWORDS
from run_inference import SEP
from fuzzywuzzy import fuzz


def compute_single_result(args, result_file):
    results = pd.read_csv(result_file)
    if args.mode == 'token-id':

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

    elif args.mode == 'token':
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
    elif args.mode == 'line':
        hits = 0
        edit_sim = 0.0
        for _, row in results.iterrows():
            expected = row["expected"]
            suggestion = row["suggestions"]
            print(expected)
            print("AA")
            print(suggestion)
            if expected.lower() == suggestion.lower():
                hits += 1
            edit_sim += fuzz.ratio(suggestion.lower(), expected.lower())
        print(f'EM: {(hits / len(results)) * 100:.2f}')
        print(f'Edit Similarity: {edit_sim / len(results) * 100:.2f}')
    ###   # Calculate EM and edit similarity
    ## total = len(gts)
    #  em = 0.0
    #   edit_sim = 0.0
    #   for pred, gt in zip(preds, gts):
    #       gt = json.loads(gt)["gt"]
    #       edit_sim += fuzz.ratio(pred, gt)
    #       if pred.split() == gt.split():
    #           em += 1
    #   print(self.model)


#   logger.info(f"Edit sim: {round(edit_sim / total, 2)}, EM: {round(em / total * 100, 2)}\n")


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


def main(args):
    if os.path.isdir(args.results):
        compute_several_results(args, args.results)
    else:
        compute_single_result(args, args.results)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'line', 'token'])
    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2-medium.csv')
    args = parser.parse_args()
    main(args)
