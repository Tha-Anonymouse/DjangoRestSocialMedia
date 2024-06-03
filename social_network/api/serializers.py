from rest_framework import serializers
from .models import UserProfile, FriendRequest

# Serializer for UserProfile model to handle user-related data
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

    def create(self, validated_data):
        """
        Create and return a new UserProfile instance, given the validated data.
        """
        # Create user with the provided email and username
        user = UserProfile(
            email=validated_data['email'],
            username=validated_data['username']
        )
        # Hash the password and save the user instance
        user.set_password(validated_data['password'])
        user.save()
        return user


# Serializer for FriendRequest model to handle friend request data
class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserProfileSerializer(read_only=True)  # Nested serialization for from_user
    to_user = UserProfileSerializer(read_only=True)    # Nested serialization for to_user

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'is_accepted')
        read_only_fields = ('from_user', 'is_accepted')  # Ensure these fields are read-only


# Serializer to handle the creation of FriendRequest instances
class FriendRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id',)

    def create(self, validated_data):
        """
        Create and return a new FriendRequest instance, given the validated data.
        This method ensures that duplicate friend requests are not created.
        """
        # Extract from_user and to_user from validated data
        from_user = validated_data["from_user"]
        to_user = validated_data['to_user']

        # Check if a friend request already exists between these users
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError('Friend request already sent.')

        # Create and return the new FriendRequest instance
        return FriendRequest.objects.create(from_user=from_user, to_user=to_user)


# Serializer to handle pending friend requests
class PendingFriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(slug_field='username', queryset=UserProfile.objects.all())  # Use username for from_user

    class Meta:
        model = FriendRequest
        fields = ['from_user']


# Serializer to list friends with only their usernames
class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username']  # Only include the username field


# Serializer to handle friend request responses (accept/reject)
class FriendRequestResponseSerializer(serializers.Serializer):
    username = serializers.CharField()
    response = serializers.ChoiceField(choices=[('accept', 'Accept'), ('reject', 'Reject')])  # Limit response to accept or reject



