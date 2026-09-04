import os
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.models import Product


class Command(BaseCommand):
    help = "Привязывает картинки из папки фронтенда к товарам"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default=None,
            help="Папка с картинками",
        )

    def handle(self, *args, **options):
        source = options.get("source")
        if source:
            image_dirs = [source]
        else:
            base = settings.BASE_DIR
            image_dirs = [
                os.path.join(base, "diploma-frontend", "frontend", "static", "frontend", "assets", "img", "content"),
                os.path.join(base, "..", "diploma-frontend", "frontend", "static", "frontend", "assets", "img", "content"),
            ]

        image_files = []
        for img_dir in image_dirs:
            if os.path.isdir(img_dir):
                for root, dirs, files in os.walk(img_dir):
                    for f in files:
                        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            image_files.append(os.path.join(root, f))

        if not image_files:
            self.stdout.write(self.style.ERROR(
                "Картинки не найдены! Укажи папку через --source /path/to/images"
            ))
            return

        self.stdout.write(f"Найдено картинок: {len(image_files)}")
        for f in image_files:
            self.stdout.write(f"  {f}")

        media_products = os.path.join(settings.MEDIA_ROOT, "products")
        os.makedirs(media_products, exist_ok=True)

        products = Product.objects.filter(is_deleted=False).order_by("id")
        self.stdout.write(f"Товаров в базе: {products.count()}")

        assigned = 0
        for i, product in enumerate(products):
            src = image_files[i % len(image_files)]
            filename = f"product_{product.id}_{os.path.basename(src)}"
            dst = os.path.join(media_products, filename)
            shutil.copy2(src, dst)

            product.image = f"products/{filename}"
            product.save(update_fields=["image"])
            assigned += 1
            self.stdout.write(f"  [{i + 1}] {product.name} -> products/{filename}")

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Привязано картинок: {assigned} (из {len(image_files)} уникальных)"
        ))
