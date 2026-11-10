"""Keep images out of article HTML.

Images pasted from Word or Google Docs arrive in the editor either embedded
(data:image/...;base64,...) or as links to Google's servers, which can
expire. Both are converted to JPEG and stored under PASTED_DIR, and the
<img> is pointed at the ARTICLE_VERSION copy.
"""
import base64
import binascii
import io
import logging
import re
import secrets
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from filebrowser.base import FileObject
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

PASTED_DIR = "uploads/images/pasted"
ARTICLE_VERSION = "extra_large"
MAX_WIDTH = 2000
JPEG_QUALITY = 90
MAX_BYTES = 10 * 1024 * 1024  # same as FILEBROWSER_MAX_UPLOAD_SIZE
FETCH_TIMEOUT = 15
REMOTE_HOST_SUFFIX = ".googleusercontent.com"
DATA_URI = re.compile(r"^data:image/[\w.+-]+;base64,(.*)$", re.I | re.S)


class ImageError(Exception):
    pass


def store_image(data):
    """Convert image bytes to JPEG (transparency onto white, at most
    MAX_WIDTH wide), save in PASTED_DIR/YYYY/MM/ and return the URL of
    its ARTICLE_VERSION copy."""
    if len(data) > MAX_BYTES:
        raise ImageError("it is larger than 10 MB")
    try:
        with Image.open(io.BytesIO(data)) as source:
            im = ImageOps.exif_transpose(source)
            im.load()
    except (OSError, SyntaxError, Image.DecompressionBombError) as e:
        raise ImageError("it is not a readable image") from e
    if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info:
        rgba = im.convert("RGBA")
        im = Image.new("RGB", rgba.size, "white")
        im.paste(rgba, mask=rgba.getchannel("A"))
    else:
        im = im.convert("RGB")
    if im.width > MAX_WIDTH:
        height = round(im.height * MAX_WIDTH / im.width)
        im = im.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True)
    name = "{}/{:%Y/%m}/pasted-{}.jpg".format(
        PASTED_DIR, timezone.localtime(), secrets.token_hex(4)
    )
    path = default_storage.save(name, ContentFile(out.getvalue()))
    return FileObject(path).version_generate(ARTICLE_VERSION).url


def decode_data_uri(src):
    match = DATA_URI.match(src.strip())
    if not match:
        raise ImageError("it is not an embedded image we recognise")
    payload = re.sub(r"\s+", "", match.group(1))
    if len(payload) * 3 // 4 > MAX_BYTES:
        raise ImageError("it is larger than 10 MB")
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ImageError("the embedded data is corrupt") from e


def is_google_image(src):
    url = urlparse(src.strip())
    host = (url.hostname or "").lower()
    return url.scheme == "https" and host.endswith(REMOTE_HOST_SUFFIX)


def fetch_google_image(url):
    """Download an image from Google's servers. Redirects are followed by
    hand so that we never fetch from anywhere except googleusercontent.com."""
    try:
        for _ in range(4):
            if not is_google_image(url):
                raise ImageError("Google redirected it to another site")
            response = requests.get(
                url,
                timeout=FETCH_TIMEOUT,
                stream=True,
                allow_redirects=False,
                headers={"User-Agent": "GroundUp image copier"},
            )
            with response:
                if response.is_redirect:
                    url = urljoin(url, response.headers["Location"])
                    continue
                if response.status_code != 200:
                    raise ImageError(
                        f"Google returned error {response.status_code}"
                    )
                content_type = response.headers.get("Content-Type", "")
                if not content_type.startswith("image/"):
                    raise ImageError("Google did not return an image")
                data = bytearray()
                for chunk in response.iter_content(64 * 1024):
                    data += chunk
                    if len(data) > MAX_BYTES:
                        raise ImageError("it is larger than 10 MB")
                return bytes(data)
        raise ImageError("there were too many redirects")
    except requests.RequestException as e:
        raise ImageError("it could not be downloaded from Google") from e


def process_html(html, skip_srcs=()):
    """Store embedded and Google images found in html.

    Returns (new_html, problems, failed_srcs). new_html is None if nothing
    changed. Embedded images that can't be stored are removed, never kept.
    Google images that can't be copied are left pointing at Google."""
    markers = ("data:image", "googleusercontent.com", "file:", "blob:")
    if not html or not any(m in html for m in markers):
        return None, [], []
    soup = BeautifulSoup(html, "html.parser")
    changed = False
    problems = []
    failed = []
    for img in soup.find_all("img", src=True):
        src = img["src"].strip()
        lower = src[:5].lower()
        try:
            if lower == "data:":
                img["src"] = store_image(decode_data_uri(src))
            elif is_google_image(src) and src not in skip_srcs:
                img["src"] = store_image(fetch_google_image(src))
            elif lower in ("file:", "blob:"):
                problems.append(
                    "A pasted image points to a file on the editor's own "
                    "computer and will not show on the site. Please insert "
                    "it with the image button."
                )
                continue
            else:
                continue
            for attr in ("srcset", "width", "height"):
                if attr in img.attrs:
                    del img[attr]
            changed = True
        except ImageError as e:
            logger.warning("Pasted image not stored: %s", e)
            if lower == "data:":
                img.decompose()
                changed = True
                problems.append(
                    f"A pasted image was removed because {e}. Please insert "
                    "it with the image button."
                )
            else:
                failed.append(src)
                problems.append(
                    f"An image from Google Docs could not be copied to our "
                    f"server because {e}. It still points to Google and may "
                    "stop working: please download it and insert it with "
                    "the image button."
                )
    return (str(soup) if changed else None), problems, failed
