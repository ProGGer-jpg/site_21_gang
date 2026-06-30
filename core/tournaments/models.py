from django.db import models
from django.conf import settings
from catalog_21.models import Game


class Tournament(models.Model):
    """Турнир по игре"""
    class Status(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Предстоящий'
        ACTIVE = 'ACTIVE', 'Активный'
        FINISHED = 'FINISHED', 'Завершён'

    title = models.CharField("Название турнира", max_length=200)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Игра")
    description = models.TextField("Описание", blank=True)
    date = models.DateField("Дата проведения")
    time = models.TimeField("Время начала")
    location = models.CharField("Место проведения", max_length=200, help_text="Например: Комната 1, Главный зал")
    max_participants = models.PositiveIntegerField("Максимум участников", default=8)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.UPCOMING)
    finished_at = models.DateTimeField("Завершён в", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Создал"
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.game.title} ({self.date})"

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"
        ordering = ['-date', '-time']


class TournamentParticipant(models.Model):
    """Участник турнира"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Участник",
        related_name='tournament_participations'
    )
    registered_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.tournament.title}"

    class Meta:
        verbose_name = "Участник турнира"
        verbose_name_plural = "Участники турниров"
        unique_together = ['tournament', 'user']
        ordering = ['registered_at']


class TournamentResult(models.Model):
    """Результат турнира (место участника)"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Участник",
        related_name='tournament_results'
    )
    place = models.PositiveIntegerField("Место")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.tournament.title} ({self.place} место)"

    class Meta:
        verbose_name = "Результат турнира"
        verbose_name_plural = "Результаты турниров"
        unique_together = ['tournament', 'user']
        ordering = ['place']


class PlayerRating(models.Model):
    """Рейтинг игрока"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Игрок",
        related_name='player_rating'
    )
    rating = models.IntegerField("Рейтинг", default=0)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}: {self.rating}"

    class Meta:
        verbose_name = "Рейтинг игрока"
        verbose_name_plural = "Рейтинги игроков"
        ordering = ['-rating']