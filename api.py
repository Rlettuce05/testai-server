import responder
import uvicorn
from src import Resource, Greeting

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
api.add_route('/api/greeting/{name}', Greeting)

if __name__ == '__main__':
    uvicorn.run("api:api",host="0.0.0.0", port=8000, reload=True)
