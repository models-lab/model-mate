import torch
import logging
import os
import json
from transformers import pipeline, AutoModelForCausalLM, GPT2LMHeadModel
from tqdm import tqdm

class Recommender:
    def __init__(self, model, type, test_path, output_file='predictions.txt', max_new_tokens=8, num_ret_seq = 1):
        self.model = model # name of the model
        self.path = 'runs/' + model # path of the trained model
        self.type = type # type of predictions
        self.test_path = test_path # where is the test set
        self.pred_dir = self.type + '_' + model.split('/')[0]  # dir where predictions are saved
        self.output_file = output_file  # name of the file where predictions are saved
        self.pred_path = self.pred_dir + '/' + output_file # full path of the predictions (if they're in just one file)
        self.max_new_tokens = max_new_tokens # tokens to predict
        self.num_ret_seq = num_ret_seq # number of different predictions

    def recommendToken(self):
        assert self.type == 'token'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = self.pred_dir
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        if self.model == 'gpt2-modelset_token-256/best_model':
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)

            with open(self.test_path, "r") as file, open(self.pred_path, "w") as out_file:
                for line in tqdm(file, desc="Processing lines", unit=" line"):
                    out_tokens = "<s>"
                    # Creamos todos los prefijos posibles (salvo la linea entera)
                    words = line.split()
                    prefixes = [' '.join(words[:i + 1]) for i in range(len(words) - 1)]
                    # Predecimos un token por cada línea nueva.
                    predictions = generator(prefixes)

                    # A veces se predicen 0 tokens. En ese caso, añado yo el token "NO PRED". ¿Esta esto solucionado?
                    # De ser asi se podria eliminar. NO ESTOY SEGURO aunque parece que ya no veo no_pred.
                    for prefix, prediction in zip(prefixes, predictions):
                        pred = prediction[0]['generated_text']
                        prefSize = len(prefix.split())
                        if prefSize == len(pred.split()):
                            out_tokens += ' ' + 'NO_PRED'
                        else:
                            out_tokens += ' ' + pred.split()[prefSize]

                    # Escribo en el fichero la predicción
                    out_file.write(out_tokens + '\n')
        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"


    def recommendLine(self):
        assert self.type == 'line'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = os.path.basename(self.path)
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        # Tokens de fin de linea.
        end = [';', '}']

        if self.path == './runs/gpt2-modelset_line-256':
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)
            # Abrimos el conjunto de test y el fichero para las predicciones.
            with open(self.test_path, "r") as file, open(self.pred_path, "w") as out_file:
                for line in file:
                    input = json.loads(line)["input"]
                    try:
                        # Predecimos
                        prediction = generator(input)[0]['generated_text'].strip()
                        pred = []
                        inputTokens = input.split()
                        for token in prediction.split()[len(inputTokens):]:
                            # No tenemos en cuenta los tokens del input.
                            # A partir de ahí, corto la predicción en el primer token de fin de línea.
                            if token not in end:
                                pred.append(token)
                            else:
                                pred.append(token)
                                break

                        finalPred = " ".join(pred)
                    except IndexError:
                        print("Error encontrado en la frase ")
                        break

                    out_file.write(finalPred + '\n')

        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def recommendByClass(self):
        assert self.type == 'class'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        pred_dir = self.pred_dir
        if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)

        if self.path == './runs/gpt2-modelset_token-256':
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)
            for filename in os.listdir(self.test_path):
                with open(os.path.join(self.test_path, filename), 'r') as file, open(pred_dir + os.path.splitext(filename)[0] + 'Pred.txt', 'w') as out_file:
                    lines = file.readlines()
                    input = [json.loads(line)["input"] for line in lines]
                    # Predecimos.
                    predictions = generator(input, num_return_sequences=self.num_ret_seq)
                    for i, prediction in enumerate(predictions):
                        inputTokens = input[i].split()
                        for j in range(self.num_ret_seq):
                            pred = []
                            predTokens = prediction[j]['generated_text'].strip().split()
                            if len(predTokens) > len(inputTokens):
                                pred.append(predTokens[len(inputTokens)])
                            else:
                                pred.append('NO_PRED')
                            finalPred = " ".join(pred)
                            out_file.write(finalPred + ' ')
                        out_file.write('\n')
        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def evaluateToken(self):
        preds = open(self.output_file, "r").readlines()
        gts = open(self.test_path, "r").readlines()
        assert len(preds) == len(gts), f"No hay el mismo número de lineas en las predicciones y en las respuestas correctas: {len(preds)} vs {len(gts)}"
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

        logger.info(f"Total: {total} tokens, accuracy: {round(correct / total * 100, 2)}")

    def evaluateLine(self):
        # Cargo las predicciones y las ground-truth
        preds = open(args.predictions, "r").readlines()
        gts = open(args.answers, "r").readlines()

        # Comprobacion para ver que tienen el mismo numero de lineas.
        assert len(preds) == len(gts), f"Samples of predictions and answers are not equal, {len(preds)}: {len(gts)}"

        # Calculo el EM y Edit Similarity.
        total = len(gts)
        EM = 0.0
        edit_sim = 0.0
        for pred, gt in zip(preds, gts):
            gt = json.loads(gt)["gt"]
            edit_sim += fuzz.ratio(pred, gt)
            if pred.split() == gt.split():
                EM += 1

        logger.info(f"Edit sim: {round(edit_sim / total, 2)}, EM: {round(EM / total * 100, 2)}")

    def evaluateByClass(self):
        directory_path = 'tests_by_class'
        for filename in os.listdir(directory_path):
            # Cargo las predicciones y las ground-truth
            preds = open('preds_by_class/' + os.path.splitext(filename)[0] + 'Pred.txt', 'r').readlines()
            gts = open('tests_by_class/' + filename, "r").readlines()

            # Comprobacion para ver que tienen el mismo numero de lineas.
            assert len(preds) == len(gts), f"Samples of predictions and answers are not equal, {len(preds)}: {len(gts)}"

            # Calculo el accuracy. No se tienen en cuenta los tokens <s>, </s> ni <EOL>.
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
                predList = pred.strip().split()
                for i in range(5):
                    if predList[i] == gt:
                        mrr += 1 / (i + 1)
                        break

            logger.info(
                f"Type: {filename}, Total: {total} tokens, accuracy: {round(correct / total * 100, 2)}, Edit sim: {round(edit_sim / total, 2)}")
            logger.info(f"MRR = {mrr / total}")

