from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model

User = get_user_model()



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.TextField(blank=True, null=True)
    course = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    year_lvl = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='profile_pictures/', validators=[FileExtensionValidator(allowed_extensions=['webp','jpg', 'jpeg', 'png'])], null=True, blank=True)

    def __str__(self):
        return self.user.username
    

class Schedule(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.TextField(blank=True, null=True)
    year_lvl = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    room_name = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course} - {self.date} ({self.start_time} - {self.end_time})"
    
    

class History(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.timestamp}"