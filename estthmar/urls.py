from django.contrib import admin
from django.urls import path

from estthmar import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ai/', views.AIView.as_view(), name='ai'),
    path('ask_pdf/', views.AskPDFView.as_view(), name='ask_pdf'),
    path('pdf/', views.PDFView.as_view(), name='pdf'),
]
