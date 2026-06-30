from .models import PlayerRating


class AutoCreatePlayerRatingMiddleware:
    """Автоматически создаёт запись в рейтинге для обычных пользователей"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, что пользователь авторизован и НЕ является staff
        if (request.user.is_authenticated and
                not request.user.is_staff and
                not PlayerRating.objects.filter(user=request.user).exists()):
            # Создаём запись с рейтингом 0
            PlayerRating.objects.create(user=request.user, rating=0)

        response = self.get_response(request)
        return response