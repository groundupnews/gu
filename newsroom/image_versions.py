"""Custom django-filebrowser hooks for image versions (the sized copies in
_versions).

- PngToJpegNamer: a PNG without real transparency gets JPEG versions,
  named e.g. photo_large.png.jpg. The .png is kept so that photo.png and
  photo.jpg in the same folder don't share version names, and so the
  original can be found from a version.
- quantize_transparent: a version with real transparency (so it stays PNG)
  is reduced to 256 colours, which keeps transparency and shrinks it a lot.
"""
import functools
import os

from PIL import Image
from filebrowser.namers import VersionNamer
from filebrowser.settings import VERSIONS
from filebrowser.utils import get_modified_time


def has_transparency(im):
    """True if any pixel is not fully opaque."""
    if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info:
        return im.convert("RGBA").getchannel("A").getextrema()[0] < 255
    return False


@functools.lru_cache(maxsize=4096)
def _png_is_opaque(storage, path, mtime):
    with storage.open(path) as f, Image.open(f) as im:
        return not has_transparency(im)


def png_is_opaque(file_object):
    """Checked once per file (and again if the file changes). On any error
    assume transparency, which keeps filebrowser's normal behaviour."""
    storage = file_object.site.storage
    try:
        mtime = get_modified_time(storage, file_object.path)
        return _png_is_opaque(storage, file_object.path, mtime)
    except Exception:
        return False


class PngToJpegNamer(VersionNamer):
    def get_version_name(self):
        if self.extension.lower() == ".png" and png_is_opaque(self.file_object):
            return (
                self.file_object.filename_root
                + "_"
                + self.version_suffix
                + self.extension
                + ".jpg"
            )
        return super().get_version_name()

    def get_original_name(self):
        # photo_large.png.jpg -> photo.png
        root, png_ext = os.path.splitext(self.file_object.filename_root)
        if self.extension.lower() == ".jpg" and png_ext.lower() == ".png":
            name, _, suffix = root.rpartition("_")
            if name and suffix in VERSIONS:
                return name + png_ext
        return super().get_original_name()


def quantize_transparent(im, **kwargs):
    """Version processor: reduce images with real transparency to 256
    colours. Opaque images (including opaque PNGs, which become JPEG) and
    images already using a palette are left alone."""
    if im.mode != "P" and has_transparency(im):
        return im.convert("RGBA").quantize(256, method=Image.Quantize.FASTOCTREE)
    return im


quantize_transparent.valid_options = ()
