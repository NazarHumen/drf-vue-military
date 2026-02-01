from django import template

from apps.favorites.models import Favorite

register = template.Library()


@register.simple_tag()
def user_favorites(request):
    # Отримуємо всі обрані товари для поточного користувача
    favorites = Favorite.objects.filter(user=request.user)

    # Повертаємо кількість обраних товарів та самі товари
    return {"total_quantity": favorites.count(), "favorites": favorites}
