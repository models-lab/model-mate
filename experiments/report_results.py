import os.path
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from collections import defaultdict

from tqdm import tqdm

from parse_test_dataset import KEYWORDS, SPECIAL_TOKEN_IGNORE
from run_inference import SEP


def get_atts_block(sample):
    tokens = sample.split(' ')
    atts = []
    for j, t in enumerate(tokens):
        if t == ';':
            atts.append(tokens[j - 1].lower())
    return atts


def compute_single_result(args, mode, result_file):
    try:
        results = pd.read_csv(result_file)
    except:
        print("Can't load ", result_file)
        if mode == 'token-id':
            return {kw: 0 for kw in KEYWORDS}
        elif mode == 'token':
            return {'accuracy': 0}
        elif mode == 'line':
            return {'EM': 0, 'Edit Similarity': 0}
        elif mode == 'block':
            return {'BLEU': 0, 'BLEU best k': 0, 'Recall attrs': 0}
        else:
            raise ValueError("Invalid mode")

    if mode == 'token-id':
        metrics = {}
        for kw in KEYWORDS:
            results_filtered = results[results["keyword"] == kw]
            print(len(results_filtered))
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

            value = np.mean(rrs) * 100
            print(f'MRR for kw {kw}: {value:.2f}')
            metrics[kw] = round(value, 2)
        return metrics

    elif mode == 'token':
        hits = 0
        for idx, row in results.iterrows():
            expected = row["expected"]
            if isinstance(expected, float):
                print("Non-string type in ", row)
                expected = str(expected)

            if type(row["suggestions"]) is not str:
                print(idx, row["suggestions"])
                continue

            suggestions = row["suggestions"].split(SEP)
            if expected.lower() == suggestions[0].lower():
                hits += 1
        accuracy = (hits / len(results)) * 100
        print(f'Accuracy: {accuracy:.2f}')
        return {'accuracy': accuracy}
    elif mode == 'line':
        hits = 0
        edit_sim = 0.0
        for _, row in results.iterrows():
            expected = row["expected"]
            suggestion = row["suggestions"].split(SEP)[0]
            if expected.lower() == suggestion.lower():
                hits += 1
            edit_sim += fuzz.ratio(suggestion.lower(), expected.lower())

        em = (hits / len(results)) * 100
        es = edit_sim / len(results)
        print(f'EM: {em:.2f}')
        print(f'Edit Similarity: {es:.2f}')
        return {'EM': round(em, 2), 'Edit Similarity': round(es, 2)}

    elif mode == 'block':
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

        r_all_bleus = np.mean(all_bleus) * 100
        r_all_k_bleus = np.mean(all_bleus_k) * 100
        r_att_names = np.mean(recall_att_names) * 100
        print(f'BLEU: {r_all_bleus:.2f}')
        print(f'BLEU best k: {r_all_k_bleus:.2f}')
        print(f'Recall attrs: {r_att_names:.2f}')

        return {'BLEU': round(r_all_bleus, 2), 'BLEU best k': round(r_all_k_bleus, 2),
                'Recall attrs': round(r_att_names, 2)}

    elif args.mode == 'performance':
        quartiles = results["predlen"].quantile([0.25, 0.5, 0.75])
        print(quartiles)
        print(np.mean(results["time"]))

        # Create bucket intervals based on quartiles
        bucket_intervals = [(0, quartiles[0.25]), (quartiles[0.25], quartiles[0.5]),
                            (quartiles[0.5], quartiles[0.75]), (quartiles[0.75], results["predlen"].max())]

        # Dictionary to store buckets and their respective times and counts
        buckets = defaultdict(lambda: {"sum_time": 0, "count": 0})

        # Populate buckets and calculate sum of times and counts
        for _, row in results.iterrows():
            len_value = row["predlen"]
            time_value = row["time"]

            # Find the appropriate bucket interval
            for interval in bucket_intervals:
                if interval[0] <= len_value <= interval[1]:
                    bucket_key = interval
                    break

            buckets[bucket_key]["sum_time"] += time_value
            buckets[bucket_key]["count"] += 1

        # Calculate mean time for each bucket
        mean_times = {interval: bucket["sum_time"] / bucket["count"] for interval, bucket in buckets.items()}

        # Plot bar plots for each bucket
        plt.figure(figsize=(10, 6))
        for interval, mean_time in mean_times.items():
            plt.bar(str(interval), mean_time, label=f"{interval}")

        plt.xlabel("Bucket Interval")
        plt.ylabel("Mean Time")
        plt.title("Mean Time for Each Bucket Interval")
        plt.legend()
        plt.savefig("mean_time_buckets.png")
        # plt.show()

        return mean_times
        
    raise ValueError("Invalid mode: " + mode)


def compute_results_by_mode(result_folder, mode):
    folders = result_folder.split(',')
    files = [(os.path.basename(f), os.path.join(f, 'results_' + mode + '.csv')) for f in folders]

    rows = []
    for name, f in files:
        print("Processing ", f)
        result = {'Model': name}
        result.update(compute_single_result(args, mode, f))
        rows.append(result)

    import pandas as pd
    df = pd.DataFrame(rows)
    return df


def compute_all_results(args, result_folder):
    modes = ['token', 'token-id', 'line', 'block']
    df = compute_results_by_mode(result_folder, modes[0])
    for mode in modes[1:]:
        df2 = compute_results_by_mode(result_folder, mode)
        df = pd.merge(df, df2, on='Model', how='outer')

    df = format_dataframe(args, df)

    ltx = df.to_latex(index=False)
    print(ltx)

def compute_several_results(args, result_folder):
    folders = result_folder.split(',')
    files = [(os.path.basename(f), os.path.join(f, 'results_' + args.mode + '.csv')) for f in folders]
    # files = [join(result_folder, f) for f in listdir(result_folder) if isfile(join(result_folder, f))]

    rows = []
    for name, f in files:
        print("Processing ", f)
        result = {'Model': name}
        result.update(compute_single_result(args, args.mode, f))
        rows.append(result)

    import pandas as pd
    df = pd.DataFrame(rows)
    df = format_dataframe(args, df)

    ltx = df.to_latex(index=False)
    # ltx = df.to_latex(columns=['name', 'accuracy'])
    # ltx = stl.to_latex()
    print(ltx)


def format_dataframe(args, df):
    if args.mapping is None:
        return df
    
    if args.sort is not None:
        df = df.sort_values(by=[args.sort], ascending=False)
    import yaml
    with open(args.mapping, 'r') as file:
        mapping = yaml.safe_load(file)
    df['Model'].replace(mapping['models'], inplace=True)
    # print(mapping['models'])
    # for key, value in mapping['models'].items():
    #    if key in df:
    #        df = df.rename(columns={key: value})
    for key, value in mapping['metrics'].items():
        if key in df:
            df[key] = df[key].map(lambda x: round(x, 2))
            df = df.rename(columns={key: value})
    return df


def main(args):
    # if os.path.isdir(args.results):
    if "," in args.results:
        if args.mode == 'all':
            compute_all_results(args, args.results)
        else:
            compute_several_results(args, args.results)
    else:
        compute_single_result(args, args.mode, args.results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
<<<<<<< HEAD
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'line', 'token', 'block', 'performance'])
=======
    parser.add_argument('--mode', type=str, default='token-id', choices=['all', 'token-id', 'line', 'token', 'block'])
>>>>>>> 3261a2e (Report results able to aggregate everything in a single table)
    parser.add_argument('--results', required=True)
    parser.add_argument('--sort', required=False)
    parser.add_argument('--mapping', required=False, default='mapping.yaml')
    args = parser.parse_args()
    main(args)
