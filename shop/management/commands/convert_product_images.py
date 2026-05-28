from io import BytesIO
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from PIL import Image

from shop.models import Product


class Command(BaseCommand):
    help = "Convert existing product images to WEBP"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quality",
            type=int,
            default=75,
            help="WEBP quality (1-100). Default: 75",
        )

        parser.add_argument(
            "--max-size",
            type=int,
            default=500,
            help="Maximum width/height in pixels. Default: 500",
        )

        parser.add_argument(
            "--method",
            type=int,
            default=6,
            choices=range(0, 7),
            help="WEBP compression method (0-6). Default: 6",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate conversion without saving files",
        )

        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Re-convert already existing WEBP images",
        )

    def handle(self, *args, **options):

        quality = options["quality"]
        max_size = options["max_size"]
        method = options["method"]
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]

        products = Product.objects.exclude(image="")

        total = products.count()
        converted = 0
        skipped = 0
        failed = 0

        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Starting WEBP conversion..."))
        self.stdout.write(f"Products found: {total}")
        self.stdout.write(f"Quality: {quality}")
        self.stdout.write(f"Max Size: {max_size}px")
        self.stdout.write(f"Compression Method: {method}")
        self.stdout.write(f"Dry Run: {dry_run}")
        self.stdout.write("")

        for index, product in enumerate(products, start=1):

            if not product.image:
                skipped += 1
                continue

            old_name = product.image.name

            self.stdout.write(
                f"[{index}/{total}] Processing: {old_name}"
            )

            if old_name.lower().endswith(".webp") and not overwrite:
                skipped += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped already WEBP: {old_name}"
                    )
                )
                continue

            try:

                # Open from storage backend
                with product.image.open("rb") as image_file:

                    with Image.open(image_file) as img:

                        # Convert unsupported modes
                        # if img.mode not in ("RGB",):
                        #     img = img.convert("RGB")
                        if img.mode in ("RGBA", "LA"):
                            pass
                        elif img.mode != "RGB":
                            img = img.convert("RGB")

                        # Resize while preserving ratio
                        img.thumbnail((max_size, max_size))

                        # Save WEBP to memory
                        img_io = BytesIO()

                        img.save(
                            img_io,
                            format="WEBP",
                            quality=quality,
                            method=method,
                            optimize=True,
                        )

                        img_io.seek(0)

                        # Build new filename
                        base_name = os.path.splitext(old_name)[0]
                        new_name = f"{base_name}.webp"

                        if dry_run:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"[DRY RUN] Would convert: "
                                    f"{old_name} → {new_name}"
                                )
                            )
                            converted += 1
                            continue

                        # Atomic DB transaction
                        # with transaction.atomic():

                        #     # Save old name before overwrite
                        #     old_storage_name = old_name

                        #     # Save converted image
                        #     product.image.save(
                        #         new_name,
                        #         ContentFile(img_io.read()),
                        #         save=False,
                        #     )

                        #     product.save(update_fields=["image"])

                        #     # Delete old file from storage backend
                        #     if old_storage_name != new_name:
                        #         product.image.storage.delete(
                        #             old_storage_name
                        #         )
                        
                        old_storage_name = old_name

                        with transaction.atomic():

                            product.image.save(
                                new_name,
                                ContentFile(img_io.getvalue()),
                                save=False,
                            )

                            product.save(update_fields=["image"])
                            
                        # Delete old file after file handles close
                        if (
                            old_storage_name != new_name
                            and product.image.storage.exists(old_storage_name)
                        ):
                            try:
                                product.image.storage.delete(old_storage_name)
                            except Exception as delete_error:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Could not delete old file: "
                                        f"{old_storage_name}"
                                    )
                                )
                                self.stdout.write(str(delete_error))

                        converted += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Converted: "
                                f"{old_name} → {new_name}"
                            )
                        )

            except Exception as e:

                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"Failed: {old_name}"
                    )
                )

                self.stdout.write(
                    self.style.ERROR(str(e))
                )

        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS("WEBP Conversion Finished"))
        self.stdout.write("=" * 50)

        self.stdout.write(f"Total Products : {total}")
        self.stdout.write(
            self.style.SUCCESS(f"Converted      : {converted}")
        )
        self.stdout.write(
            self.style.WARNING(f"Skipped        : {skipped}")
        )

        if failed:
            self.stdout.write(
                self.style.ERROR(f"Failed         : {failed}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Failed         : 0")
            )

        self.stdout.write("")