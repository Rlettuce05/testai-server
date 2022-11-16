from tensorflow.keras.models import load_model
from PIL import Image
import os
import numpy as np
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "JupyterNotebook/saved_model")
MODEL_FILE = os.path.join(MODEL_DIR, "model.h5")


class Service:
    model = load_model(MODEL_FILE)

    @staticmethod
    def predict(data):
        label_predict = {0:"飛行機", 1:"自動車", 2:"鳥", 3:"猫", 4:"鹿", 5:"犬", 6:"カエル", 7:"馬", 8:"船", 9:"トラック"}
        img_binary = base64.b64decode(data["img"][22:])
        with open("temp.png", 'bw') as f:
            f.write(img_binary)
        img = np.array(Image.open("temp.png").convert("RGB"))
        img = img.reshape(1, 32, 32, 3)
        print(img)
        print(img.shape)
        predict_num = Service.model.predict(img)
        predict_num = np.argmax(predict_num[0])
        label = label_predict[predict_num]
        print(label)
        return label

class Resource:
    @staticmethod
    async def on_post(req, resp):
        data = await req.media()
        res = Service.predict(data)
        resp.media = {
            "status": True,
            "result": res
        }

class Greeting:
    @staticmethod
    async def on_post(rep, resp, *, name):
        resp.media = { "result" : f"Hello {name}" }
