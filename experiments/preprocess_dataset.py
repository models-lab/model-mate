import os.path
import re

import hydra
from omegaconf import DictConfig
from sklearn.model_selection import train_test_split

SPECIAL_TOKEN = "<URIPRE>"


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    with open(os.path.join(cfg['dataset']['path'], cfg['dataset']['full_dataset'])) as f:
        contents = f.readlines()
    new_contents = []
    for metamodel in contents:
        new_metamodel = re.sub('"([^"]*)"', SPECIAL_TOKEN, metamodel)
        if new_metamodel[0] == ' ':
            new_metamodel = new_metamodel[1:]
        new_contents.append(new_metamodel)

    # Splitting dataset 70/20/10
    train_val, test = train_test_split(new_contents, test_size=0.20, random_state=cfg['run']['seed'])
    train, val = train_test_split(train_val, test_size=0.1 / 0.8, random_state=cfg['run']['seed'])

    for filename, filecontent in zip([os.path.join(cfg['dataset']['path'], cfg['run']['train_file']),
                                      os.path.join(cfg['dataset']['path'], cfg['run']['val_file']),
                                      os.path.join(cfg['dataset']['path'], cfg['run']['test_file'])],
                                     [train, val, test]):
        with open(filename, "a") as f:
            f.writelines(filecontent)


if __name__ == '__main__':
    main()
