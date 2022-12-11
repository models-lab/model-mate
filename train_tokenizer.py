import argparse
import os.path

from datasets import load_dataset
from tokenizers.implementations import ByteLevelBPETokenizer
from transformers import AutoConfig

from preprocess_dataset import TRAIN_TXT, SPECIAL_TOKEN

MODEL_CONFIG = "distilgpt2"
MODEL_DIR = MODEL_CONFIG + "-enfatic"
TOKENIZER_JSON = os.path.join(MODEL_DIR, "tokenizer.json")


def main(args):
    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT)})["train"]
    tokenizer = ByteLevelBPETokenizer()
    config = AutoConfig.from_pretrained(MODEL_CONFIG)

    def batch_iterator(batch_size=100):
        for i in range(0, len(dataset), batch_size):
            yield dataset[i: i + batch_size]["text"]

    tokenizer.train_from_iterator(batch_iterator(), vocab_size=config.vocab_size, min_frequency=2, special_tokens=[
        "<s>",
        "</s>",
        "<unk>",
        "<pad>",
        "<mask>",
        SPECIAL_TOKEN,
    ])
    os.makedirs(MODEL_DIR, exist_ok=True)
    tokenizer.save(TOKENIZER_JSON)

    config.n_layer = 3
    config.n_head = 6
    config.save_pretrained(MODEL_DIR)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    args = parser.parse_args()
    main(args)
