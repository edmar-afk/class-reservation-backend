from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import date
from django.utils import timezone
from rest_framework.generics import DestroyAPIView, RetrieveAPIView
from django.utils.timezone import localdate
import requests # pyright: ignore[reportMissingModuleSource]
import threading
from .serializers import StudentRegisterSerializer, StudentSerializer, UserSerializer, TeacherCreateSerializer, ScheduleSerializer
from .models import Student, Schedule


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        return Response({
            "access": serializer.validated_data["access"],
            "refresh": serializer.validated_data["refresh"],
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        })


class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("===== STUDENT REGISTER REQUEST =====")
        print("RAW DATA:", request.data)

        serializer = StudentRegisterSerializer(data=request.data)

        if serializer.is_valid():
            print("VALIDATED DATA:", serializer.validated_data)
            serializer.save()

            print("STATUS: SUCCESS - Student created")
            return Response(
                {"message": "Student registered successfully"},
                status=status.HTTP_201_CREATED
            )

        print("STATUS: FAILED VALIDATION")
        print("ERRORS:", serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        student = Student.objects.filter(user=user).first()

        return Response({
            "user": UserSerializer(user).data,
            "student": StudentSerializer(student).data if student else None,
        })

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        student = Student.objects.filter(user=user).first()

        if not student:
            return Response(
                {"detail": "Student profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update full name
        if "full_name" in request.data:
            student.full_name = request.data.get("full_name")

        # Update profile picture
        if "profile_picture" in request.FILES:
            student.profile_picture = request.FILES["profile_picture"]

        student.save()

        return Response({
            "user": UserSerializer(user).data,
            "student": StudentSerializer(student).data,
        }, status=status.HTTP_200_OK)
        
        
class StudentByUserIDView(APIView):
    def get(self, request, user_id):
        try:
            student = Student.objects.select_related("user").get(user_id=user_id)
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        


class UsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        students = Student.objects.select_related("user").all()

        serializer = StudentSerializer(
            students,
            many=True,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
class UserDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.select_related("user").all()
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        # Delete the related Django User.
        # Because Student.user uses on_delete=models.CASCADE,
        # the Student will also be deleted automatically.
        instance.user.delete()

        
        
class TeacherCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TeacherCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():
            teacher = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Teacher created successfully.",
                    "teacher": {
                        "id": teacher.id,
                        "full_name": teacher.full_name,
                        "phone_number": teacher.phone_number,
                        "profile_picture": (
                            teacher.profile_picture.url
                            if teacher.profile_picture
                            else None
                        ),
                        "is_staff": teacher.user.is_staff,
                        "is_superuser": teacher.user.is_superuser,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
class ScheduleListCreateView(generics.ListCreateAPIView):
    queryset = Schedule.objects.select_related("instructor").all().order_by(
        "date",
        "start_time"
    )
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]


class ScheduleUpdateView(generics.UpdateAPIView):
    queryset = Schedule.objects.select_related("instructor").all()
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]

    lookup_field = "pk"
    
    
class ScheduleDeleteView(generics.DestroyAPIView):
    queryset = Schedule.objects.all()
    permission_classes = [AllowAny]
    lookup_field = "pk"