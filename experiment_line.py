import torch
import logging
import os
import json

from transformers import GPT2LMHeadModel
from transformers import pipeline

# Path del modelo pre-entrenado.
model_path = "./runs/gpt2-modelset_line-256/best_model"

# Carga del modelo pre-entrenado.
model = GPT2LMHeadModel.from_pretrained(model_path)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Usamos la GPU si esta disponible.
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Creamos un pipeline con el tipo de tarea que vamos a resolver
# y el path al modelo cargado.
generator = pipeline("text-generation", model=model_path, max_new_tokens=20, handle_long_generation="hole")

# Fichero donde guardamos las predicciones.
output_file = "predictionsLine.txt"

# Fichero con el conjunto de test.
test_path = "./modelset_line/test.json"

# Fichero reducido
#file_path = "./test200.txt"
#file_path = "alone.txt"


# Contador para saber por que frase vamos.
cnt = 0

end = [';', '}']

# Abrimos el conjunto de test y el fichero para las predicciones.
# longitudes: [678, 1477]
with open(test_path, "r") as file, open(output_file, "w") as out_file:
    for line in file:
        cnt += 1
        input = json.loads(line)["input"]

        print("Empiezan predicciones:" + str(cnt))

        try:
            prediction = generator(input)[0]['generated_text'].strip()
            pred = []
            inputTokens = input.split()
            for i,token in enumerate(prediction.split()):
                if i < len(inputTokens):
                    continue
                if token not in end:
                    pred.append(token)
                else:
                    pred.append(token)
                    break

# borrar
            finalPred = " ".join(pred)
            print(input)
            print(finalPred)
        except IndexError:
            print("Error encontrado en la frase ", cnt)
            break

        out_file.write(finalPred + '\n')
        print("terminada frase: " + str(cnt))
