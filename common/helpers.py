from common.models import User, Album


def get_valid_users():
    recent_albums = Album.objects.order_by('-made_todays_album').prefetch_related('reviews', 'reviews__user')[:MISSED_ALBUM_CAP]
    valid_users = set()
    # The Grant Exception 🫡
    valid_users.add(User.objects.get(email="gbirindelli20@gmail.com").id)
    for album in recent_albums:
        reviewed_users = [review.user for review in album.reviews.all()]
        for user in reviewed_users:
            valid_users.add(user.id)

    return User.objects.filter(id__in=valid_users)
