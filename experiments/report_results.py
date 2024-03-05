import argparse

import numpy as np
import pandas as pd

from parse_test_dataset import KEYWORDS
from run_inference import SEP


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'line', 'token'])
    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2.csv')
    args = parser.parse_args()
    main(args)
