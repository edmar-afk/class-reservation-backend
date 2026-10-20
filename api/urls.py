from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
# ssd
urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/student/', views.StudentRegisterView.as_view(), name='student-register'),
    
    path("users/", views.UsersView.as_view(), name="users"),
    path("users/<int:pk>/", views.UserDeleteView.as_view(), name="user-delete"),
    path("users/teachers/", views.TeacherCreateView.as_view(), name="teacher-create"),
    path("student/<int:user_id>/", views.StudentByUserIDView.as_view()),
    path("profile/<int:user_id>/", views.UserProfileView.as_view()),
    
    
    path("schedules/", views.ScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("schedules/<int:pk>/", views.ScheduleUpdateView.as_view(), name="schedule-update"),
    path("schedules/<int:pk>/delete/", views.ScheduleDeleteView.as_view(),name="schedule-delete"),
]
