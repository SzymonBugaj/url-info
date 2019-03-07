from django.urls import path
from .views import ResultView, UrlView

urlpatterns = [
   path('', UrlView.as_view(), name='base'),
   path('results/', ResultView.as_view(), name='result'),
]