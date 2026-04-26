from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import InstructorProxy
from .models import Instructor, Student, Subject, Room, Reservation

User = get_user_model()

admin.site.unregister(User)

@admin.register(InstructorProxy)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("username", "last_login", 'date_joined')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=True)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "is_staff",
        "action_column",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False).exclude(username="admin")

    # Rename column headers
    def get_list_display(self, request):
        return (
            "username",
            "approved_status",
            "action_column",
        )

    # Custom display for is_staff with label "Approved"
    def approved_status(self, obj):
        return obj.is_staff

    approved_status.boolean = True
    approved_status.short_description = "Approved"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:user_id>/toggle-approval/",
                self.admin_site.admin_view(self.toggle_approval),
                name="user-toggle-approval",
            ),
        ]
        return custom_urls + urls

    def toggle_approval(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.is_staff = not user.is_staff
        user.save()
        return redirect(request.META.get("HTTP_REFERER", "/admin/"))

    def action_column(self, obj):
        toggle_url = reverse("admin:user-toggle-approval", args=[obj.pk])
        delete_url = reverse("admin:auth_user_delete", args=[obj.pk])

        if obj.is_staff:
            toggle_label = "Reject"
            toggle_color = "#d9534f"
        else:
            toggle_label = "Approve"
            toggle_color = "#28a745"

        return format_html(
            """
            <a class="button" style="background:{}; color:white; padding:5px 10px; border-radius:4px; margin-right:5px;"
               href="{}">{}</a>
            <a class="button" style="background:#6c757d; color:white; padding:5px 10px; border-radius:4px;"
               href="{}">Delete</a>
            """,
            toggle_color,
            toggle_url,
            toggle_label,
            delete_url,
        )

    action_column.short_description = "Action"