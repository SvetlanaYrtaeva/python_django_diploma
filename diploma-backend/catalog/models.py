from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class ActiveQuerySet(models.QuerySet):
    def active(self):
        # Возвращает только товары/категории, которые не удалены и активны
        return self.filter(is_deleted=False, is_active=True)


class Category(models.Model):
    name = models.CharField(
        "название",
        max_length=150,
    )

    slug = models.SlugField(
        "ссылка",
        max_length=180,
        unique=True,
        blank=True,
    )

    icon = models.ImageField(
        "иконка",
        upload_to="categories/",
        blank=True,
        null=True,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        "избранная категория",
        default=False,
    )

    is_active = models.BooleanField(
        "активна",
        default=True,
    )

    is_deleted = models.BooleanField(
        "удалена",
        default=False,
    )

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Seller(models.Model):
    name = models.CharField(
        "название производителя",
        max_length=150,
        unique=True,
    )

    is_deleted = models.BooleanField(
        "удалён",
        default=False,
    )

    class Meta:
        verbose_name = "производитель"
        verbose_name_plural = "производители"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "название тега",
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        "ссылка",
        max_length=120,
        unique=True,
        blank=True,
    )

    is_deleted = models.BooleanField(
        "удалён",
        default=False,
    )

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="категория",
    )

    seller = models.ForeignKey(
        Seller,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="производитель",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        blank=True,
        verbose_name="теги",
    )

    name = models.CharField(
        "название",
        max_length=255,
    )

    slug = models.SlugField(
        "ссылка",
        max_length=280,
        unique=True,
        blank=True,
    )

    image = models.ImageField(
        "изображение",
        upload_to="products/",
        blank=True,
        null=True,
    )

    short_description = models.CharField(
        "краткое описание",
        max_length=500,
    )

    description = models.TextField(
        "описание",
    )

    price = models.DecimalField(
        "цена",
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    old_price = models.DecimalField(
        "старая цена",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )

    sorting_index = models.PositiveIntegerField(
        "индекс сортировки",
        default=0,
    )

    purchases_count = models.PositiveIntegerField(
        "количество покупок",
        default=0,
    )

    limited_edition = models.BooleanField(
        "ограниченный тираж",
        default=False,
    )

    characteristics = models.JSONField(
        "характеристики",
        default=dict,
        blank=True,
    )

    is_active = models.BooleanField(
        "активен",
        default=True,
    )

    is_deleted = models.BooleanField(
        "удалён",
        default=False,
    )

    created_at = models.DateTimeField(
        "дата создания",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "дата изменения",
        auto_now=True,
    )

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = (
            "sorting_index",
            "-purchases_count",
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def reviews_count(self):

        try:
            return self.reviews.filter(is_deleted=False).count()
        except Exception:
            return 0

    def __str__(self):
        return self.name
