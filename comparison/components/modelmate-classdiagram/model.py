import os
import sys

sys.path.append(os.path.dirname(__file__))
from utils.model_io import ModelInOut, execute_model, ModelImplementation
import torch
from tqdm import tqdm
from transformers import RobertaTokenizerFast, RobertaForMaskedLM

from run_inference import get_suggestions_next_line

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

k = 5

class Model(ModelImplementation):
    def train(self, X, y, inout: ModelInOut):
        pass

    def ignore_train(self):
        return True

    def test(self, loaded_model, X, inout: ModelInOut):
        all_data = X

        from transformers import AutoTokenizer, AutoModelForCausalLM
        #model_path = os.path.join(inout.original, 'model', 'graphical-distil-gpt2')
        #model_path = os.path.join(inout.original, 'model', 'codeparrot-classdiagram')

        context_length = 512
        model_path = os.path.join(inout.original, 'model', 'codeparrot-cd-shuffled')

        #context_length = 1024
        #model_path = os.path.join(inout.original, 'model', 'codegen-multi-cd-shuffled')

        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        cfg = {
            "params": {
                "context_length": context_length
            },
            "evaluation": {
                "max_new_tokens": 16,
                "num_beams": 10,
                "mode": "line",
                "samples_token_id": 5,
                "samples_line": -1,
                "samples_token": 5,
                "samples_block": 5
            }
        }

        # max_new_tokens: 256


        all_suggestions = []
        all_data.reset_index()
        for idx, data in tqdm(all_data.iterrows(), desc='Loop over the data'):
            suggestions = []
            try:
                emfatic_input = data['emfatic'].strip()
                suggestions = self.do_suggestion(model, tokenizer, emfatic_input, cfg)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in {data['ids']}, owner {data['owner']}, target {data['target']}")
            all_suggestions.append(suggestions)

        return all_suggestions

    def do_suggestion(self, model, tokenizer, emfatic_input, cfg):
        suggestions = get_suggestions_next_line(model, tokenizer, emfatic_input, cfg)
        results = []
        for s in suggestions:
            r = self.parse_suggestion(s)
            if r != '}' and r not in results:
                results.append(r)

        # return [s[0] for s in sorted_suggestions][:5]
        return results[:5]

    def parse_suggestion(self, suggestion):
        parts = suggestion.split(':')
        return parts[0].strip()

def main(inout: ModelInOut):
    inout.execute_model(Model())


if __name__ == "__main__":
    execute_model(main)
    exit(0)
