import json

# Path con el test set (lineas completas).
test_path = "./modelset_line/test.txt"

# Palabras a partir de las cuales cortar los prefijos y predecir a partir de ellas.
keywords = ["class", "attr", "ref", "extends", "package", "val"]
# Tokens que definen el fin de una linea.
endline_words = ['<EOL>']

with open(test_path, "r") as file, open("modelset_line/test.json", "w") as test:
    for line in file:
        tokens = line.split()
        # Por cada token del modelo, veo si coincide con una keyword.
        for i, token in enumerate(tokens):
            if token in keywords:
                # Creo un nuevo caso de test.
                line_dict = {}
                inp = " ".join(tokens[:i+1])
                # Quiero un 15% de contexto al menos,
                # sin contar los 13 tokens fijos a todos los modelos.
                if len(inp)-13 >= 0.15*(len(tokens) - 13):
                    line_dict['input'] = inp
                else:
                    continue

                gt = []
                j = i+1
                # Calculo qué se tiene que predecir (hasta encontrar un token de fin de linea)
                while(tokens[j] not in endline_words):
                    gt.append(tokens[j])
                    j += 1
                gt.append(tokens[j])
                line_dict['gt'] = " ".join(gt)
                # Escribo el caso de test.
                test.write(json.dumps(line_dict) + '\n')