from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Schedule


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
        ]
        read_only_fields = ["id"]


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

    def update(self, instance, validated_data):
        # Get nested User information
        user_data = validated_data.pop("user", None)

        # Update linked Django User
        if user_data is not None:
            user = instance.user

            for field, value in user_data.items():
                setattr(user, field, value)

            user.save()

        # Update Student information
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance

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




class TeacherCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )
    confirm_password = serializers.CharField(
        write_only=True
    )
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True
    )

    def validate_phone_number(self, value):
        value = value.strip()

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        full_name = validated_data["full_name"]
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]
        profile_picture = validated_data.get("profile_picture")

        user = User.objects.create_user(
            username=phone_number,
            password=password,
            first_name=full_name,
            is_staff=True,       # Teacher
            is_superuser=False,  # NOT an admin
        )

        teacher = Student.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number,
            course=None,
            section=None,
            year_lvl=None,
            profile_picture=profile_picture,
        )

        return teacher
    
    


class ScheduleSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = [
            "id",
            "instructor",
            "instructor_name",
            "course",
            "year_lvl",
            "section",
            "room_name",
            "date",
            "start_time",
            "end_time",
        ]
        read_only_fields = ["id", "instructor_name"]

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.username