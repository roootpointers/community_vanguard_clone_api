from rest_framework.routers import SimpleRouter
from accounts.api.views.media_storage import Base64MediaUploadViewSet
from .views.user import UserViewSet
from .views.verification import VerificationViewSet
from .views.profile import UserProfileViewSet
from .views.role import UserRoleViewSet
from .views.register import UserRegisterViewSet
from .views.existence import ExistenceCheckView
from .views.login import UserLoginViewSet
from .views.admin_login import AdminLoginViewSet
from .views.change_password import ChangePasswordViewSet
from .views.update_password import UpdatePasswordViewSet
from .views.interest import InterestListCreateAPIView, InterestDetailAPIView
from .views.preferred_contribution_path import PreferredContributionPathListCreateAPIView, PreferredContributionPathDetailAPIView
from .views.affiliation import AffiliationListCreateAPIView, AffiliationDetailAPIView
from .views.ban_user import BanUserViewSet
from .views.admin_verification import AdminVerificationDocumentViewSet
from django.urls import path, include

router = SimpleRouter()
router.register("api/user", UserViewSet, basename="user")
router.register("api/verification", VerificationViewSet, basename="verification")
router.register("api/profile", UserProfileViewSet, basename="profile")
router.register("api/role", UserRoleViewSet, basename="role")
router.register("api/media", Base64MediaUploadViewSet, basename="media")
router.register("api/admin-verification-documents", AdminVerificationDocumentViewSet, basename="admin-verification-documents")

urlpatterns = [
    path("", include(router.urls)),

    # Accounts API
    path("api/accounts/email-signup/", UserRegisterViewSet.as_view({"post": "email_signup"}), name="email_signup"),
    path("api/accounts/social-signup/", UserRegisterViewSet.as_view({"post": "social_signup"}), name="social_signup"),

    # Login API
    path("api/accounts/email-login/", UserLoginViewSet.as_view({"post": "email_login"}), name="email_login"),
    path("api/accounts/social-login/", UserLoginViewSet.as_view({"post": "social_login"}), name="social_login"),
    
    # Admin Login API
    path("api/accounts/admin-login/", AdminLoginViewSet.as_view({"post": "admin_login"}), name="admin_login"),

    # Change Password API (Old - without authentication)
    path("api/accounts/change-password/", ChangePasswordViewSet.as_view({"post": "change_password"}), name="change_password"),
    
    # Update Password API (New - for authenticated users)
    path("api/accounts/update-password/", UpdatePasswordViewSet.as_view({"post": "update_password"}), name="update_password"),

    # Existence Check API
    path("api/accounts/check-existence/", ExistenceCheckView.as_view(), name="check_existence"),
    
    # Interests API (CRUD)
    path("api/accounts/interests/", InterestListCreateAPIView.as_view(), name="interests_list_create"),
    path("api/accounts/interests/<uuid:uuid>/", InterestDetailAPIView.as_view(), name="interests_detail"),
    
    # Preferred Contribution Paths API (CRUD)
    path("api/accounts/preferred-contribution-paths/", PreferredContributionPathListCreateAPIView.as_view(), name="preferred_contribution_paths_list_create"),
    path("api/accounts/preferred-contribution-paths/<uuid:uuid>/", PreferredContributionPathDetailAPIView.as_view(), name="preferred_contribution_paths_detail"),
    
    # Affiliations API (CRUD)
    path("api/accounts/affiliations/", AffiliationListCreateAPIView.as_view(), name="affiliations_list_create"),
    path("api/accounts/affiliations/<uuid:uuid>/", AffiliationDetailAPIView.as_view(), name="affiliations_detail"),
    
    # Ban/Unban User API (Admin only)
    path("api/accounts/ban/", BanUserViewSet.as_view({"post": "ban_user"}), name="ban_user"),
    path("api/accounts/unban/", BanUserViewSet.as_view({"post": "unban_user"}), name="unban_user"),
    path("api/accounts/banned-users/", BanUserViewSet.as_view({"get": "list_banned_users"}), name="list_banned_users"),
]
