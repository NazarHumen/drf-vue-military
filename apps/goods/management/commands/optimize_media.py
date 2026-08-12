from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

from apps.goods.models import ProductImage, Products, product_image_path
from apps.users.models import User, user_image_path

MAX_SIDE = 1920
QUALITY = 82

# Each model paired with the upload_to helper that defines its layout,
# so --restructure reproduces exactly what a fresh upload would create.
SPECS = (
    (Products, product_image_path),
    (ProductImage, product_image_path),
    (User, user_image_path),
)


class Command(BaseCommand):
    help = (
        "Converts product images to WebP and optionally moves them into "
        "product_<id>/ folders, updating the paths stored in the DB"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the plan without touching the disk or the DB",
        )
        parser.add_argument(
            "--restructure",
            action="store_true",
            help="Move files into goods_images/product_<id>/",
        )
        parser.add_argument(
            "--no-convert",
            action="store_true",
            help="Skip WebP conversion (move files only)",
        )

    def handle(self, *args, **options):
        self.dry = options["dry_run"]
        self.restructure = options["restructure"]
        self.to_webp = not options["no_convert"]

        if not self.to_webp and not self.restructure:
            raise CommandError(
                "--no-convert without --restructure does nothing"
            )

        self.media_root = Path(settings.MEDIA_ROOT)
        # Destinations already assigned in this run. Needed because under
        # --dry-run nothing is written, so two rows aiming at the same
        # target would otherwise both look free.
        self.planned = set()

        saved = 0
        done = 0
        skipped = 0

        # Iterate over DB rows, not over the filesystem: the stored path
        # and the file on disk have to change together, otherwise every
        # image 404s while the DB still points at the old location.
        for model, path_for in SPECS:
            qs = model.objects.exclude(image="").exclude(image__isnull=True)
            for obj in qs.iterator():
                freed = self.process(model, obj, path_for)
                if freed is None:
                    skipped += 1
                else:
                    saved += freed
                    done += 1

        self.report(done, skipped, saved)

    def report(self, done, skipped, saved):
        if self.dry:
            self.stdout.write(
                self.style.WARNING(
                    f"[dry-run] to process: {done}, unchanged: {skipped}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {done} images, unchanged: {skipped}, "
                f"freed ~{saved // 1024 // 1024} MB"
            )
        )

    def process(self, model, obj, path_for):
        """Convert and/or move one image.

        Returns the number of bytes freed, or None when the row needs no
        work (already in its target shape, or the file is missing).
        """
        name = obj.image.name
        old_path = self.media_root / name
        if not old_path.exists():
            self.stderr.write(self.style.WARNING(f"missing file: {name}"))
            return None

        new_name = self.target_name(obj, name, path_for)
        if new_name == name:
            return None

        new_path = self.free_path(self.media_root / new_name, old_path)
        new_name = new_path.relative_to(self.media_root).as_posix()
        self.planned.add(new_path)

        before = old_path.stat().st_size
        if self.dry:
            self.stdout.write(f"{name}\n  -> {new_name} ({before // 1024} KB)")
            return 0

        new_path.parent.mkdir(parents=True, exist_ok=True)
        if self.to_webp:
            self.save_as_webp(old_path, new_path)
            old_path.unlink()
        else:
            old_path.rename(new_path)

        # update() instead of obj.save(): the overridden Products.save()
        # refetches the exchange rate and recalculates prices on every
        # call, which has no place in a bulk media rewrite.
        model.objects.filter(pk=obj.pk).update(image=new_name)

        after = new_path.stat().st_size
        self.stdout.write(
            f"{name}\n"
            f"  -> {new_name} ({before // 1024} KB -> {after // 1024} KB)"
        )
        return before - after

    def target_name(self, obj, name, path_for):
        """Build the destination path relative to MEDIA_ROOT."""
        source = Path(name)
        filename = source.name
        if self.to_webp:
            filename = Path(filename).with_suffix(".webp").name

        if self.restructure:
            # Reuse the upload_to helper so the layout matches exactly
            # what new uploads produce.
            return path_for(obj, filename)
        # ImageField stores POSIX separators, while Path on Windows
        # renders "\" — as_posix() keeps the DB value portable to prod.
        return source.with_name(filename).as_posix()

    def free_path(self, target, source):
        """Return a destination that collides with nothing.

        Orphaned files left over from earlier uploads may already occupy
        the target name, so a numeric suffix is appended when needed.
        """
        if target == source:
            return target

        candidate = target
        counter = 1
        while candidate.exists() or candidate in self.planned:
            candidate = target.with_name(
                f"{target.stem}_{counter}{target.suffix}"
            )
            counter += 1
        return candidate

    def save_as_webp(self, old_path, new_path):
        img = Image.open(old_path)
        # WebP supports alpha, so RGBA is kept as is — converting to RGB
        # would turn transparent backgrounds into a black rectangle.
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        # thumbnail() only ever scales down, so smaller files stay intact.
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        img.save(new_path, "WEBP", quality=QUALITY, method=6)
