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
from .serializers import StudentRegisterSerializer, StudentSerializer, InstructorSerializer, UserSerializer, RoomSerializer, ReservationSerializer
from .models import Student, Instructor, Subject, Room, Reservation


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
        

class RoomListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    

class StudentSetScheduleView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, user_id, room_id):
        print("=== REQUEST DEBUG ===")
        print("USER_ID:", user_id)
        print("ROOM_ID:", room_id)
        print("REQUEST DATA:", request.data)

        try:
            student = Student.objects.get(user_id=user_id)
        except Student.DoesNotExist:
            print("ERROR: Student not found for user_id:", user_id)
            return Response(
                {"error": "Student profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            print("ERROR: Room not found for room_id:", room_id)
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReservationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(student=student, room=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("=== SERIALIZER INVALID ===")
        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class AllReservationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        reservations = Reservation.objects.select_related("student", "room").all()

        data = []

        for reservation in reservations:
            data.append({
                "id": reservation.id,
                "student": {
                    "id": reservation.student.id,
                    "full_name": reservation.student.full_name,
                    "course": reservation.student.course,
                    "year_lvl": reservation.student.year_lvl,
                    "phone_number": reservation.student.phone_number,
                    "profile_picture": request.build_absolute_uri(
                        reservation.student.profile_picture.url
                    ) if reservation.student.profile_picture else None,
                },
                "room": {
                    "id": reservation.room.id,
                    "name": reservation.room.name,
                },
                "course": reservation.course,
                "year_lvl": reservation.year_lvl,
                "subject": reservation.subject,
                "section": reservation.section,
                "reserve_date": reservation.reserve_date,
                "time_in": reservation.time_in,
                "time_out": reservation.time_out,
            })

        return Response(data, status=status.HTTP_200_OK)
    
    
class ReservationDeleteView(DestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    lookup_field = "id"
    
    
class ReservationFilterView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, course, year_lvl, section):
        reservations = Reservation.objects.filter(
            course=course,
            year_lvl=year_lvl,
            section=section
        ).order_by("-reserve_date", "time_in")

        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)