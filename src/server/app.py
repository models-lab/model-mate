from flask import Flask, request, jsonify

from inference import ModelInference

import time


class FlaskModelMateApp:
    def __init__(self, model: ModelInference, app: Flask = None):
        if app is None:
            app = Flask(__name__)
            # Load configuration from environment variables
            app.config.from_prefixed_env()

        self.app = app
        self.model = model

        @app.post("/recommend/fragment")
        def recommend_fragment():
            data = request.get_json()
            text = data['context'].strip()
            # type_ = data.get('type', 'token')

            cfg = {
                "num_beams": 4,
                "max_new_tokens": 128,
                "context_length": 512
            }

            start = time.time()
            fragments = self.model.get_suggestions_next_block(text, **cfg)
            end = time.time()

            print(f"Time: {end - start}")
            print("Fragments:" , fragments)

            text = fragments[0]
            fragment = text.split(' ')
            return jsonify({"fragment": fragment, "time": end - start, "text": text})

        @app.post("/recommend/token")
        def recommend_token():
            data = request.get_json()
            text = data['context'].strip()
            # type_ = data.get('type', 'token')

            cfg = {
                "num_beams": 7,
                "max_new_tokens": 8,
                "context_length": 512
            }

            start = time.time()
            suggestions = self.model.get_suggestions_next_token(text, **cfg)
            end = time.time()

            print(f"Time: {end - start}")
            print(suggestions)

            return jsonify({"suggestions": suggestions, "time": end - start, "text": text})

        @app.post("/recommend/line")
        def recommend_line():
            data = request.get_json()
            text = data['context'].strip()
            # type_ = data.get('type', 'token')

            cfg = {
                "num_beams": 4,
                "max_new_tokens": 32,
                "context_length": 512
            }

            start = time.time()
            suggestions = self.model.get_suggestions_next_line(text, **cfg)
            end = time.time()

            print(f"Time: {end - start}")
            print(suggestions)

            return jsonify({"suggestions": suggestions, "time": end - start, "text": text})

    def run(self):
        self.app.run(host='0.0.0.0', port=8080)
