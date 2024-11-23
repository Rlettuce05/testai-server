from torch import load
from PIL import Image
import PIL.ImageDraw as ImageDraw
import os
import base64
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms

MODEL_FILE = os.path.join("./net.prm")

class Service:
    # 学習済みモデルの読み込み

    @staticmethod
    def predict(data):
        model = fasterrcnn_resnet50_fpn(weights = "COCO_V1", weights_backbone='DEFAULT')
        model.roi_heads.box_predictor = FastRCNNPredictor(model.roi_heads.box_predictor.cls_score.in_features, 3)
        model.load_state_dict(load(MODEL_FILE))
        model.cpu()
        model.eval()
        # fasterRCNNを使って信号機の予測を行い，画像を返す
        label_predict = ["background", "GREEN", "RED"]
        img_binary = base64.b64decode(data["img"][22:])
        with open("temp.png", 'bw') as f:
            f.write(img_binary)
        del img_binary
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
        outputs = model([img])
        del model
        del img
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
        del draw
        del image

        with open("output.png", "rb") as f:
            img_binary = f.read()
        result = base64.b64encode(img_binary).decode("utf-8")
        del img_binary
        os.remove("temp.png")
        os.remove("output.png")

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
