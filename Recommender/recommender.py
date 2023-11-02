import torch
import logging
import os
from transformers import pipeline, AutoModelForCausalLM, GPT2LMHeadModel

class Recommender:
    def __init__(self, path, type, max_new_tokens=8, test_path, output_file='predictions.txt'):
        self.path = path
        self.type = type
        self.max_new_tokens = max_new_tokens
        self.test_path = test_path
        self.output_file = output_file

    def recommendToken(self):
        assert self.type = 'token'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        predDir = os.path.basename(self.path)
        if not os.path.exists(predDir):
            os.makedirs(predDir)

        if self.path == './runs/gpt2-modelset_token-256':
            generator = pipeline("text-generation", model=self.path, max_new_tokens=self.max_new_tokens,
                                 handle_long_generation="hole", device=0)

            with open(self.test_path, "r") as file, open(os.path.join(predDir, self.output_file, "w") as out_file:
                for line in file:
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
        assert self.type = 'line'
        logging.getLogger("transformers").setLevel(logging.ERROR)
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        predDir = os.path.basename(self.path)
        if not os.path.exists(predDir):
            os.makedirs(predDir)

        # Tokens de fin de linea.
        end = [';', '}']

        if self.path == './runs/gpt2-modelset_line-256':
            # Abrimos el conjunto de test y el fichero para las predicciones.
            with open(self.test_path, "r") as file, open(os.path.join(predDir, self.output_file, "w") as out_file:
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
                        print("Error encontrado en la frase ", cnt)
                        break

                    out_file.write(finalPred + '\n')

        else:
            print('Model not found')
            return f"Recommendation based on path: {self.path}"

    def recommendByClass(self):

    
    def evaluateToken:

    def evaluateLine:

    def evaluateByClass:

