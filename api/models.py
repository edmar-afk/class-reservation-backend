from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator



class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], null=True, blank=True)

    def __str__(self):
        return self.user.username


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
    
    

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='subjects')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    

class Room(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - ID: {self.id}"
    

class Reservation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    course = models.TextField(blank=True, null=True)
    year_lvl = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    reserve_date = models.DateField(blank=True, null=True)
    time_in = models.DateTimeField()
    time_out = models.DateTimeField()

    def __str__(self):
        return f"{self.student.full_name} reserved {self.room.name} for {self.subject}"