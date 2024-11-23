import responder
import os
from src import Resource

api = responder.API(
    cors=True,
    allowed_hosts=["*"],
    cors_params={
        "allow_origins": "*",
        "allow_methods": "POST, GET, OPTIONS",
        "allow_headers": "*"
    }
)

api.add_route('/api/predict', Resource)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5042))
    api.run(address="0.0.0.0", port=port)
