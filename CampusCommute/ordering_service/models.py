from django.db import models
from django.conf import settings


class RideOrder(models.Model):
    PENDING   = "pending"
    ACCEPTED  = "accepted"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING,   "Pending"),
        (ACCEPTED,  "Accepted"),
        (CANCELLED, "Cancelled"),
    ]

    rider  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ride_orders")
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="accepted_rides")

    pickup_location  = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat       = models.FloatField()
    pickup_lng       = models.FloatField()

    approx_time    = models.DateTimeField()
    num_passengers = models.PositiveIntegerField(default=1)
    description    = models.TextField(blank=True)

    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ordering_service"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rider} to {self.dropoff_location} [{self.status}]"


class Notification(models.Model):
    recipient  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    ride_order = models.ForeignKey(RideOrder, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ordering_service"
        ordering = ["-created_at"]

    def __str__(self):
        return f"to {self.recipient}: {self.message[:60]}"


class RideReview(models.Model):
    ride = models.OneToOneField(RideOrder, on_delete=models.CASCADE, related_name='review')
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ordering_service'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.driver} by {self.rider} - {self.rating} Stars"


class CommunityPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ordering_service'
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author} at {self.created_at}"


class PostComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ordering_service'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
