import os.path

import hydra
from datasets import load_dataset
from omegaconf import DictConfig
from tokenizers.implementations import ByteLevelBPETokenizer
from transformers import AutoConfig


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    model_dir = "tokenizer-emfatic" + f"-{cfg['dataset']['level']}"
    dataset = load_dataset("text", data_files={"train": os.path.join(cfg['dataset']['path'],
                                                                     cfg['run']['train_file'])})["train"]
    tokenizer = ByteLevelBPETokenizer()
    config = AutoConfig.from_pretrained("gpt2")

    def batch_iterator(batch_size=100):
        for i in range(0, len(dataset), batch_size):
            yield dataset[i: i + batch_size]["text"]

    tokenizer.train_from_iterator(batch_iterator(),
                                  vocab_size=config.vocab_size,
                                  min_frequency=2)

    os.makedirs(os.path.join(cfg['run']['tokenizers_folder'], model_dir), exist_ok=True)
    tokenizer.save_model(os.path.join(cfg['run']['tokenizers_folder'], model_dir))


if __name__ == '__main__':
    main()
