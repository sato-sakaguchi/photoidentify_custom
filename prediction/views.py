from django.shortcuts import render
from django.views import View
from django.conf import settings

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.applications.vgg16 import decode_predictions


from .models import LearnedData
from .forms import ImageUploadForm

from io import BytesIO
import os
import pandas as pd

class PredictView(View):
    def get(self, request, *args, **kwargs):

        context         = {}
        context["form"] = ImageUploadForm()

        return render(request, "home.html", context)

    def post(self, request, *args, **kwargs):

        context = {}
        form    = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_file    = form.cleaned_data["image"]

            # 画像ファイルの前処理
            img_file    = BytesIO(img_file.read())
            img         = load_img(img_file, target_size=(224, 224))

            img_array   = img_to_array(img)
            img_array   = img_array.reshape((1, 224, 224, 3))
            img_array   = preprocess_input(img_array)

            # 判定用のモデルを読み込みと予測
            # TODO:ここでAIモデルの読み込みをしているため、アップロードしたAIモデルを読み込み、判定させると良い。
            # 最新のAIモデルが含まれるモデルオブジェクトを取り出す。
            learned_data    = LearnedData.objects.order_by("-dt").first()

            if learned_data:
                # /home/akagi/.GitHub/samurai/2024/sakaguchi/lesson16/deeplearning-advanced-kadai/photoidentify_custom/media/prediction/learned_data/file/vgg16_ErcixrI.h5
                model_path  = os.path.join(str(settings.BASE_DIR) + learned_data.file.url)
            else:
                model_path  = os.path.join(settings.BASE_DIR, "prediction", "models", "vgg16.h5")
                print("None")

            print(model_path)

            model       = load_model(model_path)
            result      = model.predict(img_array)

            # 結果をdfにまとめてコンテキストに与える。
            pred_1          = decode_predictions(result)
            categories      = [item[1] for sublist in pred_1 for item in sublist]
            probabilities   = [item[2] for sublist in pred_1 for item in sublist]
            
            df              = pd.DataFrame({"カテゴリ": categories, "確率": probabilities})

            context["prediction"]   = df.values.tolist()
            context["img_data"]     = request.POST.get("img_data")
            context["form"]         = form
        else:
            context["form"]         = ImageUploadForm()


        return render(request, "home.html", context)

predict = PredictView.as_view()


