import json

# Path con el test set (lineas completas).
test_path = "./modelset_token/test.txt"

# Palabras a partir de las cuales cortar los prefijos y predecir a partir de ellas.
keywords = ["class", "attr", "ref", "extends", "package", "val"]

with open(test_path, "r") as file, \
     open("tests_by_class/testClass.json", "w") as testClass, \
     open("tests_by_class/testAttr.json", "w") as testAttr, \
     open("tests_by_class/testRef.json", "w") as testRef, \
     open("tests_by_class/testExtends.json", "w") as testExtends, \
     open("tests_by_class/testPackage.json", "w") as testPackage, \
     open("tests_by_class/testVal.json", "w") as testVal:
    for line in file:
        tokens = line.split()
        # Por cada token del modelo, veo si coincide con una keyword.
        for i, token in enumerate(tokens):
            if token in keywords:
                # Creo un nuevo caso de test.
                line_dict = {}
                inp = " ".join(tokens[:i + 1])
                # Quiero un 15% de contexto al menos,
                # sin contar los 13 tokens fijos a todos los modelos.
                if i - 13 >= 0.15 * (len(tokens) - 13):
                    line_dict['input'] = inp
                else:
                    continue

                gt = []
                j = i + 1
                gt.append(tokens[j])
                line_dict['gt'] = " ".join(gt)

                if token == "class":
                    testClass.write(json.dumps(line_dict) + '\n')
                elif token == "extends":
                    testExtends.write(json.dumps(line_dict) + '\n')
                elif token == "package":
                    testPackage.write(json.dumps(line_dict) + '\n')
                elif token == "attr":
                    testAttr.write(json.dumps(line_dict) + '\n')
                elif token == "ref":
                    testRef.write(json.dumps(line_dict) + '\n')
                elif token == "val":
                    testVal.write(json.dumps(line_dict) + '\n')

                if( len(tokens ) < j+3):
                    continue

                if tokens[j+1] == "[" and tokens[j+3] == "]":
                    line_dict['input'] =  " ".join(tokens[:j + 4])
                    line_dict['gt'] = tokens[j+4]
                    # Escribo el caso de test.
                    if token == "attr":
                        testAttr.write(json.dumps(line_dict) + '\n')
                    elif token == "ref":
                        testRef.write(json.dumps(line_dict) + '\n')
                    elif token == "val":
                        testVal.write(json.dumps(line_dict) + '\n')