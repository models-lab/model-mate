import os
import logging
import json
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    directory_path = 'tests_by_class'
    for filename in os.listdir(directory_path):
        # Cargo las predicciones y las ground-truth
        preds = open('preds_by_class/' + os.path.splitext(filename)[0] + 'Pred.txt', 'r').readlines()
        gts = open('tests_by_class/' + filename, "r").readlines()


        # Comprobacion para ver que tienen el mismo numero de lineas.
        assert len(preds) == len(gts), f"Samples of predictions and answers are not equal, {len(preds)}: {len(gts)}"

        # Calculo el accuracy. No se tienen en cuenta los tokens <s>, </s> ni <EOL>.
        total = 0
        correct = 0.0
        edit_sim = 0.0
        for pred, gt in zip(preds, gts):
            gt = json.loads(gt)["gt"]
            total += 1
            edit_sim += fuzz.ratio(pred.strip(), gt.strip())
            if pred.strip() == gt.strip():
                correct += 1

        logger.info(f"Type: {filename}, Total: {total} tokens, accuracy: {round(correct / total * 100, 2)}, Edit sim: {round(edit_sim/total, 2)}")


if __name__ == "__main__":
    main()
