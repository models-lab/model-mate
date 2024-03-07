import argparse

import numpy as np
import pandas as pd

from parse_test_dataset import KEYWORDS
from run_inference import SEP
from fuzzywuzzy import fuzz


def main(args):
    results = pd.read_csv(args.results)
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
        for _, row in results.iterrows():
            expected = row["expected"]
            suggestions = row["suggestions"].split(SEP)
            if expected.lower() == suggestions[0].lower():
                hits += 1
        print(f'Accuracy: {(hits/len(results)) * 100:.2f}')

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




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'line', 'token'])
    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2-medium.csv')
    args = parser.parse_args()
    main(args)
