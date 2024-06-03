from django.urls import path
from .views import (
    UserProfileRegistrationView,
    login_view,
    UserSearchView,
    FriendsListView,
    SendFriendRequestView,
    RespondFriendRequestView,
    PendingFriendRequestsView
)

# Define URL patterns for the application
urlpatterns = [
    # URL pattern for user registration
    path('register/', UserProfileRegistrationView.as_view(), name='user-register'),
    # URL pattern for user login
    path('login/', login_view, name='user-login'),
    # URL pattern for searching users
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    # URL pattern for listing friends
    path('friends/', FriendsListView.as_view(), name='friends-list'),
    # URL pattern for sending friend requests using the recipient's username
    path('friend-requests/send/<str:username>/', SendFriendRequestView.as_view(), name='send-friend-request'),
    # URL pattern for responding to friend requests (accept/reject)
    path('friend-requests/respond/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    # URL pattern for listing pending friend requests
    path('friend-requests/pending/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
]