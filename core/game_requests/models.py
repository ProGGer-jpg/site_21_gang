from django.db import models
from django.conf import settings
from catalog_21.models import Platform


class GameRequest(models.Model):
    """Заявка от сотрудника на добавление новой игры в каталог."""

    STATUS_NEW = 'new'
    STATUS_APPROVED = 'approved'
    STATUS_ADDED = 'added'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_APPROVED, 'Одобрена'),
        (STATUS_ADDED, 'Игра добавлена'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    title = models.CharField("Название игры", max_length=200)
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        verbose_name="Платформа",
        related_name="game_requests",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Кто подал заявку",
        related_name="game_requests",
    )
    reason = models.TextField(
        "Почему стоит добавить",
        help_text="Например: клиенты часто просят",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    admin_comment = models.TextField(
        "Комментарий администратора",
        blank=True,
        default="",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.platform}) — {self.get_status_display()}"

    class Meta:
        verbose_name = "Заявка на игру"
        verbose_name_plural = "Заявки на игры"
        ordering = ['-created_at']