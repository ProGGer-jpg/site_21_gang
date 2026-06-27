from django.db import models

class Platform(models.Model):
    """Игровые платформы (PS4, PS5, Xbox, Switch)"""
    name = models.CharField("Название платформы", max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Платформа"
        verbose_name_plural = "Платформы"
        ordering = ['name']


class Game(models.Model):
    """Сама игра (название, жанр)"""
    title = models.CharField("Название игры", max_length=200)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, verbose_name="Платформа")
    genre = models.CharField("Жанр", max_length=100, blank=True)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return f"{self.title} ({self.platform})"

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['title']


class Disc(models.Model):
    """Физический диск (конкретный экземпляр игры)"""
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Свободен'
        IN_USE = 'IN_USE', 'В игре'
        BROKEN = 'BROKEN', 'Сломан/Ремонт'
        LOST = 'LOST', 'Утерян'

    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Игра")
    barcode = models.CharField("Инвентарный номер / Штрихкод", max_length=50, unique=True)
    condition = models.CharField("Состояние", max_length=100, default="Отличное")
    status = models.CharField(
        "Статус диска",
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    purchase_date = models.DateField("Дата покупки", null=True, blank=True)

    def __str__(self):
        return f"[{self.barcode}] {self.game.title}"

    class Meta:
        verbose_name = "Диск"
        verbose_name_plural = "Диски"
        ordering = ['barcode']


class Room(models.Model):
    """Игровая комната / Конкретная приставка"""
    name = models.CharField("Номер комнаты / Название", max_length=50)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, verbose_name="Платформа")
    is_active = models.BooleanField("Комната работает", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"
        ordering = ['name']


class Client(models.Model):
    """Клиент (используется в бронях, турнирах и т.д.)"""
    name = models.CharField("Имя / Никнейм", max_length=100)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    is_blacklisted = models.BooleanField("В черном списке", default=False)
    notes = models.TextField("Заметки о клиенте", blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    def __str__(self):
        status = "🚫" if self.is_blacklisted else "✅"
        return f"{status} {self.name}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['-created_at']