import json
import logging
import os
import random
from collections import defaultdict

import hydra
from datasets import load_dataset
from omegaconf import DictConfig
from tqdm import tqdm

import common
from preprocess_dataset import SPECIAL_TOKEN
from train_transformer import EOL_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN


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


def generate_samples_block(sample):
    tokens = sample.split(" ")
    pairs = []
    f_index = None
    for j, t in enumerate(tokens):
        if t == "{":
            f_index = j
        elif t == "}":
            context = " ".join(tokens[0: f_index + 1])
            expected = " ".join(tokens[f_index + 1: j + 1])
            pairs.append((context, expected))
    return pairs


SPECIAL_TOKEN_IGNORE = [EOL_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN, SPECIAL_TOKEN]


def generate_samples_token(sample):
    all_tokens = sample.split(' ')
    return [(' '.join(all_tokens[0:j + 1]), token) for j, token in enumerate(all_tokens[1:])
            if token not in SPECIAL_TOKEN_IGNORE]


def generate_samples_line(sample):
    all_lines = sample.split(f' {EOL_TOKEN} ')
    return [(f' {EOL_TOKEN} '.join(all_lines[0:j + 1]) + f' {EOL_TOKEN}', line) for j, line in
            enumerate(all_lines[1:]) if line not in SPECIAL_TOKEN_IGNORE]


KEYWORDS = ["class", "attr", "ref", "extends", "package", "val"]


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    random.seed(cfg['run']['seed'])

    train_data_folder = common.get_train_data_folder(cfg)
    dataset = load_dataset("text",
                           data_files={"test": os.path.join(train_data_folder, cfg['run']['test_file'])})["test"]

    logging.getLogger().info(f"Generate parsed test dataset mode={cfg['evaluation']['mode']}")

    if cfg['evaluation']['mode'] == 'token-id':
        # token id
        output = defaultdict(list)
        for sample in tqdm(dataset["text"], desc='Parsing'):
            for kw in KEYWORDS:
                pairs_temp = generate_samples_kw(sample, kw)
                if len(pairs_temp) > cfg['evaluation']['samples_token_id']:
                    pairs_temp = random.sample(pairs_temp, cfg['evaluation']['samples_token_id'])
                output[kw] += pairs_temp
    elif cfg['evaluation']['mode'] == 'token':
        # random token
        output = []
        for sample in tqdm(dataset["text"], desc='Parsing'):
            pairs_temp = generate_samples_token(sample)
            if len(pairs_temp) > cfg['evaluation']['samples_token']:
                pairs_temp = random.sample(pairs_temp, cfg['evaluation']['samples_token'])
            output += pairs_temp
    elif cfg['evaluation']['mode'] == 'line':
        # line
        output = []
        for sample in tqdm(dataset["text"], desc='Parsing'):
            pairs_temp = generate_samples_line(sample)
            if len(pairs_temp) > cfg['evaluation']['samples_line']:
                pairs_temp = random.sample(pairs_temp, cfg['evaluation']['samples_line'])
            output += pairs_temp
    elif cfg['evaluation']['mode'] == 'block':
        output = []
        for sample in tqdm(dataset["text"], desc='Parsing'):
            pairs_temp = generate_samples_block(sample)
            if len(pairs_temp) > cfg['evaluation']['samples_block']:
                pairs_temp = random.sample(pairs_temp, cfg['evaluation']['samples_block'])
            output += pairs_temp
    else:
        raise ValueError('Mode not supported')

    with open(os.path.join(train_data_folder, f"parsed_test_{cfg['evaluation']['mode']}.json"), 'w') as f:
        json.dump(output, f)


if __name__ == '__main__':
    main()
