import json

test_path = "./test200.txt"

keywords = ["class", "attr", "ref", "extends", "package"]
endline_words = ["}", ";", "</s>"]

with open(test_path, "r") as file, open("modelset_line/test.json", "w") as test:
    for line in file:
        tokens = line.split()

        for i, token in enumerate(tokens):
            if token in keywords:
                line_dict = {}
                inp = " ".join(tokens[:i+1])
                # quiero un 15% de contexto al menos
                # sin contar los 13 tokens fijos a todos los modelos
                if len(inp)-13 >= 0.15*(len(tokens) - 13):
                    line_dict['input'] = inp
                else:
                    continue

                gt = []
                j = i+1
                while(tokens[j] not in endline_words):
                    gt.append(tokens[j])
                    j += 1
                gt.append(tokens[j])
                line_dict['gt'] = " ".join(gt)
                #print(line_dict)
                test.write(json.dumps(line_dict) + '\n')