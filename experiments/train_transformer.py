from logging import Logger, getLogger
import os
from pathlib import Path

import hydra
from datasets.load import load_dataset
from omegaconf import DictConfig
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, GPT2LMHeadModel, \
    AutoConfig, EarlyStoppingCallback, GPT2TokenizerFast, AutoModelForCausalLM
from transformers.tokenization_utils_base import BatchEncoding

import common
from preprocess_dataset import SPECIAL_TOKEN

EOL_TOKEN = '<EOL>'
BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
UNK_TOKEN = '<unk>'


def check_tokens(tokenizer):
    for special in [SPECIAL_TOKEN, EOL_TOKEN, UNK_TOKEN, EOS_TOKEN, BOS_TOKEN]:
        logger: Logger = getLogger()
        logger.info(f'Checking token {special}: {len(tokenizer.tokenize(special)) == 1}')
        assert len(tokenizer.tokenize(special)) == 1


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    logger: Logger = getLogger()
    logger.info(f'Training with: learning_rate = {cfg["params"]["learning_rate"]}')

    train_data_folder = common.get_train_data_folder(cfg)

    dataset = load_dataset("text", data_files={"train": os.path.join(train_data_folder, cfg['run']['train_file']),
                                               "test": os.path.join(train_data_folder, cfg['run']['test_file']),
                                               "val": os.path.join(train_data_folder, cfg['run']['val_file'])})
    if not cfg['model']['local_tokenizer']:
        tokenizer = AutoTokenizer.from_pretrained(cfg['model']['hugging_face_model'], bos_token=BOS_TOKEN,
                                                  eos_token=EOS_TOKEN, pad_token=EOS_TOKEN,
                                                  unk_token=UNK_TOKEN)
    else:
        tokenizer = GPT2TokenizerFast(vocab_file=os.path.join(cfg['run']['tokenizers_folder'],
                                                              f"{cfg['model']['tokenizer_dir']}"
                                                              f"-{cfg['dataset']['level']}",
                                                              'vocab.json'),
                                      merges_file=os.path.join(cfg['run']['tokenizers_folder'],
                                                               f"{cfg['model']['tokenizer_dir']}"
                                                               f"-{cfg['dataset']['level']}",
                                                               'merges.txt'),
                                      bos_token=BOS_TOKEN, eos_token=EOS_TOKEN,
                                      pad_token=EOS_TOKEN, unk_token=UNK_TOKEN)
        tokenizer.add_tokens([UNK_TOKEN, EOS_TOKEN, BOS_TOKEN])
    tokenizer.add_tokens([SPECIAL_TOKEN, EOL_TOKEN])

    check_tokens(tokenizer)

    context_length = cfg['params']['context_length']

    def tokenize(element):
        outputs: BatchEncoding = tokenizer(
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

    if cfg['model']['is_pretrained']:
        model = AutoModelForCausalLM.from_pretrained(cfg['model']['hugging_face_model'])
        model.resize_token_embeddings(len(tokenizer))
    else:
        config = AutoConfig.from_pretrained(cfg['model']['hugging_face_model'],
                                            vocab_size=len(tokenizer),
                                            n_ctx=context_length,
                                            bos_token_id=tokenizer.bos_token_id,
                                            eos_token_id=tokenizer.eos_token_id)
        model = GPT2LMHeadModel(config)
        model.resize_token_embeddings(len(tokenizer))

    # logger.info(f'Checking input embeddings: {model.transformer.wte.weight.shape[0]}, {len(tokenizer)}')

    output_dir = common.get_trained_model_folder(cfg)

    args_training = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=cfg['params']['batch_size'],
        per_device_eval_batch_size=cfg['params']['batch_size'],
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        gradient_accumulation_steps=cfg['params']['gradient_accumulation_steps'],
        num_train_epochs=cfg['params']['epochs'],
        weight_decay=0.1,
        learning_rate=cfg['params']['learning_rate'],
        save_strategy="epoch",
        fp16=True,
        push_to_hub=False,
        metric_for_best_model='eval_loss',
        load_best_model_at_end=True,
        lr_scheduler_type=cfg['params']['scheduler'],
        save_total_limit=2
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
    parts = list(Path(best_ckpt_path).parts)[:-1] + [cfg['run']['best_model_folder']]
    new_path = os.path.join(*parts)
    os.rename(best_ckpt_path, new_path)


if __name__ == '__main__':
    main()
