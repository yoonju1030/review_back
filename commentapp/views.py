from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from animeapp.models import Anime


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_comment(request):
    try:
        anime_id = request.data.get('animeId')
        user_id = request.data.get("userId")
        content = request.data.get('content')
        Comment.objects.create(
            user_id=user_id,
            content=content,
            anime=anime_id
        )
        response = Response({"result": status.HTTP_200_OK})
        return response
    except Exception as e:
        return Response({'message': "create comment fail", 'result': False, 'error': str(e)})
    
@api_view(["POST"])
def get_all_comment_by_anime(request):
    try:
        anime_id = request.data.get('animeId')
        comments = Comment.objects.filter(anime=anime_id).order_by('-created_at')
        result = [{"content": c.content, "id": c.user_id, "time": c.created_at} for c in comments]
        return Response({'message': "Success to get comments", 'result': result})
    except Exception as e:
        return Response({'message': "Fail to get comment", 'result': False, 'error': str(e)})
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_comment_by_users(request):
    try:
        user_id = request.data.get('userId')
        comments = Comment.objects.filter(user_id=user_id).order_by('-created_at')
        anime_ids = list(set([c.anime for c in comments]))
        # anime 필드가 CharField이므로 문자열로 비교
        anime_dict = {}
        for anime_id in anime_ids:
            try:
                anime = Anime.objects.get(id=int(anime_id))
                anime_dict[anime_id] = anime.name
            except (Anime.DoesNotExist, ValueError):
                anime_dict[anime_id] = ""
        result = []
        for c in comments:
            result.append({
                "content": c.content,
                "id": c.anime,
                "time": c.created_at,
                "name": anime_dict.get(c.anime, "")
            })
        return Response({'message': "Success to get comments", 'result': result})
    except Exception as e:
        return Response({'message': "Fail to get comment", 'result': False, 'error': str(e)})