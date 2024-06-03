from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .models import UserProfile, FriendRequest
from .serializers import UserProfileSerializer, FriendRequestCreateSerializer, FriendRequestResponseSerializer, \
    PendingFriendRequestSerializer, FriendListSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from knox.models import AuthToken

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileRegistrationView(generics.CreateAPIView):
    """
    View for registering a new user profile.
    This view handles the creation of a new user profile with username, email, and password.
    It ensures that the user data is valid and securely saves the user with a hashed password.
    """

    queryset = UserProfile.objects.all()  # Define the queryset for the view
    permission_classes = (AllowAny,)  # Allow anyone to access this view (no authentication required)
    serializer_class = UserProfileSerializer  # Define the serializer to be used

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new user profile.
        Validates the incoming data and calls the perform_create method to save the user.
        """
        serializer = self.get_serializer(data=request.data)  # Deserialize the incoming data
        serializer.is_valid(raise_exception=True)  # Validate the data; raise an exception if invalid
        self.perform_create(serializer)  # Save the valid user data
        headers = self.get_success_headers(serializer.data)  # Get any headers to return in the response
        return Response({
            'status': 'success',
            'message': 'User registered successfully.',
        }, status=status.HTTP_201_CREATED, headers=headers)  # Return a success response

    def perform_create(self, serializer):
        """
        Perform the creation of a new user.
        This method sets the user's password securely and saves the user instance.
        """
        user = serializer.save()  # Save the serializer data to create a new user instance
        user.set_password(serializer.validated_data['password'])  # Hash the user's password
        user.save()  # Save the user instance with the hashed password


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Handles user login and returns an authentication token if credentials are valid.

    Request Body:
    - email: User's email address (string)
    - password: User's password (string)

    Response:
    - 200 OK: Returns the authentication token if login is successful.
    - 401 Unauthorized: Returns an error message if login fails due to invalid credentials.
    """
    # Extract email and password from the request data
    email = request.data.get('email')
    password = request.data.get('password')

    # Attempt to retrieve the user by email
    try:
        user = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        # If user does not exist, return an error response
        return Response({'detail': 'Invalid email credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the provided password matches the user's password
    if user.check_password(password):
        # Generate an authentication token using Knox
        _, token = AuthToken.objects.create(user)
        # Return the token in the response
        return Response({
            'token': token,
        }, status=status.HTTP_200_OK)
    else:
        # If the password is incorrect, return an error response
        return Response({'detail': 'Invalid password credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfilePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserSearchView(generics.ListAPIView):
    """
    API view to search for users by email or username.
    If the search query contains an '@' symbol and matches a valid email format,
    it searches by email. Otherwise, it searches by username.

    The view supports pagination and requires the user to be authenticated.
    """

    serializer_class = UserProfileSerializer
    pagination_class = UserProfilePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override the get_queryset method to filter the UserProfile queryset
        based on the search query provided in the request parameters.
        """
        query = self.request.query_params.get('search', '')
        # Check if the query is a valid email format and search by email
        if self.is_valid_email(query):
            return UserProfile.objects.filter(email__iexact=query)
        # Search by username (case-insensitive)
        return UserProfile.objects.filter(Q(username__icontains=query))

    def is_valid_email(self, email):
        """
        Validates if the provided query is a valid email format.
        Args:
            email (str): The email address to validate.
        Returns:
            bool: True if the email is valid, False otherwise.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False



class SendFriendRequestView(generics.CreateAPIView):
    """
    View to send a friend request to another user.
    Only authenticated users can send friend requests.
    """
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Perform the actual creation of the friend request.

        Args:
            serializer: The serializer instance containing validated data.

        Returns:
            Response: A DRF Response object with the result of the operation.
        """
        from_user = self.request.user
        to_username = self.kwargs.get('username')

        # Attempt to retrieve the user to whom the friend request is being sent
        try:
            to_user = UserProfile.objects.get(username=to_username)
        except UserProfile.DoesNotExist:
            # Return a 404 response if the user does not exist
            return Response({'detail': 'User with this username does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Rate limiting: Check if the user has sent more than 3 friend requests in the last minute
        cache_key = f"{from_user.id}_friend_requests"
        requests_count = cache.get(cache_key, 0)
        if requests_count >= 3:
            # Return a 429 response if the rate limit is exceeded
            return Response({'detail': 'You cannot send more than 3 friend requests within a minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if a friend request has already been sent to this user
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            # Return a 400 response if the friend request already exists
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the friend request
        serializer.save(from_user=from_user, to_user=to_user)

        # Update the cache to increment the friend request count
        cache.set(cache_key, requests_count + 1, timeout=60)

        # Return a 201 response indicating success
        return Response({'detail': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        """
        Override the create method to handle the friend request creation process.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A DRF Response object with the result of the operation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)


class PendingFriendRequestsView(generics.ListAPIView):
    """
    API view to list pending friend requests received by the authenticated user.
    The response includes the usernames of users who sent the friend requests.
    """
    serializer_class = PendingFriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter friend requests that are pending (i.e., not accepted) and directed to the authenticated user.

        Returns:
            QuerySet: A QuerySet containing pending FriendRequest objects.
        """
        try:
            return FriendRequest.objects.filter(to_user=self.request.user, is_accepted=False)
        except Exception:
            return FriendRequest.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Customize the response format to only include the usernames of users who sent the friend requests.
        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            Response: A Response object containing the list of pending friend requests.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Extract usernames from the serialized data
        usernames = [friend_request['from_user'] for friend_request in serializer.data]
        return Response({'pending friend requests': usernames}, status=status.HTTP_200_OK)


class RespondFriendRequestView(APIView):
    """
    API view to respond to a friend request (accept or reject).
    Uses a JSON payload to specify the username of the request sender and the response action.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to respond to a friend request.
        Validates the input data, checks the existence of the user and friend request,
        and performs the accept or reject action.
        """
        # Validate the input data
        serializer = FriendRequestResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the authenticated user (the recipient of the friend request)
        to_user = request.user
        # Get the username of the user who sent the friend request
        from_username = serializer.validated_data['username']
        # Get the response action (accept or reject)
        response = serializer.validated_data['response']

        try:
            # Try to get the user who sent the friend request
            from_user = UserProfile.objects.get(username=from_username)
            # Try to get the friend request
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
        except UserProfile.DoesNotExist:
            # Return an error response if the user does not exist
            return Response({'detail': 'User with this username does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except FriendRequest.DoesNotExist:
            # Return an error response if the friend request does not exist
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Handle the response action
        if response == 'accept':
            # If the action is accept, mark the friend request as accepted
            friend_request.accept()
            return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)
        elif response == 'reject':
            # If the action is reject, delete the friend request
            friend_request.reject()
            return Response({'detail': 'Friend request rejected.'}, status=status.HTTP_200_OK)
        else:
            # Return an error response if the action is invalid
            return Response({'detail': 'Invalid response.'}, status=status.HTTP_400_BAD_REQUEST)



class FriendsListView(APIView):
    # This view requires the user to be authenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        GET method to retrieve a list of friends for the authenticated user.
        The response contains the usernames of all accepted friends.
        """
        user = request.user

        try:
            # Query the UserProfile model to find friends
            friends = UserProfile.objects.filter(
                Q(sent_friend_requests__to_user=user, sent_friend_requests__is_accepted=True) |
                Q(received_friend_requests__from_user=user, received_friend_requests__is_accepted=True)
            ).distinct()

            # Serialize the friend data to include only usernames
            serializer = FriendListSerializer(friends, many=True)

            # Extract usernames from the serialized data
            usernames = [friend['username'] for friend in serializer.data]

            # Return the usernames in the required format
            return Response({'friends': usernames}, status=status.HTTP_200_OK)

        except Exception:
            # Handle any unexpected errors
            return Response({'detail': "Unexpected Error Occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)