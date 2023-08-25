from unicodedata import name
from django.urls import path, include
from . import views

app_name = 'YT-downloader'

urlpatterns = [
	path('', views.ytd, name="ytd"),
	path('download/', views.download_page, name="download"),
	path('download/<res>/', views.success, name="success"),
    path('mp3_page/', views.mp3_page, name="mp3_page"),
	path('mp3_page/<res>/', views.mp3_success, name="mp3_success"),
	path('about/', views.about, name="about"),
	path('music/', views.music, name="music"),
	# path('download-music/', views.download_music, name="download-music"),
	path('download-playlist/', views.playlist, name="download-playlist"),
	path('contact/', views.contact, name='contact'),
]