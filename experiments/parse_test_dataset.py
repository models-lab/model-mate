import argparse
import json
import random
from collections import defaultdict

from datasets import load_dataset
from tqdm import tqdm


def generate_samples_kw(sample, keyword="class"):
    positions = []
    start_index = 0
    while True:
        index = sample.find(f" {keyword} ", start_index)
        if index == -1:
            break
        positions.append(index + len(keyword) + 1)
        start_index = index + 1

    pairs = []
    for p in positions:
        input_seq = sample[:p]
        output_token = sample[p + 1:].split(' ')[0]
        pairs.append((input_seq, output_token))
    return pairs


def generate_samples_token(sample):
    all_tokens = sample.split(' ')
    return [(' '.join(all_tokens[0:j + 1]), token) for j, token in enumerate(all_tokens[1:])]

def generate_samples_line(sample, keyword="class"):
    positions = []
    start_index = 0
    while True:
        index = sample.find(f" {keyword} ", start_index)
        if index == -1:
            break
        positions.append(index + len(keyword) + 1)
        start_index = index + 1

    pairs = []
    for p in positions:
        input_seq = sample[:p]
        # Output is until <EOL> token.
        idx = p+1
        while sample[idx] != '<' or sample[idx+1] != 'E' or sample[idx+2] != 'O' or sample[idx+3] != 'L' or sample[idx+4] != '>':
            idx += 1
        output_token = sample[p + 1: idx + 5]
        pairs.append((input_seq, output_token))
    return pairs

KEYWORDS = ["class", "attr", "ref", "extends", "package", "val"]

def main(args):
    random.seed(args.seed)
    dataset = load_dataset("text", data_files={"test": args.test_set})["test"]

    if args.mode == 'token-id':
        output = defaultdict(list)
        for sample in tqdm(dataset["text"], desc='Parsing'):
            for kw in KEYWORDS:
                pairs_temp = generate_samples_kw(sample, kw)
                if len(pairs_temp) > args.n:
                    pairs_temp = random.sample(pairs_temp, args.n)
                output[kw] += pairs_temp
    elif args.mode == 'token':
        output = []
        for sample in tqdm(dataset["text"], desc='Parsing'):
            pairs_temp = generate_samples_token(sample)
            if len(pairs_temp) > args.n:
                pairs_temp = random.sample(pairs_temp, args.n)
            output += pairs_temp
    elif args.mode == 'line':
        output = []
        for sample in tqdm(dataset["text"], desc='Parsing'):
            for kw in KEYWORDS:
                pairs_temp = generate_samples_line(sample, kw)
                if len(pairs_temp) > args.n:
                    pairs_temp = random.sample(pairs_temp, args.n)
                output += pairs_temp

    else:
        raise ValueError(f'{args.mode} invalid')

    with open(args.parsed_test, 'w') as f:
        json.dump(output, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--test_set', type=str, default='data/temp/modelset_token/test.txt',
                        help='metamodels dataset folder')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'token', 'line'])
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--parsed_test', default='data/temp/modelset_token/test_parsed_token-id.json')
    args = parser.parse_args()
    main(args)
