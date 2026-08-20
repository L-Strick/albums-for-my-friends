from common.constants import MISSED_ALBUM_CAP
from common.models import User, Album


def get_valid_users():
    recent_albums = Album.objects.order_by('-made_todays_album').prefetch_related('reviews', 'reviews__user')[:MISSED_ALBUM_CAP]
    valid_users = set()
    # The Grant Exception 🫡
    grant = User.objects.filter(email="gbirindelli20@gmail.com")
    if grant.exists():
        valid_users.add(grant.first().id)
    for album in recent_albums:
        reviewed_users = [review.user for review in album.reviews.all()]
        for user in reviewed_users:
            valid_users.add(user.id)

    if len(valid_users) == 0:
        valid_users = User.objects.all().values_list("id", flat=True)

    return User.objects.filter(id__in=valid_users)
