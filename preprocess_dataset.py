import argparse
import os.path
import re

from sklearn.model_selection import train_test_split

FULL_DATASET_NAME = 'modelset_full.txt'
TRAIN_TXT = 'train.txt'
TEST_TXT = 'test.txt'
VAL_TXT = 'dev.txt'
SPECIAL_TOKEN = "<STR_URI_PREFIX>"


def main(args):
    with open(os.path.join(args.dataset, FULL_DATASET_NAME)) as f:
        contents = f.readlines()
    new_contents = []
    for metamodel in contents:
        new_metamodel = re.sub('"([^"]*)"', SPECIAL_TOKEN, metamodel)
        new_contents.append(new_metamodel)

    # Splitting dataset 70/20/10
    train_val, test = train_test_split(new_contents, test_size=0.20, random_state=args.seed)
    train, val = train_test_split(train_val, test_size=0.1 / 0.8, random_state=args.seed)

    for filename, filecontent in zip([os.path.join(args.dataset, TRAIN_TXT),
                                      os.path.join(args.dataset, VAL_TXT),
                                      os.path.join(args.dataset, TEST_TXT)],
                                     [train, val, test]):
        with open(filename, "a") as f:
            f.writelines(filecontent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="./dataset",
                        help="dataset path")
    parser.add_argument("--seed", default=123,
                        help="seed")
    args = parser.parse_args()
    main(args)
