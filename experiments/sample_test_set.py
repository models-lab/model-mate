import argparse
from parse_test_dataset import *
import tiktoken

def main(args):
    random.seed(args.seed)
    KEYWORDS = ["class", "attr", "ref", "extends", "package", "val"]
    with open(args.parsed_test) as f:
        parsed_test = json.load(f)

    if args.mode == 'token-id':
        filtered_parsed_test = {keyword: [x for x in parsed_test[keyword] if len(x[0].split()) <= 2000] for keyword in
                                KEYWORDS}
        for kw in KEYWORDS:
            if len(filtered_parsed_test[kw]) > 200:
                filtered_parsed_test[kw] = random.sample(filtered_parsed_test[kw], 200)
        with open("data/temp/modelset_token/parsed_test_sampled_token-id22222.json", 'w') as file:
            json.dump(filtered_parsed_test, file)

    elif args.mode == 'line':
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-instruct')
        pt = [x for x in parsed_test if len(encoding.encode(x[0])) <= 3500]
        if len(pt) > 1000:
            pt = random.sample(pt, 1000)
        with open("data/temp/modelset_line/parsed_test_sampled_line.json", 'w') as file:
            json.dump(pt, file)

    elif args.mode == 'block':
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-instruct')
        pt = [x for x in parsed_test if len(encoding.encode(x[0])) <= 3500]
        if len(pt) > 1000:
            pt = random.sample(pt, 1000)
        with open("data/temp/modelset_token/parsed_test_sampled_block.json", 'w') as file:
            json.dump(pt, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'token', 'line', 'block'])
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--parsed_test', default='data/temp/modelset_token/parsed_test_token-id.json')
    args = parser.parse_args()
    main(args)