import argparse
import logging
import os
import sys
from pathlib import Path

from datasets import load_dataset
from prettytable import PrettyTable
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, GPT2LMHeadModel, \
    AutoConfig, EarlyStoppingCallback, GPT2TokenizerFast

from preprocess_dataset import TRAIN_TXT, TEST_TXT, VAL_TXT, SPECIAL_TOKEN

EOL_TOKEN = '<EOL>'
BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
UNK_TOKEN = '<unk>'

MODELS_FOLDER = 'runs'
BEST_MODEL = 'best-model'


def print_command_and_args():
    logger = logging.getLogger()
    logger.info('COMMAND: {}'.format(' '.join(sys.argv)))
    config_table = PrettyTable()
    config_table.field_names = ["Configuration", "Value"]
    config_table.align["Configuration"] = "l"
    config_table.align["Value"] = "l"
    for config, value in vars(args).items():
        config_table.add_row([config, str(value)])
    logger.info('Configuration:\n{}'.format(config_table))


def setup_logger(log_file):
    # std out
    logger = logging.getLogger()
    logger.setLevel(level=logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    # file out
    if log_file is not None:
        file = logging.FileHandler(log_file)
        file.setLevel(level=logging.INFO)
        formatter = logging.Formatter('[%(asctime)s | %(filename)s | line %(lineno)d] - %(levelname)s: %(message)s')
        file.setFormatter(formatter)
        logger.addHandler(file)


def check_tokens(tokenizer):
    for special in [SPECIAL_TOKEN, EOL_TOKEN, UNK_TOKEN, EOS_TOKEN, BOS_TOKEN]:
        logger = logging.getLogger()
        logger.info(f'Checking token {special}: {len(tokenizer.tokenize(special)) == 1}')
        assert len(tokenizer.tokenize(special)) == 1


def main(args):
    logger = logging.getLogger()

    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT),
                                               "test": os.path.join(args.dataset, TEST_TXT),
                                               "val": os.path.join(args.dataset, VAL_TXT)})
    if args.is_pretrained:
        model_dir = args.huggingface_model
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}", bos_token=BOS_TOKEN,
                                                  eos_token=EOS_TOKEN, pad_token=EOS_TOKEN,
                                                  unk_token=UNK_TOKEN)
    else:
        model_dir = args.model_dir
        tokenizer = GPT2TokenizerFast(vocab_file=os.path.join(model_dir, 'vocab.json'),
                                      merges_file=os.path.join(model_dir, 'merges.txt'),
                                      bos_token=BOS_TOKEN, eos_token=EOS_TOKEN,
                                      pad_token=EOS_TOKEN, unk_token=UNK_TOKEN)
        tokenizer.add_tokens([UNK_TOKEN, EOS_TOKEN, BOS_TOKEN])

    tokenizer.add_tokens([SPECIAL_TOKEN, EOL_TOKEN])
    context_length = args.context_length

    def tokenize(element):
        outputs = tokenizer(
            element["text"],
            truncation=True,
            max_length=context_length,
            return_overflowing_tokens=True,
            return_length=True,
            padding='max_length'
        )
        input_batch = [input_ids for input_ids in outputs["input_ids"]]
        return {"input_ids": input_batch}

    tokenized_datasets = dataset.map(
        tokenize, batched=True, remove_columns=dataset["train"].column_names
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    if args.is_pretrained:
        model = GPT2LMHeadModel.from_pretrained(model_dir)
        model.resize_token_embeddings(len(tokenizer))
    else:
        config = AutoConfig.from_pretrained("gpt2",
                                            vocab_size=len(tokenizer),
                                            n_ctx=context_length,
                                            bos_token_id=tokenizer.bos_token_id,
                                            eos_token_id=tokenizer.eos_token_id)
        model = GPT2LMHeadModel(config)
        model.resize_token_embeddings(len(tokenizer))

    logger.info(f'Checking input embeddings: {model.transformer.wte.weight.shape[0]}, {len(tokenizer)}')

    output_dir = os.path.join(MODELS_FOLDER, f"{args.output_path_model}-{context_length}")
    args_training = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        gradient_accumulation_steps=8,
        num_train_epochs=args.epochs,
        weight_decay=0.1,
        learning_rate=1e-3,
        save_strategy="epoch",
        fp16=True,
        push_to_hub=False,
        metric_for_best_model='eval_loss',
        load_best_model_at_end=True,
        lr_scheduler_type=args.schedule
    )

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=args_training,
        data_collator=data_collator,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["val"],
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    trainer.train()

    logger.info('Renaming the best model!')
    best_ckpt_path = trainer.state.best_model_checkpoint
    parts = list(Path(best_ckpt_path).parts)[:-1] + [BEST_MODEL]
    new_path = os.path.join(*parts)
    os.rename(best_ckpt_path, new_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset_token_level",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    parser.add_argument("--output_path_model")
    parser.add_argument("--huggingface_model", default='')
    parser.add_argument("--model_dir", default='')
    parser.add_argument("--is_pretrained", action='store_true')
    parser.add_argument("--context_length", default=256,
                        help="context_length", type=int)
    parser.add_argument("--batch_size", default=8,
                        help="batch_size", type=int)
    parser.add_argument("--schedule", choices=["linear", "constant"],
                        default="linear")
    parser.add_argument("--epochs", default=10,
                        help="epochs", type=int)
    args = parser.parse_args()

    output_log_file = os.path.join(MODELS_FOLDER,
                                   f"{args.output_path_model}-{args.context_length}")
    os.makedirs(output_log_file, exist_ok=True)
    setup_logger(os.path.join(output_log_file, 'info.log'))
    print_command_and_args()

    main(args)
