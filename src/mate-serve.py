from argparse import ArgumentParser

from inference import TokenInference
from server.app import FlaskModelMateApp

if __name__ == '__main__':
    # TODO: We may have several models served via a configuration file
    parser = ArgumentParser(description='Server to expose recommender')
    parser.add_argument('--model', required=True,
                        help='Path to the model')
    parser.add_argument('--device', required=False, default='cuda',
                        help='Device used to run the model')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Show debugging information')

    args = parser.parse_args()

    token_inference = TokenInference(args.model, args.device)
    app = FlaskModelMateApp(token_inference)
    app.run()
