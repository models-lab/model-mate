import json
import logging
import os
import random
from collections import defaultdict
from typing import Optional

import hydra
from datasets.load import load_dataset
from datasets import Dataset
from omegaconf import DictConfig
from tqdm import tqdm

import common
from preprocess_dataset import SPECIAL_TOKEN
from train_transformer import EOL_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN
import re


class TokenMatcher:
    def __init__(self, name, cfg):
        self.name = name
        self.regexes = [re.compile(r) for r in cfg.regex]
        self.result = cfg.result
        self.tests = cfg.tests

    def do_self_test(self):
        for t in self.tests:
            match = self.match(t.value.split(' '), 0)
            print("Checking ", t.value, " with ", [str(r) for r in self.regexes])
            print("Result: ", match)

            assert t.expected == match

    def match(self, token_sequence, idx):
        current_idx = idx
        matches = []
        for regex in self.regexes:
            if current_idx == len(token_sequence):
                return None

            token = token_sequence[current_idx]
            m = regex.match(token)
            if m is None:
                return None

            matches.append(m)
            current_idx = current_idx + 1

        return matches[self.result].group(0)


class Language:
    """A simple specification of a language"""

    def __init__(self, cfg):
        self.keywords: list[str] = cfg.keywords if 'keywords' in cfg else []
        self.matchers: list[TokenMatcher] = [TokenMatcher(name, m) for name, m in cfg.matches.items()] if 'matches' in cfg else []
        for m in self.matchers:
            m.do_self_test()

    @property
    def token_type_names(self):
        return self.keywords + [m.name for m in self.matchers]

    def match(self, token_sequence, idx):
        for m in self.matchers:
            matched_string: Optional[str] = m.match(token_sequence, idx)
            if matched_string is not None:
                return matched_string, m
        return None, None


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


def generate_samples_regex(sample, language):
    output = defaultdict(list)

    tokens = sample.split(' ')
    position = 0
    for idx, token in enumerate(tokens):
        expected_token, match = language.match(tokens, idx)
        offset = 0

        if expected_token is not None:
            offset = match.result * 2
            # This is the position of the matched token (e.g., : Type <EOL>) => result = 1
            # Multiply by 2 to account for the spaces

            input_seq = sample[:(position + offset - 1)]
            output[match.name].append((input_seq, expected_token))

        position = position + len(token) + 1

    return output


def generate_samples_block(sample, block_spec):
    start = block_spec.start
    end = block_spec.end

    tokens = sample.split(" ")
    pairs = []
    f_index = None
    for j, t in enumerate(tokens):
        if t == start:
            f_index = j
        elif t == end and f_index is not None:
            context = " ".join(tokens[0: f_index + 1])
            expected = " ".join(tokens[f_index + 1: j + 1])

            pairs.append((context, expected))
            f_index = None
    return pairs


SPECIAL_TOKEN_IGNORE: 'list[str]' = [EOL_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN, SPECIAL_TOKEN]


def generate_samples_token(sample):
    all_tokens = sample.split(' ')
    return [(' '.join(all_tokens[0:j + 1]), token) for j, token in enumerate(all_tokens[1:])
            if token not in SPECIAL_TOKEN_IGNORE]


def generate_samples_line(sample):
    all_lines = sample.split(f' {EOL_TOKEN} ')
    pairs = [(f' {EOL_TOKEN} '.join(all_lines[0:j + 1]) + f' {EOL_TOKEN}', line) for j, line in
            enumerate(all_lines[1:]) if line not in SPECIAL_TOKEN_IGNORE]
    return [(context, line) for context, line in pairs if len(line) > 2]



@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    random.seed(cfg['run']['seed'])

<<<<<<< HEAD
    train_data_folder: str = common.get_train_data_folder(cfg)
=======
    train_data_folder = common.get_train_data_folder(cfg)
>>>>>>> 03ad019 (Typing.)
    dataset: Dataset = load_dataset("text",
                           data_files={"test": os.path.join(train_data_folder, cfg['run']['test_file'])})["test"]

    logging.getLogger().info(f"Generate parsed test dataset mode={cfg['evaluation']['mode']}")

    language = Language(cfg.language)

    if cfg['evaluation']['mode'] == 'token-id':
        samples_per_token_id: int = cfg['evaluation']['samples_token_id']

        # token id
        output = defaultdict(list)
        for sample in tqdm(dataset["text"], desc='Parsing'):
            for kw in language.keywords:
                pairs_temp = generate_samples_kw(sample, kw)
                if len(pairs_temp) > samples_per_token_id:
                    pairs_temp = random.sample(pairs_temp, samples_per_token_id)
                output[kw] += pairs_temp

            pairs_by_match = generate_samples_regex(sample, language)
            for key, pairs_temp in pairs_by_match.items():
                if len(pairs_temp) > samples_per_token_id:
                    pairs_temp = random.sample(pairs_temp, samples_per_token_id)
                output[key] += pairs_temp

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
            pairs_temp = generate_samples_block(sample, cfg.language.block)
            if len(pairs_temp) > cfg['evaluation']['samples_block']:
                pairs_temp = random.sample(pairs_temp, cfg['evaluation']['samples_block'])
            output += pairs_temp
    else:
        raise ValueError('Mode not supported')

    filename = os.path.join(train_data_folder, f"parsed_test_{cfg['evaluation']['mode']}.json")
    with open(filename, 'w') as f:
        json.dump(output, f)

    print("Test file written in ", filename)


if __name__ == '__main__':
    main()
