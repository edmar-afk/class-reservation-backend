from django.contrib import admin
from .models import Instructor, Student, Subject, Room, Reservation

admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(Reservation)