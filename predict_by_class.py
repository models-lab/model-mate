import logging
import json
import os
import torch

from transformers import GPT2LMHeadModel
from transformers import pipeline

# Path del modelo pre-entrenado.
model_path = "./runs/gpt2-modelset_token-256/best_model"

# Carga del modelo pre-entrenado.
model = GPT2LMHeadModel.from_pretrained(model_path)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Usamos la GPU si esta disponible.
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# Creamos un pipeline con el tipo de tarea que vamos a resolver
# y el path al modelo cargado.
# max_new_tokens = 20, se presupone que no hay mas de 20 tokens hasta el fin de linea
# handle_long_generation = "hole" para que no haya problemas con lineas mayores de 1024 tokens, truncado automatico
generator = pipeline("text-generation", model=model_path, max_new_tokens=8, handle_long_generation="hole", device=0)

directory_path = "tests_by_class"
num_ret_seq = 5
# Contador para saber por que frase vamos.
cnt = 0


for filename in os.listdir(directory_path):
        cnt = 0
        with open(os.path.join(directory_path, filename), 'r') as file, open('preds_by_class/' + os.path.splitext(filename)[0] + 'Pred.txt', 'w') as out_file:
            cnt += 1
            lines = file.readlines()
            input = [json.loads(line)["input"] for line in lines]
            print("Empiezan predicciones:" + str(cnt))
            # Predecimos.
            predictions = generator(input, num_return_sequences=num_ret_seq)
            print("end preds")
            for i, prediction in enumerate(predictions):
                inputTokens = input[i].split()
                for j in range(num_ret_seq):
                    pred = []
                    predTokens = prediction[j]['generated_text'].strip().split()
                    if len(predTokens) > len(inputTokens):
                        pred.append(predTokens[len(inputTokens)])
                    else:
                        pred.append('NO_PRED')
                    finalPred = " ".join(pred)
                    out_file.write(finalPred + ' ')
                out_file.write('\n')
            print("terminado file: " + str(cnt))
