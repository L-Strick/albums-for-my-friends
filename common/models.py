import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from common.managers import UserManager


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def update(self, update_dict=None, **kwargs):
        """ Helper method to update objects """
        if not update_dict:
            update_dict = kwargs
        update_fields = {"updated_on"}
        for k, v in update_dict.items():
            setattr(self, k, v)
            update_fields.add(k)
        self.save(update_fields=update_fields)

    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser, TimestampedModel):
    email = models.EmailField(unique=True)
    username = None  # disable the AbstractUser.username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Album(TimestampedModel):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    submitted_by = models.CharField(max_length=255, null=True, blank=True)
    cover_art = models.ImageField(upload_to="covers/", null=True)
    made_todays_album = models.DateTimeField(null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.made_todays_album:
            self.made_todays_album = None
        super(Album, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} // {self.artist}"

    def get_average_score(self):
        reviews = self.reviews.filter(rating__isnull=False)
        if reviews.count() > 0:
            return sum(reviews.values_list('rating', flat=True)) / reviews.count()
        else:
            return '--'


class AlbumReview(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    album = models.ForeignKey(Album, on_delete=models.PROTECT, related_name="reviews")
    notes = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('10.0'))])
