from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    """
    Custom user model extending Django's AbstractUser to include email as a unique field.
    This model also redefines the groups and user_permissions fields to use a custom related_name.
    """

    email = models.EmailField(unique=True)  # Email field, must be unique for each user

    # Redefine groups field with a custom related_name to avoid clashes with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_profile_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )

    # Redefine user_permissions field with a custom related_name to avoid clashes with the default User model
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_profile_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    REQUIRED_FIELDS = ['email']  # Email is required for creating a user via createsuperuser
    USERNAME_FIELD = 'username'  # Use username as the unique identifier for authentication

    def __str__(self):
        """String representation of the UserProfile model."""
        return f"{self.username} ({self.email})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['username']  # Default ordering by username

class FriendRequest(models.Model):
    """
    Model representing a friend request between two users.
    """

    # Foreign key to the user who sent the friend request
    from_user = models.ForeignKey(
        UserProfile,
        related_name='sent_friend_requests',
        on_delete=models.CASCADE
    )

    # Foreign key to the user who received the friend request
    to_user = models.ForeignKey(
        UserProfile,
        related_name='received_friend_requests',
        on_delete=models.CASCADE
    )

    # Boolean field indicating whether the friend request was accepted
    is_accepted = models.BooleanField(default=False)

    class Meta:
        # Ensure that a user cannot send multiple friend requests to the same user
        unique_together = ('from_user', 'to_user')
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'
        ordering = ['from_user']  # Default ordering by from_user

    def __str__(self):
        """String representation of the FriendRequest model."""
        return f"FriendRequest from {self.from_user.username} to {self.to_user.username}"

    def accept(self):
        """Accept the friend request."""
        self.is_accepted = True
        self.save()

    def reject(self):
        """Reject the friend request."""
        self.delete()

