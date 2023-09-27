import os
import logging
import argparse
from fuzzywuzzy import fuzz
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description='Evaluacion a nivel de linea')
    parser.add_argument('--answers', '-a', required=True, help="Respuestas correctas en txt")
    parser.add_argument('--predictions', '-p', required=True,
                        help="Predicciones en txt")
    args = parser.parse_args()

    # Cargo las predicciones y las ground-truth
    preds = open(args.predictions, "r").readlines()
    gts = open(args.answers, "r").readlines()

    # Comprobacion para ver que tienen el mismo numero de lineas.
    assert len(preds) == len(gts), f"Samples of predictions and answers are not equal, {len(preds)}: {len(gts)}"

    # Calculo el EM y Edit Similarity.
    total = len(gts)
    EM = 0.0
    edit_sim = 0.0
    for pred, gt in zip(preds, gts):
        gt = json.loads(gt)["gt"]
        edit_sim += fuzz.ratio(pred, gt)
        if pred.split() == gt.split():
            EM += 1

    logger.info(f"Edit sim: {round(edit_sim/total, 2)}, EM: {round(EM/total*100, 2)}")

if __name__ == "__main__":
    main()
