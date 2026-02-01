from apps.favorites.models import Favorite


def get_user_favorites(request):
    """Отримує обрані товари для користувача або сесії."""
    if request.user.is_authenticated:
        return Favorite.objects.filter(user=request.user).select_related(
            "product"
        )

    if not request.session.session_key:
        request.session.create()

    return Favorite.objects.filter(
        session_key=request.session.session_key
    ).select_related("product")


def merge_favorites_on_login(request, user):
    """
    Об'єднує обрані товари з сесії з обраними товарами користувача
    після авторизації.
    """
    session_key = request.session.session_key
    if not session_key:
        return

    session_favorites = Favorite.objects.filter(session_key=session_key)

    for favorite in session_favorites:
        # Перевіряємо чи товар вже є в обраних користувача
        existing = Favorite.objects.filter(
            user=user, product=favorite.product
        ).first()

        if not existing:
            # Переносимо товар до користувача
            favorite.user = user
            favorite.session_key = None
            favorite.save()
        else:
            # Видаляємо дублікат з сесії
            favorite.delete()
