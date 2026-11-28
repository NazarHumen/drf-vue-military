from apps.favorites.models import Favorite


def get_user_favorites(request):
    """Get favorite products for the user or session."""
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
    Merges favorite products from the session with the user's favorite products
    after login.
    """
    session_key = request.session.session_key
    if not session_key:
        return

    session_favorites = Favorite.objects.filter(session_key=session_key)

    for favorite in session_favorites:
        # Check if the product is already in the user's favorites
        existing = Favorite.objects.filter(
            user=user, product=favorite.product
        ).first()

        if not existing:
            # Migrate the product to the user
            favorite.user = user
            favorite.session_key = None
            favorite.save()
        else:
            # Remove duplicate from session
            favorite.delete()
