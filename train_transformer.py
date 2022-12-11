import argparse
import os

from datasets import load_dataset
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, GPT2LMHeadModel, \
    AutoConfig

from preprocess_dataset import TRAIN_TXT, TEST_TXT, VAL_TXT, SPECIAL_TOKEN
from train_tokenizer import MODEL_DIR


def main(args):
    dataset = load_dataset("text", data_files={"train": os.path.join(args.dataset, TRAIN_TXT),
                                               "test": os.path.join(args.dataset, TEST_TXT),
                                               "val": os.path.join(args.dataset, VAL_TXT)})
    if args.is_pretrained:
        model_dir = args.huggingface_model
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}", bos_token='<s>',
                                                  eos_token='</s>', pad_token='</s>')
    else:
        model_dir = MODEL_DIR
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}", bos_token='<s>',
                                                  eos_token='</s>', pad_token='</s>',
                                                  special_tokens=[SPECIAL_TOKEN])
    # print(tokenizer('<s> @ namespace ( uri = <STR_URI_PREFIX> , prefix = <STR_URI_PREFIX> ) package employee'))
    # print(tokenizer.pad_token)
    context_length = 128

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

    print(model.transformer.wte.weight.shape[0])
    print(len(tokenizer))

    args_training = TrainingArguments(
        output_dir=args.output_path_model,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        gradient_accumulation_steps=8,
        num_train_epochs=10,
        weight_decay=0.1,
        learning_rate=1e-3,
        save_strategy="epoch",
        fp16=True,
        push_to_hub=False
    )

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=args_training,
        data_collator=data_collator,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["val"]
    )

    trainer.train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed", type=int)
    parser.add_argument("--output_path_model")
    parser.add_argument("--huggingface_model", default='')
    parser.add_argument("--is_pretrained", action='store_true')
    args = parser.parse_args()
    main(args)
