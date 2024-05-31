from django.urls import path
from.views import OCRCheckView

urlpatterns = [
    path('OCRCheckView/', OCRCheckView.as_view(), name='OCRCheckView'),
]
