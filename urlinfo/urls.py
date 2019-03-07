from django.urls import path
from . import views
from .views import ResultView, UrlView 

urlpatterns = [
    path('', UrlView.as_view()),
    path('results/', ResultView.as_view()),
]