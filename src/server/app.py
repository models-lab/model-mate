from flask import Flask, request, jsonify

from inference import TokenInference

import time

class FlaskModelMateApp:
    def __init__(self, token_model: TokenInference, app: Flask = None):
        if app is None:
            app = Flask(__name__)
            # Load configuration from environment variables
            app.config.from_prefixed_env()

        self.app = app
        self.token_model = token_model

        @app.post("/recommend/fragment")
        def recommend_token():
            data = request.get_json()
            text = data['context'].strip()
            # type_ = data.get('type', 'token')

            start = time.time()
            fragment = self.token_model.generate_fragment(text)
            end = time.time()

            print(f"Time: {end - start}")
            print(fragment)

            text = " ".join(fragment)
            return jsonify({"fragment": fragment, "time": end - start, "text": text})

    def run(self):
        self.app.run(host='0.0.0.0', port=8080)
