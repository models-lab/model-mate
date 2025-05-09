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
        model_path = os.path.join(inout.original, 'model', 'distil-gpt2')

        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        cfg = {
            "params": {
                "context_length": 512
            },
            "evaluation": {
                "max_new_tokens": 100,
                "num_beams": 5,
                "mode": "line",
                "samples_token_id": 5,
                "samples_line": 3,
                "samples_token": 5,
                "samples_block": 5
            }
        }

        max_new_tokens: 256


        all_suggestions = []
        all_data.reset_index()
        for idx, data in tqdm(all_data.iterrows(), desc='Loop over the data'):
            suggestions = []
            try:
                emfatic_input = data['emfatic']

                suggestions = self.do_suggestion(model, tokenizer, emfatic_input, cfg)
                # suggestions = [self.parse_suggestion(s) for s in suggestions]
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in {data['ids']}, owner {data['owner']}, target {data['target']}")
            all_suggestions.append(suggestions)

        return all_suggestions

    def do_suggestion(self, model, tokenizer, emfatic_input, cfg):
        s_attr = emfatic_input + ' attr'
        s_val = emfatic_input + ' val'
        s_ref = emfatic_input + ' ref'

        cfg["output_scores"] = True

        best_suggestions = []
        best_scores = []

        all_suggestions = []
        all_scores = []
        for s in [s_attr, s_val, s_ref]:
            suggestions, scores = get_suggestions_next_line(model, tokenizer, s, cfg)
            print(suggestions)
            all_suggestions.extend(suggestions[1:])
            all_scores.extend(scores[1:])

            best_suggestions.append(suggestions[0])
            best_scores.append(scores[0])

        sorted_suggestions = sorted(zip(all_suggestions, all_scores), key=lambda x: x[1], reverse=True)
        best_suggestions = sorted(zip(best_suggestions, best_scores), key=lambda x: x[1], reverse=True)

        all = best_suggestions + sorted_suggestions[:2]
        all = sorted(all, key=lambda x: x[1], reverse=True)

        results = []
        for s in all:
            r = self.parse_suggestion(s[0])
            if r not in results:
                results.append(r)

        # return [s[0] for s in sorted_suggestions][:5]
        return results[:5]

    def parse_suggestion(self, suggestion):
        parts = suggestion.split(' ')
        if parts[-1] == ';':
            return parts[-2]
        else:
            return parts[-1]

def main(inout: ModelInOut):
    inout.execute_model(Model())


if __name__ == "__main__":
    execute_model(main)
    exit(0)
