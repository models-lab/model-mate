import os


def get_trained_model_id(cfg):
    context_length = cfg['params']['context_length']
    return f"{cfg['model']['model_name']}-"f"{cfg['dataset']['name']}-"f"{context_length}"


def get_trained_model_folder(cfg):
    return os.path.join(cfg['run']['models_folder'], get_trained_model_id(cfg))


def get_train_data_folder(cfg):
    return os.path.join(cfg.run.train_data_folder, cfg.dataset.name)


def get_test_dataset_by_token(cfg):
    train_data_folder = os.path.join(cfg.run.train_data_folder, cfg.dataset.name)
    test_tokens = os.path.join(train_data_folder, "test.txt")
    return test_tokens


def get_test_dataset_by_lines(cfg):
    train_data_folder = os.path.join(cfg.run.train_data_folder, cfg.dataset.name)
    test_by_lines = os.path.join(train_data_folder, "tests_by_lines")
    return test_by_lines


def get_test_dataset_folder_by_class(cfg):
    train_data_folder = os.path.join(cfg.run.train_data_folder, cfg.dataset.name)
    test_by_class = os.path.join(train_data_folder, "tests_by_class")
    return test_by_class
