import os.path
import re
import sys
import hydra
from omegaconf import DictConfig

from Recommender.recommender import Recommender

import common

sys.path.append('..')

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    model_folder = os.path.join(common.get_trained_model_folder(cfg), "best_model")
    train_data_folder = os.path.join(cfg.run.train_data_folder, cfg.dataset.name)

    if cfg.evaluation.type == 'tokens':
        evaluation_type = 'token'
        test_path = common.get_test_dataset_by_token(cfg)
    elif cfg.evaluation.type == 'by_category':
        evaluation_type = 'class'
        test_path = common.get_test_dataset_folder_by_class(cfg)
    elif cfg.evaluation.type == 'lines':
        evaluation_type = 'line'
        test_path = common.get_test_dataset_by_lines(cfg)
    else:
        raise ValueError("Invalid evaluation type " + cfg.evaluation.type)

    test_file = os.path.join(train_data_folder, cfg.run.test_file)

    model_name = cfg.model.model_name.split('/')[-1]
    results_folder = f"runs/{cfg.dataset.name}-{cfg.evaluation.type}-{model_name}"
    os.makedirs(results_folder, exist_ok=True)

    recommender = Recommender(
        model=model_folder,
        type=evaluation_type,
        test_path=test_path,
        max_new_tokens=8,
        num_ret_seq=1,
        pred_path=os.path.join(results_folder, "predictions.txt")
    )

    if cfg.evaluation.type == 'tokens':
        recommender.recommend_token()
        recommender.evaluate_token()
    elif cfg.evaluation.type == 'by_category':
        mrr_cut = cfg.evaluation.mrr_cut
        recommender.mrr_by_class(mrr_cut)
    elif cfg.evaluation.type == 'lines':
        recommender.recommend_line()
        recommender.evaluate_line()
    else:
        raise ValueError("Invalid evaluation type " + cfg.evaluation.type)


if __name__ == '__main__':
    main()
