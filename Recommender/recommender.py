import torch
import logging
import os
import json
from transformers import pipeline, AutoModelForCausalLM, GPT2LMHeadModel
from tqdm import tqdm
from fuzzywuzzy import fuzz

class Recommender:
    def __init__(self, model, type, test_path, output_file='predictions.txt', max_new_tokens=8, num_ret_seq = 1, mrr=1):
        self.model = model # name of the model that the recommender will use
        self.path = 'runs/' + model # the trained model will always be under the runs folder
        self.type = type # type of predictions
        self.test_path = test_path # where is the test set
        if(len(model.split('/')) <= 2):
            self.pred_dir = self.type + '_' + model.split('/')[0]  # dir where predictions are saved
            self.pred_path = self.type + '_' + model.split('/')[0] + '/' + output_file  # full path of the predictions (if they're in just one file)
        else:
            self.pred_dir = self.type + '_' + model.split('/')[1]  # dir where predictions are saved
            self.pred_path = self.type + '_' + model.split('/')[1] + '/' + output_file  # full path of the predictions (if they're in just one file)
        self.output_file = output_file  # name of the file where predictions are saved
        self.max_new_tokens = max_new_tokens # tokens to predict
        self.num_ret_seq = num_ret_seq # number of different predictions

    def recommend_token(self):
        assert self.type == 'token'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = self.pred_dir
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        if True:
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)

            with open(self.test_path, "r") as file, open(self.pred_path, "w") as out_file:
                for line in tqdm(file, desc="Processing lines", unit=" line"):
                    out_tokens = "<s>"
                    # Creating all possible prefixes (except the whole line)
                    words = line.split()
                    prefixes = [' '.join(words[:i + 1]) for i in range(len(words) - 1)]
                    # We predict one token for each prefix
                    predictions = generator(prefixes)
                    # Sometimes no tokens were predicted. I think this is already solved so it could be removed.
                    for prefix, prediction in zip(prefixes, predictions):
                        pred = prediction[0]['generated_text']
                        pref_size = len(prefix.split())
                        if pref_size == len(pred.split()):
                            out_tokens += ' ' + 'NO_PRED'
                        else:
                            out_tokens += ' ' + pred.split()[pref_size]

                    # Write into prediction file.
                    out_file.write(out_tokens + '\n')
        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def recommend_token2(self, prefix):
        assert self.type == 'token'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)
        generated_tokens = []
        predictions = generator(prefix, num_return_sequences=self.num_ret_seq)
        input_tokens = prefix.split()
        for j in range(self.num_ret_seq):
            pred = []
            pred_tokens = predictions[j]['generated_text'].strip().split()
            if len(pred_tokens) > len(input_tokens):
                pred.append(pred_tokens[len(input_tokens)])
            else:
                pred.append('NO_PRED')
            final_pred = " ".join(pred)
            generated_tokens.append(final_pred)
        return generated_tokens

    def recommend_line(self):
        assert self.type == 'line'
        logger = logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = self.pred_dir
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        # Set of tokens that indicate the end of a line.
        end = ['<EOL>']

        if True:
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)
            with open(self.test_path, "r") as file, open(self.pred_path, "w") as out_file:
                for line in tqdm(file, desc="Processing lines", unit=" line"):
                    input = json.loads(line)["input"]
                    try:
                        prediction = generator(input)[0]['generated_text'].strip()
                        pred = []
                        input_tokens = input.split()
                        for token in prediction.split()[len(input_tokens):]:
                            # We skip the tokens in the input and keep until the first end of line token.
                            if token not in end:
                                pred.append(token)
                            else:
                                pred.append(token)
                                break

                        final_pred = " ".join(pred)
                    except IndexError:
                        print("Error found")
                        break

                    out_file.write(final_pred + '\n')

        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def recommend_line2(self, prefix):
        assert self.type == 'line'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        end = ['<EOL>']
        generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                             handle_long_generation="hole", device=0)
        generated_lines = []
        input_tokens = prefix.split()
        predictions = generator(prefix, num_return_sequences=self.num_ret_seq)
        for j in range(self.num_ret_seq):
            pred = []
            pred_tokens = predictions[j]['generated_text'].strip().split()

            for token in predictions[len(input_tokens):]:
                # We skip the tokens in the input and keep until the first end of line token.
                if token not in end:
                    pred.append(token)
                else:
                    pred.append(token)
                    break

            if len(pred_tokens) > len(input_tokens):
                pred.append(pred_tokens[len(input_tokens)])
            else:
                pred.append('NO_PRED')
            final_pred = " ".join(pred)
            generated_lines.append(final_pred)
        return generated_lines

    def recommend_by_class(self):
        assert self.type == 'class'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = self.pred_dir
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        if True:
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)
            for filename in os.listdir(self.test_path):
                with open(os.path.join(self.test_path, filename), 'r') as file, open(pred_dir + '/' + os.path.splitext(filename)[0] + 'Pred.txt', 'w') as out_file:
                    lines = file.readlines()
                    input = [json.loads(line)["input"] for line in lines]
                    predictions = generator(input, num_return_sequences=self.num_ret_seq)
                    for i, prediction in enumerate(predictions):
                        input_tokens = input[i].split()
                        for j in range(self.num_ret_seq):
                            pred = []
                            pred_tokens = prediction[j]['generated_text'].strip().split()
                            if len(pred_tokens) > len(input_tokens):
                                pred.append(pred_tokens[len(input_tokens)])
                            else:
                                pred.append('NO_PRED')
                            final_pred = " ".join(pred)
                            out_file.write(final_pred + ' ')
                        out_file.write('\n')
        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def evaluate_token(self):
        print(self.model)
        logger = logging.getLogger("transformers")
        logger.setLevel(logging.INFO)
        preds = open(self.pred_path, "r").readlines()
        gts = open(self.test_path, "r").readlines()
        assert len(preds) == len(gts), f"Not the same number of lines in prediction file and in ground truth file: {len(preds)} vs {len(gts)}"
        total = 0
        correct = 0.0
        for pred, gt in zip(preds, gts):
            pred = pred.split()
            gt = gt.split()
            assert len(pred) == len(
                gt), f"Sequence length of prediction and answer are not equal, {len(pred)}: {len(gt)}"
            for x, y in zip(pred, gt):
                if y not in ["<s>", "</s>", "<EOL>"]:
                    total += 1
                    if x == y:
                        correct += 1
        logger.info(f"Total: {total} tokens, accuracy: {round(correct / total * 100, 2)}\n")

    def evaluate_token_by_class(self):
        print(self.model)
        logger = logging.getLogger("transformers")
        logger.setLevel(logging.INFO)
        preds = open(self.pred_path, "r").readlines()
        gts = open(self.test_path, "r").readlines()
        assert len(preds) == len(
            gts), f"Not the same number of lines in prediction file and in ground truth file: {len(preds)} vs {len(gts)}"
        total_attr, total_class, total_extends, total_package, total_ref, total_val = 0, 0, 0, 0, 0, 0
        ok_attr, ok_class, ok_extends, ok_package, ok_ref, ok_val = 0, 0, 0, 0, 0, 0
        for pred, gt in zip(preds, gts):
            pred = pred.split()
            gt = gt.split()
            assert len(pred) == len(
                gt), f"Sequence length of prediction and answer are not equal, {len(pred)}: {len(gt)}"
            count_attr, count_class, count_extends, count_package, count_ref, count_val = 0, 0, 0, 0, 0, 0
            for x, y in zip(pred, gt):
                if count_attr:
                    count_attr = 0
                    total_attr += 1
                    if x == y:
                        ok_attr += 1
                elif count_class:
                    count_class = 0
                    total_class += 1
                    if x == y:
                        ok_class += 1
                elif count_extends:
                    count_extends = 0
                    total_extends += 1
                    if x == y:
                        ok_extends += 1
                elif count_package:
                    count_package = 0
                    total_package += 1
                    if x == y:
                        ok_package += 1
                elif count_ref:
                    count_ref = 0
                    total_ref += 1
                    if x == y:
                        ok_ref += 1
                elif count_val:
                    count_val = 0
                    total_val += 1
                    if x == y:
                        ok_val += 1

                if y == 'attr':
                    count_attr = 1
                elif y == 'class':
                    count_class = 1
                elif y == 'extends':
                    count_extends = 1
                elif y == 'package':
                    count_package = 1
                elif y == 'ref':
                    count_ref = 1
                elif y == 'val':
                    count_val = 1


        logger.info(f"Total Attr: {total_attr} tokens, accuracy: {round(ok_attr / total_attr * 100, 2)}")
        logger.info(f"Total Class: {total_class} tokens, accuracy: {round(ok_class / total_class * 100, 2)}")
        logger.info(f"Total Extends: {total_extends} tokens, accuracy: {round(ok_extends / total_extends * 100, 2)}")
        logger.info(f"Total Package: {total_package} tokens, accuracy: {round(ok_package / total_package * 100, 2)}")
        logger.info(f"Total Ref: {total_ref} tokens, accuracy: {round(ok_ref / total_ref * 100, 2)}")
        logger.info(f"Total Val: {total_val} tokens, accuracy: {round(ok_val / total_val * 100, 2)}\n")

    def evaluate_line(self):
        logger = logging.getLogger("transformers")
        logger.setLevel(logging.INFO)
        # Loading preds and gts
        preds = open(self.pred_path, "r").readlines()
        gts = open(self.test_path, "r").readlines()

        assert len(preds) == len(gts), f"Length of predictions and answers is not equal, {len(preds)}: {len(gts)}"

        # Calculate EM and edit similarity
        total = len(gts)
        em = 0.0
        edit_sim = 0.0
        for pred, gt in zip(preds, gts):
            gt = json.loads(gt)["gt"]
            edit_sim += fuzz.ratio(pred, gt)
            if pred.split() == gt.split():
                em += 1
        print(self.model)
        logger.info(f"Edit sim: {round(edit_sim / total, 2)}, EM: {round(em / total * 100, 2)}\n")



    def mrr_by_class(self, rank = 1):
        print(self.model)
        logger = logging.getLogger("transformers")
        logger.setLevel(logging.INFO)
        for filename in os.listdir(self.test_path):
            preds = open(self.pred_dir + '/' + os.path.splitext(filename)[0] + 'Pred.txt', 'r').readlines()
            gts = open('tests_by_class/' + filename, "r").readlines()

            assert len(preds) == len(gts), f"Samples of predictions and answers are not equal, {len(preds)}: {len(gts)}"

            total = 0
            correct = 0.0
            edit_sim = 0.0
            mrr = 0
            for pred, gt in zip(preds, gts):
                gt = json.loads(gt)["gt"]
                total += 1
                edit_sim += fuzz.ratio(pred.strip(), gt.strip())
                if pred.strip() == gt.strip():
                    correct += 1
                pred_list = pred.strip().split()
                for i in range(rank):
                    if pred_list[i] == gt:
                        mrr += 1 / (i + 1)
                        break

            logger.info(
                f"Type: {filename}, Total: {total} tokens, MRR = {mrr / total}")
        print('\n')