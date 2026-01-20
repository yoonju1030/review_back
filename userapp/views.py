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


@api_view(["POST"])
@permission_classes([AllowAny])
def check_unique_id(request):
    try:
        id = request.data["id"]
        exists = User.objects.filter(id=id).exists()
        return Response({"result": not exists})
    except Exception as e:
        return Response({"result": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def sign_up_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

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
            return Response(
                {"message": "validation failed", "errors": serializer.errors, "result": False},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_type = type(e).__name__
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
        user = authenticate(
            id=request.data.get("id"), password=request.data.get("password")
        )
        if user is not None:
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
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
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
        response = Response(
            {"message": "Logout success"}, status=status.HTTP_202_ACCEPTED
        )
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
    except Exception as e:
        raise e
