from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
# ssd
urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/student/', views.StudentRegisterView.as_view(), name='student-register'),
    
    path("student/<int:user_id>/", views.StudentByUserIDView.as_view()),
    path("profile/<int:user_id>/", views.UserProfileView.as_view()),
    path('rooms/', views.RoomListView.as_view(), name='room-list'),
    
    path("student-reserve/<int:user_id>/<int:room_id>/", views.StudentSetScheduleView.as_view(), name="student-reserve"),
    path("all-reservations/", views.AllReservationView.as_view(), name="all-reservations"),
    path("reservation/delete/<int:id>/", views.ReservationDeleteView.as_view()),
    
    path("reservations/<str:course>/<str:year_lvl>/<str:section>/", views.ReservationFilterView.as_view(), name="reservation-filter"),
]
