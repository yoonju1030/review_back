from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from .serialize import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
import logging

# 앱별 로거 가져오기
logger = logging.getLogger('userapp')


@api_view(["POST"])
@permission_classes([AllowAny])
def check_unique_id(request):
    try:
        id = request.data["id"]
        logger.info(f"ID 중복 확인 요청: {id}")
        exists = User.objects.filter(id=id).exists()
        result = not exists
        logger.info(f"ID 중복 확인 결과: {id} - 사용 가능: {result}")
        return Response({"result": result})
    except Exception as e:
        logger.error(f"ID 중복 확인 실패: {str(e)}", exc_info=True)
        return Response({"result": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def sign_up_user(request):
    try:
        user_id = request.data.get("id", "unknown")
        logger.info(f"회원가입 요청: {user_id}")
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"회원가입 성공: {user.id}")

            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            logger.warning(f"회원가입 검증 실패: {user_id} - {serializer.errors}")
            return Response(
                {"message": "validation failed", "errors": serializer.errors, "result": False},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_type = type(e).__name__
        logger.error(f"회원가입 실패: {error_type} - {error_detail}", exc_info=True)
        return Response(
            {
                "message": "sign up fail",
                "error_type": error_type,
                "error_detail": error_detail,
                "result": False
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def log_in_user(request):
    try:
        user_id = request.data.get("id", "unknown")
        logger.info(f"로그인 시도: {user_id}")
        
        user = authenticate(
            id=request.data.get("id"), password=request.data.get("password")
        )
        if user is not None:
            logger.info(f"로그인 성공: {user.id}")
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            logger.warning(f"로그인 실패: {user_id} - 인증 실패")
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}", exc_info=True)
        raise e


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test(request):
    try:
        return Response({"message": "success"})
    except Exception as e:
        raise e


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_out_user(request):
    try:
        user_id = request.user.id if hasattr(request.user, 'id') else "unknown"
        logger.info(f"로그아웃 요청: {user_id}")
        
        response = Response(
            {"message": "Logout success"}, status=status.HTTP_202_ACCEPTED
        )
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        logger.info(f"로그아웃 성공: {user_id}")
        return response
    except Exception as e:
        logger.error(f"로그아웃 오류: {str(e)}", exc_info=True)
        raise e
