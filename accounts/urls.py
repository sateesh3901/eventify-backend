from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# All auth-related routes
# Base: /api/auth/

urlpatterns = [
    # ── Authentication ──────────────────────────────
    path('register/',         views.register_view,        name='auth-register'),
    path('login/',            views.login_view,            name='auth-login'),
    path('logout/',           views.logout_view,           name='auth-logout'),

    # ── Current User ────────────────────────────────
    path('me/',               views.current_user_view,     name='auth-me'),
    path('profile/update/',   views.update_profile_view,   name='auth-profile-update'),
    path('password/change/',  views.change_password_view,  name='auth-password-change'),

    # ── JWT Token Refresh ───────────────────────────
    path('token/refresh/',    TokenRefreshView.as_view(),  name='token-refresh'),
]