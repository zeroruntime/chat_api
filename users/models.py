from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    online_status = models.BooleanField(default=False)  # Track online status
    last_seen = models.DateTimeField(null=True, blank=True)  # Updated only on interactions

    def __str__(self):
        return self.username

    def set_online(self):
        """Set the user as online."""
        self.online_status = True
        self.save()

    def set_offline(self):
        """Set the user as offline."""
        self.online_status = False
        self.save()

    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen = models.functions.Now()  # Current time
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)   

    def __str__(self):
        return f"Profile of {self.user.username}"


# Signal to create the user profile automatically
@receiver(post_save, sender=CustomUser)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
