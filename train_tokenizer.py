import argparse
import os.path

from datasets import load_dataset
from tokenizers.implementations import ByteLevelBPETokenizer
from transformers import AutoConfig

from preprocess_dataset import TRAIN_TXT

TOKENIZER_FOLDER = 'tokenizers'


def main(args):
    model_dir = "tokenizer-enfatic" + f"-{args.level}"
    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT)})["train"]
    tokenizer = ByteLevelBPETokenizer()
    config = AutoConfig.from_pretrained("gpt2")

    def batch_iterator(batch_size=100):
        for i in range(0, len(dataset), batch_size):
            yield dataset[i: i + batch_size]["text"]

    tokenizer.train_from_iterator(batch_iterator(),
                                  vocab_size=config.vocab_size,
                                  min_frequency=2)

    os.makedirs(os.path.join(TOKENIZER_FOLDER, model_dir), exist_ok=True)
    tokenizer.save_model(os.path.join(TOKENIZER_FOLDER, model_dir))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset_token_level",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    parser.add_argument("--level", default="token", choices=["token", "line"])
    args = parser.parse_args()
    main(args)
