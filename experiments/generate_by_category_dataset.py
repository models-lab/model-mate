import json
import os
import hydra
import common
from omegaconf import DictConfig

# Path con el test set (lineas completas).
test_path = "./modelset_token/test.txt"

# Palabras a partir de las cuales cortar los prefijos y predecir a partir de ellas.
keywords = ["class", "attr", "ref", "extends", "package", "val"]


def generate_dataset(test_path, test_by_class_folder):
    with open(test_path, "r") as file, \
            open(os.path.join(test_by_class_folder, "testClass.json"), "w") as testClass, \
            open(os.path.join(test_by_class_folder, "testAttr.json"), "w") as testAttr, \
            open(os.path.join(test_by_class_folder, "testRef.json"), "w") as testRef, \
            open(os.path.join(test_by_class_folder, "testExtends.json"), "w") as testExtends, \
            open(os.path.join(test_by_class_folder, "testPackage.json"), "w") as testPackage, \
            open(os.path.join(test_by_class_folder, "testVal.json"), "w") as testVal:
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

                    if (len(tokens) < j + 3):
                        continue

                    if tokens[j + 1] == "[" and tokens[j + 3] == "]":
                        line_dict['input'] = " ".join(tokens[:j + 4])
                        line_dict['gt'] = tokens[j + 4]
                        # Escribo el caso de test.
                        if token == "attr":
                            testAttr.write(json.dumps(line_dict) + '\n')
                        elif token == "ref":
                            testRef.write(json.dumps(line_dict) + '\n')
                        elif token == "val":
                            testVal.write(json.dumps(line_dict) + '\n')


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    if cfg.dataset.level != 'token':
        print("Invalid dataset. Expected token dataset")
        return -1

    train_data_folder = os.path.join(cfg.run.train_data_folder, cfg.dataset.name)

    test_path = os.path.join(train_data_folder, cfg['run']['test_file'])

    test_by_class_folder = common.get_test_dataset_folder_by_class(cfg)

    if not os.path.exists(test_by_class_folder):
        os.mkdir(test_by_class_folder)

    generate_dataset(test_path, test_by_class_folder)


if __name__ == '__main__':
    main()
