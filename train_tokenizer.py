import argparse
import os.path

from datasets import load_dataset
from tokenizers.implementations import ByteLevelBPETokenizer
from transformers import AutoConfig

from preprocess_dataset import TRAIN_TXT, SPECIAL_TOKEN


def main(args):

    model_config = args.model_config
    model_dir = model_config + "-enfatic"
    tokenizer_json = os.path.join(model_dir, "tokenizer.json")

    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT)})["train"]
    tokenizer = ByteLevelBPETokenizer()
    # consider gpt-2 model from scratch
    config = AutoConfig.from_pretrained(model_config)

    def batch_iterator(batch_size=100):
        for i in range(0, len(dataset), batch_size):
            yield dataset[i: i + batch_size]["text"]

    tokenizer.train_from_iterator(batch_iterator(), vocab_size=config.vocab_size, min_frequency=2, special_tokens=[
        "<s>",
        "</s>",
        "<unk>",
        SPECIAL_TOKEN,
    ])
    os.makedirs(model_dir, exist_ok=True)
    tokenizer.save(tokenizer_json)

    config.save_pretrained(model_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    parser.add_argument("--model_config", default="gpt2", choices=["distilgpt2",
                                                                   "gpt2"])
    args = parser.parse_args()
    main(args)
