from torch import load, tensor
import torch
from PIL import Image
import PIL.ImageDraw as ImageDraw
import os
import numpy as np
import base64
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join("./net.prm")


class Service:
    # 学習済みモデルの読み込み
    model = fasterrcnn_resnet50_fpn(weights = "COCO_V1", weights_backbone='DEFAULT')
    model.roi_heads.box_predictor = FastRCNNPredictor(model.roi_heads.box_predictor.cls_score.in_features, 3)
    model_weight = torch.load(MODEL_FILE)
    model.load_state_dict(model_weight)
    model.cpu()
    model.eval()

    @staticmethod
    def predict(data):
        # fasterRCNNを使って信号機の予測を行い，画像を返す
        label_predict = ["background", "GREEN", "RED"]
        img_binary = base64.b64decode(data["img"][22:])
        with open("temp.png", 'bw') as f:
            f.write(img_binary)
        image = Image.open("temp.png").convert("RGB")
        trans = [
            transforms.ToTensor(),
            transforms.Normalize(0.5, 0.5)
        ]
        trans = transforms.Compose(trans)
        img = trans(image)
        img = img.to("cpu")
        print(img)
        print(img.shape)
        outputs = Service.model([img])
        outputs = [{k: v.to('cpu').detach().numpy() for k, v in t.items()} for t in outputs]
        outputs = outputs[0]
        print(outputs)

        draw = ImageDraw.Draw(image)
        labels = ""
        for i in range(len(outputs["labels"])):
            if outputs["scores"][i] > 0.5:
                l = outputs["labels"][i]
                color = "red" if l == 2 else "blue"
                box = outputs["boxes"][i]
                l = label_predict[int(l)]
                labels += labels + l + " "
                draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline=color, width=3)
        image.save("output.png")

        with open("output.png", "rb") as f:
            img_binary = f.read()
        result = base64.b64encode(img_binary).decode("utf-8")

        return {"result": result, "label": labels}

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
