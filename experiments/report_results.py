import argparse

import numpy as np
import pandas as pd

from parse_test_dataset import KEYWORDS
from run_inference import SEP
from fuzzywuzzy import fuzz
#from tabulate import tabulate

def eval_token(results):
    hits = 0
    for _, row in results.iterrows():
        expected = row["expected"]
        suggestions = row["suggestions"].split(SEP)
        if expected.lower() == suggestions[0].lower():
            hits += 1
    print(f'Accuracy: {(hits / len(results)) * 100:.2f}')
    return hits/len(results)*100

def eval_token_id(results):
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
    return np.mean(rrs) * 100


def eval_line(results):
    hits = 0
    edit_sim = 0.0
    for _, row in results.iterrows():
        expected = row["expected"]
        suggestion = row["suggestions"][2:-2].strip()
        print(expected)
        print("AA")
        print(suggestion)
        if expected.lower() == suggestion.lower():
            hits += 1
        edit_sim += fuzz.ratio(suggestion.lower(), expected.lower())
    print(f'EM: {(hits / len(results)) * 100:.2f}')
    print(f'Edit Similarity: {edit_sim / len(results):.2f}')
    return (hits/len(results)*100, edit_sim/len(results))

def main(args):
    if args.mode == 'token-id':
        results = pd.read_csv(args.results)
        eval_token_id(results)
    elif args.mode == 'token':
        results = pd.read_csv(args.results)
        eval_token(results)
    elif args.mode == 'line':
        results = pd.read_csv(args.results)
        eval_line(results)
    elif args.mode == 'all':
        token_files = []
        token_id_files = []
        line_files = []
        tok = []
        tokid0 = []
        tokid1 = []
        line = []
        for file in FILESTOKEN:
            results = pd.read_csv(file)
            tok.append([file, eval_token(results)])
        for file in FILESTOKENID:
            results = pd.read_csv(file)
            etokid = eval_token_id(results)
            tokid0.append([file, etokid[0]])
            tokid1.append([file, etokid[1]])
        for file in FILESLINE:
            results = pd.read_csv(file)
            line.append([file, eval_line(results)])
        # List all files in directory
        #token_table = tabulate(tok, ['Model', 'Accuracy'], tablefmt="latex")
        #token_id_table = tabulate(tokid0, ['Model', 'EM'], tablefmt="latex")
        #token_id_table2 = tabulate(tokid1, ['Model', 'Edit. Sim.'], tablefmt="latex")
        #line_table = tabulate(line, ['Model', 'MRR@5'], tablefmt="latex")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'line', 'token', 'all'])
    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2-medium.csv')
    parser.add_argument('--dirtoken', default='data/temp/modelset_token')
    parser.add_argument('--dirtokenid', default='data/temp/modelset_token')
    parser.add_argument('--dirline', default='data/temp/modelset_line')
    args = parser.parse_args()
    main(args)
