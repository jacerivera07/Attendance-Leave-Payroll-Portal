from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, AttendanceViewSet, LeaveViewSet, PayrollViewSet
from .views_auth import (
    RegisterView, login_view, logout_view, 
    current_user_view, change_password_view
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leaves', LeaveViewSet, basename='leave')
router.register(r'payroll', PayrollViewSet, basename='payroll')

# The API URLs are determined automatically by the router
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', current_user_view, name='current-user'),
    path('auth/change-password/', change_password_view, name='change-password'),
    
    # API endpoints
    path('', include(router.urls)),
]
