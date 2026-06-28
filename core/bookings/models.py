from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalog_21.models import Disc, Room
from django.contrib.auth.models import User
from datetime import timedelta


class Booking(models.Model):
    MAX_HOURS = 3
    """Запись в тетради (Бронирование)"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активна'
        COMPLETED = 'COMPLETED', 'Завершена'
        CANCELED = 'CANCELED', 'Отменена'

    # Данные клиента (оставляем текстом для скорости, как в тетради)
    client_name = models.CharField("Имя клиента", max_length=100)
    client_phone = models.CharField("Телефон", max_length=20, blank=True)

    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Оформил сотрудник",
        null=True,
        blank=True
    )

    # Связь с каталогом
    disc = models.ForeignKey(Disc, on_delete=models.PROTECT, verbose_name="Диск с игрой")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Комната")

    # Время
    start_time = models.DateTimeField("Начало")
    end_time = models.DateTimeField("Конец")

    # Статус и доп. инфо
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField("Комментарий админа", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def clean(self):
        """Проверка на пересечение броней и ограничение по времени"""
        super().clean()
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            now = timezone.now()

            # 1. Проверка логики времени
            if self.start_time >= self.end_time:
                raise ValidationError("Время начала должно быть раньше времени конца.")

            # 2. Запрет бронирования в прошлом (с окном 5 минут)
            if self.start_time < now - timedelta(minutes=5):
                raise ValidationError("Нельзя создавать брони в прошлом.")

            # 3. Проверка на максимальное время (3 часа)
            if duration > timedelta(hours=self.MAX_HOURS):
                raise ValidationError(
                    f"Бронирование не может быть дольше {self.MAX_HOURS} часов."
                )

            # 4. Проверка на минимальное время (30 минут)
            if duration < timedelta(minutes=30):
                raise ValidationError("Минимальное время бронирования — 30 минут.")

            # 5. Проверка на пересечения дисков
            overlapping_disc = Booking.objects.filter(
                disc=self.disc,
                status='ACTIVE',
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
            if self.pk:
                overlapping_disc = overlapping_disc.exclude(pk=self.pk)
            if overlapping_disc.exists():
                raise ValidationError(f"Диск '{self.disc}' уже забронирован на это время!")

            # 6. Проверка на занятость комнаты (максимум 1 бронь в комнате одновременно)
            overlapping_room = Booking.objects.filter(
                room=self.room,
                status='ACTIVE',
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
            if self.pk:
                overlapping_room = overlapping_room.exclude(pk=self.pk)
            if overlapping_room.exists():
                raise ValidationError(f"Комната '{self.room}' уже занята на это время!")

            # 7. Проверка лимитов для сотрудника
            if self.employee:
                # Определяем: новая бронь активная или запланированная?
                is_active_booking = self.start_time <= now
                is_planned_booking = self.start_time > now

                if is_active_booking:
                    # Лимит активных броней: максимум 1
                    active_count = Booking.objects.filter(
                        employee=self.employee,
                        status='ACTIVE',
                        start_time__lte=now,
                        end_time__gte=now
                    )
                    if self.pk:
                        active_count = active_count.exclude(pk=self.pk)

                    if active_count.count() >= 1:
                        raise ValidationError(
                            "У вас уже есть 1 активная бронь. "
                            "Нельзя оформлять больше 1 активной брони одновременно."
                        )

                if is_planned_booking:
                    # Лимит запланированных броней: максимум 2
                    planned_count = Booking.objects.filter(
                        employee=self.employee,
                        status='ACTIVE',
                        start_time__gt=now
                    )
                    if self.pk:
                        planned_count = planned_count.exclude(pk=self.pk)

                    if planned_count.count() >= 2:
                        raise ValidationError(
                            "У вас уже есть 2 запланированные брони. "
                            "Максимум 2 запланированные брони на сотрудника."
                        )

    def __str__(self):
        return f"{self.client_name} -> {self.disc.game.title} ({self.start_time:%d.%m %H:%M})"

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ['-start_time']