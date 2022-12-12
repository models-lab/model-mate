import argparse
import os

from datasets import load_dataset
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, GPT2LMHeadModel, \
    AutoConfig, EarlyStoppingCallback

from preprocess_dataset import TRAIN_TXT, TEST_TXT, VAL_TXT, SPECIAL_TOKEN


def main(args):
    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT),
                                               "test": os.path.join(args.dataset, TEST_TXT),
                                               "val": os.path.join(args.dataset, VAL_TXT)})
    if args.is_pretrained:
        model_dir = args.huggingface_model
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}", bos_token='<s>',
                                                  eos_token='</s>', pad_token='</s>',
                                                  unk_token='<unk>')
        tokenizer.add_tokens([SPECIAL_TOKEN])
    else:
        model_dir = args.model_dir
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}", bos_token='<s>',
                                                  eos_token='</s>', pad_token='</s>',
                                                  special_tokens=[SPECIAL_TOKEN],
                                                  unk_token='<unk>')
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
        input_batch = []
        for length, input_ids in zip(outputs["length"], outputs["input_ids"]):
            if length == context_length:  # always true
                input_batch.append(input_ids)
        return {"input_ids": input_batch}

    tokenized_datasets = dataset.map(
        tokenize, batched=True, remove_columns=dataset["train"].column_names
    )

    print(dataset)
    print(tokenized_datasets)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    if args.is_pretrained:
        model = GPT2LMHeadModel.from_pretrained(model_dir)
        model.resize_token_embeddings(len(tokenizer))
    else:
        config = AutoConfig.from_pretrained(model_dir)
        model = GPT2LMHeadModel(config)
        model.resize_token_embeddings(len(tokenizer))

    print(model.transformer.wte.weight.shape[0])
    print(len(tokenizer))

    args_training = TrainingArguments(
        output_dir=args.output_path_model,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        gradient_accumulation_steps=8,
        num_train_epochs=10,
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

    best_ckpt_path = trainer.state.best_model_checkpoint
    print(best_ckpt_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    parser.add_argument("--output_path_model")
    parser.add_argument("--huggingface_model", default='')
    parser.add_argument("--model_dir", default='')
    parser.add_argument("--is_pretrained", action='store_true')
    parser.add_argument("--context_length", default=128,
                        help="context_length", type=int)
    parser.add_argument("--schedule", choices=["linear", "constant"])
    args = parser.parse_args()
    main(args)
