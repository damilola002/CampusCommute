from django.db import models
from django.conf import settings


class RideOrder(models.Model):
    PENDING   = "pending"
    ACCEPTED  = "accepted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    STATUS_CHOICES = [
        (PENDING,   "Pending"),
        (ACCEPTED,  "Accepted"),
        (CANCELLED, "Cancelled"),
        (COMPLETED, "Completed"),
    ]

    RIDE_TYPE_CHOICES = [
        ('request', 'Request'),   # rider asks for a lift
        ('offer',   'Offer'),     # driver posts an available ride
    ]

    rider  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ride_orders")
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="accepted_rides")

    ride_type        = models.CharField(max_length=10, choices=RIDE_TYPE_CHOICES, default='request')
    pickup_location  = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat       = models.FloatField()
    pickup_lng       = models.FloatField()

    approx_time    = models.DateTimeField()
    num_passengers = models.PositiveIntegerField(default=1)
    description    = models.TextField(blank=True)

    # Fields for "offer" type rides
    offered_seats = models.PositiveIntegerField(default=1, help_text="Total seats driver is offering")
    claimed_seats = models.PositiveIntegerField(default=0, help_text="Seats claimed by riders so far")

    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ordering_service"
        ordering = ["-created_at"]

    @property
    def available_seats(self):
        return max(0, self.offered_seats - self.claimed_seats)

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


class RideClaim(models.Model):
    """Records a rider claiming seats on a driver-offered ride."""
    ride_order = models.ForeignKey(RideOrder, on_delete=models.CASCADE, related_name="claims")
    rider      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ride_claims")
    seats_taken = models.PositiveIntegerField(default=1)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ordering_service"
        ordering = ["-created_at"]
        unique_together = [("ride_order", "rider")]  # one claim per rider per ride

    def __str__(self):
        return f"{self.rider} claimed {self.seats_taken} seat(s) on ride {self.ride_order_id}"


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


class ChatMessage(models.Model):
    ride_order = models.ForeignKey(RideOrder, on_delete=models.CASCADE, related_name='chat_messages')
    sender     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content_encrypted = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ordering_service'
        ordering = ['created_at']

    def encrypt_and_save(self, plain_text):
        from .crypto import encrypt_message
        self.content_encrypted = encrypt_message(plain_text)
        self.save()

    def get_decrypted_content(self):
        from .crypto import decrypt_message
        try:
            return decrypt_message(self.content_encrypted)
        except Exception:
            return "[Decryption Error]"

    def __str__(self):
        return f"Message from {self.sender} on ride {self.ride_order_id}"
