from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from random import shuffle
from .models import Anime


# Create your views here.
@api_view()
def hello_world(request):
    return Response({"message": "hello world"})

@api_view()
def get_anime(request): 
    try:
        # genres 필드가 JSONField이므로 Python 레벨에서 필터링
        all_anime = Anime.objects.all()
        target_genres = ["스포츠", "드라마"]
        filtered_anime = [
            a for a in all_anime 
            if a.genres and any(genre in a.genres for genre in target_genres)
        ]
        
        anime = []
        for a in filtered_anime:
            obj = {
                "id": str(a.id), 
                "Name": a.name, 
                'Image': a.image or '', 
            }
            anime.append(obj)
        
        for a in range(len(anime)):
            anime[a]["idx"] = a
        shuffle(anime)
        res = Response({"message": anime})
        res["Access-Control-Allow-Origin"]="*"
        return res
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(["POST"])
def get_info(request):
    try:
        id = request.data['id']
        anime = Anime.objects.get(id=id)
        result = {
            "name": anime.name,
            "airYearQuarter": anime.air_year_quarter or "",
            "content": anime.content or "",
            "contentRating": anime.content_rating or "",
            "ended": anime.ended,
            'genres': anime.genres or [],
            "tags": anime.tags or [],
            "image": anime.image or ""
        }
        return Response({"message": result})
    except Anime.DoesNotExist:
        return Response({"error": "Anime not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)