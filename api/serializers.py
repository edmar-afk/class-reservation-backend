from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Instructor, Student, Subject, Room, Reservation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "full_name",
            "course",
            "section",
            "year_lvl",
            "phone_number",
            "profile_picture",
        ]

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            "id",
            "profile_picture",
        ]
        
class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Student
        fields = [
            'username',
            'full_name',
            'password',
            'course',
            'section',
            'year_lvl',
            'phone_number',
            'profile_picture'
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        student = Student.objects.create(
            user=user,
            **validated_data
        )

        return student


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']
        
        
class ReservationSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(
        source="student.full_name",
        read_only=True
    )

    room = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "student",
            "student_full_name",
            "room",
            "course",
            "year_lvl",
            "subject",
            "section",
            "reserve_date",
            "time_in",
            "time_out",
        ]
        read_only_fields = ["student", "room"]

    def get_room(self, obj):
        return {
            "id": obj.room.id,
            "name": obj.room.name
        }