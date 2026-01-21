from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db import transaction
from random import shuffle
from .models import Anime, Genre
import logging

# 앱별 로거 가져오기
logger = logging.getLogger('animeapp')


# Create your views here.
@api_view()
def hello_world(request):
    return Response({"message": "hello world"})

@api_view()
def get_anime(request): 
    try:
        logger.info("애니메이션 목록 조회 요청")
        # genres는 ManyToManyField이므로 DB 레벨에서 필터링
        target_genres = ["스포츠", "드라마"]
        filtered_anime = (
            Anime.objects.filter(genres__name__in=target_genres)
            .distinct()
        )
        
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
        logger.info(f"애니메이션 목록 조회 성공: {len(anime)}개")
        res = Response({"message": anime})
        res["Access-Control-Allow-Origin"]="*"
        return res
    except Exception as e:
        logger.error(f"애니메이션 목록 조회 실패: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
def get_info(request):
    try:
        id = request.data['id']
        logger.info(f"애니메이션 상세 정보 조회 요청: {id}")
        anime = Anime.objects.get(id=id)
        result = {
            "name": anime.name,
            "airYearQuarter": anime.air_year_quarter or "",
            "content": anime.content or "",
            "contentRating": anime.content_rating or "",
            "ended": anime.ended,
            "genres": list(anime.genres.values_list("name", flat=True)),
            "tags": anime.tags or [],
            "image": anime.image or ""
        }
        logger.info(f"애니메이션 상세 정보 조회 성공: {id}")
        return Response({"message": result})
    except Anime.DoesNotExist:
        logger.warning(f"애니메이션을 찾을 수 없음: {id}")
        return Response({"error": "Anime not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"애니메이션 상세 정보 조회 실패: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def insert_anime(request):
    try:
        anime_data = request.data["data"]
        logger.info(f"애니메이션 등록/수정 요청: {anime_data.get('name', 'unknown')}")
    except Exception as e:
        logger.error(f"애니메이션 등록 요청 파싱 실패: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(anime_data, dict):
        return Response({"error": "data must be an object"}, status=status.HTTP_400_BAD_REQUEST)

    # 입력 키가 섞여 들어와도 최대한 흡수 (snake_case / camelCase)
    name = anime_data.get("name") or anime_data.get("Name")
    laftel_id = anime_data.get("laftel_id") or anime_data.get("laftelId")
    image = anime_data.get("image") or anime_data.get("Image")
    air_year_quarter = anime_data.get("air_year_quarter") or anime_data.get("airYearQuarter")
    content = anime_data.get("content")
    content_rating = anime_data.get("content_rating") or anime_data.get("contentRating")
    ended = anime_data.get("ended", False)
    tags = anime_data.get("tags") or []
    genres_payload = anime_data.get("genres") or []

    if not name:
        return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

    # laftel_id는 "10000 단위 int"라 했으니 가능한 범위 체크만 가볍게
    if laftel_id is not None:
        try:
            laftel_id = int(laftel_id)
        except (TypeError, ValueError):
            return Response({"error": "laftel_id must be int"}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(tags, list):
        return Response({"error": "tags must be a list"}, status=status.HTTP_400_BAD_REQUEST)

    # genres: ["드라마", ...] 또는 [{"name":"드라마"}, ...] 허용
    genre_names: list[str] = []
    if isinstance(genres_payload, list):
        for g in genres_payload:
            if isinstance(g, str) and g.strip():
                genre_names.append(g.strip())
            elif isinstance(g, dict):
                g_name = (g.get("name") or g.get("Name") or "").strip()
                if g_name:
                    genre_names.append(g_name)
    else:
        return Response({"error": "genres must be a list"}, status=status.HTTP_400_BAD_REQUEST)

    defaults = {
        "name": name,
        "laftel_id": laftel_id,
        "image": image,
        "air_year_quarter": air_year_quarter,
        "content": content,
        "content_rating": content_rating,
        "ended": bool(ended),
        "tags": tags,
    }

    with transaction.atomic():
        obj, created = Anime.objects.update_or_create(name=name, defaults=defaults)
        action = "생성" if created else "수정"
        logger.info(f"애니메이션 {action}: {name} (ID: {obj.id})")

        if genre_names:
            # 이미 DB에 있는 Genre는 새로 생성하지 않고 기존 것을 사용
            genres_to_add = []
            for gn in set(genre_names):
                genre_obj, genre_created = Genre.objects.get_or_create(name=gn)
                genres_to_add.append(genre_obj)
                if genre_created:
                    logger.info(f"새 장르 생성: {gn}")
            
            # 기존 연결은 유지하고, 새로운 genre만 추가
            # 이미 연결된 genre는 중복 추가되지 않음
            obj.genres.add(*genres_to_add)
            logger.info(f"애니메이션에 장르 연결 완료: {name} - {genre_names}")
        else:
            obj.genres.clear()
            logger.info(f"애니메이션 장르 초기화: {name}")

    return Response(
        {
            "message": "created" if created else "updated",
            "anime": {
                "id": obj.id,
                "name": obj.name,
                "laftel_id": obj.laftel_id,
                "genres": list(obj.genres.values_list("name", flat=True)),
            },
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )