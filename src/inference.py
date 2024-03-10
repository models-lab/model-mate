import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StoppingCriteria


class EndOfFunctionCriteriaToken(StoppingCriteria):

    def __init__(self, tokenizer, start_length=0):
        self.tokenizer = tokenizer
        self.start_length = start_length

    def __call__(self, input_ids, scores, **kwargs):        
        decoded_generations = self.tokenizer.batch_decode(input_ids[:, self.start_length:])
        done = []
        for decoded_generation in decoded_generations:
            done.append(decoded_generation.count(' ') > 1)
        return all(done)
                                    
        #for decoded_generation in decoded_generations:
        #    if decoded_generation.count(' ') > 1:
        #        return False
        #return True



class TokenInference:
    def __init__(self, model, device='cuda'):
        self.model = AutoModelForCausalLM.from_pretrained(model, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.device = device

    def get_suggestions_next_token(self, input, num_suggestions, max_new_tokens=10, max_length=512):
        model = self.model
        tokenizer = self.tokenizer

        sample = tokenizer([input], return_tensors="pt")
        sample["input_ids"] = sample["input_ids"][:, -(max_length - max_new_tokens):]
        sample["attention_mask"] = sample["attention_mask"][:, -(max_length - max_new_tokens):]
        with torch.no_grad():
            criteria = EndOfFunctionCriteriaToken(tokenizer, sample["input_ids"].shape[1])
            generated_sequences = model.generate(
                input_ids=self.to_device(sample["input_ids"]),
                attention_mask=self.to_device(sample["attention_mask"]),
                do_sample=False,
                max_new_tokens=max_new_tokens,
                num_return_sequences=num_suggestions,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                num_beams=num_suggestions,
                stopping_criteria=StoppingCriteriaList([criteria])
            )

        generated_sequences = generated_sequences.cpu().numpy()
        generated_new_tokens = generated_sequences[:, sample["input_ids"].shape[1]:]

        suggestions = []
        for k, new_tokens in enumerate(generated_new_tokens):
            generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
            data = generated.split(' ')
            if len(data) <= 1:
                break
            suggestions.append(data[1])
        return suggestions

    def to_device(self, v):
        if self.device == 'cuda' and torch.cuda.is_available():
            return v.cuda()
        return v

    def generate_fragment(self, input, stop=None):
        if stop is None:
            stop = [';']

        result = []
        while True:
            suggestions = self.get_suggestions_next_token(input, 1)
            if len(suggestions) == 0:
                break
            token = suggestions[0]
            #print("T: ", token)
            if token in stop:
                break
            input = input + ' ' + token
            result.append(token)

        return result
