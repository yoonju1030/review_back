from django.urls import path
from animeapp.views import hello_world, get_anime, get_info, insert_anime

urlpatterns = [
    path("hello_world/", hello_world),
    path("get_anime/", get_anime),
    path("get_info", get_info),
    path("insert_anime", insert_anime)
]