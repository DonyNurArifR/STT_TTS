from django.urls import path
from . import views

urlpatterns = [
   # path('',views.index),
   path('', views.text_to_speech_view, name='text_to_speech'),
   path('stt/', views.stt_view, name='speech_to_text'),
]