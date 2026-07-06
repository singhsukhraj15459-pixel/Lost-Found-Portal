from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model. Email is unique and used for login.
    mobile_number matches the registration fields in the blueprint.
    """
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.email


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name


class LostItem(models.Model):
    STATUS_CHOICES = [
        ('searching', 'Searching'),
        ('recovered', 'Recovered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    area = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    date_lost = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='searching')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Lost - {self.area})"


class FoundItem(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Owner'),
        ('recovered', 'Recovered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='found_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    area = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='found_items/', blank=True, null=True)
    date_found = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Found - {self.area})"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"


class MatchNotification(models.Model):
    """
    Stores potential matches found by the Strategy-based matching system.
    This is what our Observer pattern will create records into (Step: Matching).
    """
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name='matches')
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE, related_name='matches')
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        unique_together = ('lost_item', 'found_item')

    def __str__(self):
        return f"Match: {self.lost_item} <-> {self.found_item}"