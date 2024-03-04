from django.db import models
from django.utils import timezone

class LearnedData(models.Model):
    dt          = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    file        = models.FileField(verbose_name="学習済みモデル", upload_to="prediction/learned_data/file")

