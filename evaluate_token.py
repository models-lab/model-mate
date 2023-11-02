import logging
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Evaluacion a nivel de token')
    parser.add_argument('--answers', '-a', required=True, help="Respuestas correctas en txt")
    parser.add_argument('--predictions', '-p', required=True,
                        help="Predicciones en txt")
    args = parser.parse_args()

    # Cargo las predicciones y las ground-truth
    preds = open(args.predictions, "r").readlines()
    gts = open(args.answers, "r").readlines()

    # Comprobacion para ver que tienen el mismo numero de lineas.
    assert len(preds) == len(gts), f"No hay el mismo número de lineas en las predicciones y en las respuestas correctas: {len(preds)} vs {len(gts)}"
    # Calculo el accuracy. No se tienen en cuenta los tokens <s>, </s> ni <EOL>.
    total = 0
    correct = 0.0
    for pred, gt in zip(preds, gts):
        pred = pred.split()
        gt = gt.split()
        assert len(pred) == len(gt), f"Sequence length of prediction and answer are not equal, {len(pred)}: {len(gt)}"
        for x, y in zip(pred, gt):
            if y not in ["<s>", "</s>", "<EOL>"]:
                total += 1
                if x == y:
                    correct += 1

    logger.info(f"Total: {total} tokens, accuracy: {round(correct / total * 100, 2)}")


if __name__ == "__main__":
    main()
