from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from animeapp.models import Anime
from userapp.models import User
import logging

# 앱별 로거 가져오기
logger = logging.getLogger('commentapp')


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_comment(request):
    try:
        anime_id = request.data.get('animeId')
        user_id = request.data.get("userId")
        content = request.data.get('content')
        
        # 필수 필드 검증
        if not anime_id:
            return Response({'message': "animeId is required", 'result': False}, status=status.HTTP_400_BAD_REQUEST)
        if not content:
            return Response({'message': "content is required", 'result': False}, status=status.HTTP_400_BAD_REQUEST)
        
        # User 객체 가져오기 (request.user 사용 또는 userId로 조회)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'message': "User not found", 'result': False}, status=status.HTTP_404_NOT_FOUND)
        else:
            # IsAuthenticated를 사용하고 있으므로 request.user 사용 가능
            user = request.user
        
        # Anime 객체 가져오기
        try:
            anime = Anime.objects.get(id=anime_id)
        except Anime.DoesNotExist:
            return Response({'message': "Anime not found", 'result': False}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'message': "Invalid animeId format", 'result': False}, status=status.HTTP_400_BAD_REQUEST)
        
        # Comment 생성
        comment = Comment.objects.create(
            user=user,
            content=content,
            anime=anime
        )
        
        logger.info(f"댓글 생성 성공: 사용자={user.id}, 애니메이션={anime.id}, 댓글ID={comment.id}")
        
        return Response({
            'message': "Comment created successfully",
            'result': True,
            'comment_id': comment.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'message': "create comment fail", 'result': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def get_all_comment_by_anime(request):
    try:
        anime_id = request.data.get('animeId')
        if not anime_id:
            return Response({'message': "animeId is required", 'result': False}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            anime = Anime.objects.get(id=anime_id)
        except Anime.DoesNotExist:
            return Response({'message': "Anime not found", 'result': False}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'message': "Invalid animeId format", 'result': False}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(anime=anime).order_by('-created_at')
        result = [{
            "content": c.content,
            "id": c.user.id,
            "time": c.created_at
        } for c in comments]
        logger.info(f"애니메이션별 댓글 조회 성공: 애니메이션ID={anime_id}, 댓글 수={len(result)}")
        return Response({'message': "Success to get comments", 'result': result})
    except Exception as e:
        return Response({'message': "Fail to get comment", 'result': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_comment_by_users(request):
    try:
        user_id = request.data.get('userId')
        if not user_id:
            # userId가 없으면 request.user 사용
            user = request.user
        else:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'message': "User not found", 'result': False}, status=status.HTTP_404_NOT_FOUND)
        
        comments = Comment.objects.filter(user=user).order_by('-created_at')
        result = []
        for c in comments:
            result.append({
                "content": c.content,
                "id": c.anime.id,
                "time": c.created_at,
                "name": c.anime.name
            })
        return Response({'message': "Success to get comments", 'result': result})
    except Exception as e:
        return Response({'message': "Fail to get comment", 'result': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)