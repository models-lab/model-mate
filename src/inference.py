import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StoppingCriteria

# This comes from the train_transformer.py file in experiments/
EOL_TOKEN = '<EOL>'
BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
UNK_TOKEN = '<unk>'


class CriteriaToken(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            if decoded_generation.count(' ') <= 1:
                return False
        return True


class CriteriaLine(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        for decoded_generation in decoded_generations:
            dec_split = decoded_generation.split()
            if '<EOL>' not in dec_split:
                return False
        return True


class BaseInference:
    def __init__(self, model, device):
        self.model = AutoModelForCausalLM.from_pretrained(model, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.device = device
        if device == 'cpu':
            self.model.to("cpu")

    def generate(self,
                 input,
                 num_beams=5,
                 max_new_tokens=64,
                 context_length=512,
                 criteria=CriteriaToken, end_token=None):
        tokenizer = self.tokenizer
        model = self.model

        sample = tokenizer([input], return_tensors="pt")
        sample["input_ids"] = sample["input_ids"][:, -(context_length - max_new_tokens):]
        sample["attention_mask"] = sample["attention_mask"][:, -(context_length - max_new_tokens):]

        with torch.no_grad():
            if criteria:
                criteria = criteria(tokenizer, sample["input_ids"].shape[1])
                generated_sequences = model.generate(
                    input_ids=self.to_device(sample["input_ids"]),
                    attention_mask=self.to_device(sample["attention_mask"]),
                    do_sample=False,
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=num_beams,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    num_beams=num_beams,
                    stopping_criteria=StoppingCriteriaList([criteria])
                )
            else:
                generated_sequences = model.generate(
                    input_ids=self.to_device(sample["input_ids"]),
                    attention_mask=self.to_device(sample["attention_mask"]),
                    do_sample=False,
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=num_beams,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.convert_tokens_to_ids(end_token),
                    num_beams=num_beams
                )
        generated_sequences = generated_sequences.cpu().numpy()
        generated_new_tokens = generated_sequences[:, sample["input_ids"].shape[1]:]
        return generated_new_tokens

    def to_device(self, v):
        if self.device == 'cuda' and torch.cuda.is_available():
            return v.cuda()
        return v


class ModelInference(BaseInference):
    def __init__(self, model, device='cuda'):
        super().__init__(model, device)

    def get_suggestions_next_token(self, input, **kwargs):
        generated_new_tokens = self.generate(input, **self.to_params(kwargs))

        suggestions = []
        for k, new_tokens in enumerate(generated_new_tokens):
            generated = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            gsplit = generated.split(' ')
            if len(gsplit) >= 2:
                suggestions.append(generated.split(' ')[1])
        return suggestions

    def get_suggestions_next_line(self, input, **kwargs):
        generated_new_tokens = self.generate(input, criteria=None, end_token=EOL_TOKEN, **self.to_params(kwargs))

        suggestions = []
        for k, new_tokens in enumerate(generated_new_tokens):
            generated = self.tokenizer.decode(new_tokens, skip_special_tokens=True).split(EOL_TOKEN)[0].strip()
            suggestions.append(generated)
        return suggestions

    def get_suggestions_next_block(self, input, **kwargs):
        generated_new_tokens = self.generate(input, criteria=None, end_token='Ġ}', **self.to_params(kwargs))

        suggestions = []
        for k, new_tokens in enumerate(generated_new_tokens):
            generated = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            suggestions.append(generated)
        return suggestions

    def to_params(self, cfg):
        if "evaluation" in cfg:
            return {
                "num_beams": cfg['evaluation']['num_beams'],
                "max_new_tokens": cfg['evaluation']['max_new_tokens'],
                "context_length": cfg['params']['context_length']
            }
        else:
            return cfg