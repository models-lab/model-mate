import torch
import logging
import json
import os

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
generator = pipeline("text-generation", model=model_path, max_new_tokens=8, handle_long_generation="hole")

directory_path = "tests_by_class"

# Contador para saber por que frase vamos.
cnt = 0


for filename in os.listdir(directory_path):
        cnt = 0
        with open(os.path.join(directory_path, filename), 'r') as file, open('preds_by_class' + os.path.splitext(filename)[0] + 'Pred.txt', 'w') as out_file:
            for line in file:
                cnt += 1
                # Cargamos el input
                input = json.loads(line)["input"]

                print("Empiezan predicciones:" + str(cnt))
                try:
                    # Predecimos
                    prediction = generator(input)[0]['generated_text'].strip()
                    pred = []
                    inputTokens = input.split()
                    predTokens = prediction.split()
                    pred.append(predTokens[len(inputTokens)])
                    finalPred = " ".join(pred)
                except IndexError:
                    print("Error encontrado en la frase ", cnt)
                    break

                out_file.write(finalPred + '\n')
                print("terminada frase: " + str(cnt))
