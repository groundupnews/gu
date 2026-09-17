"""S18A certificate PDF rendering."""

import base64
import mimetypes
import os
import re

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from weasyprint import CSS, HTML

from . import settings as donation_settings


def _image_data_uri(static_path):
    """base64 data URI for a static image, so it embeds straight into the
    PDF without needing network access or collected static files."""
    path = finders.find(static_path)
    if not path or not os.path.exists(path):
        return ""
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode("ascii")
    return "data:{};base64,{}".format(mime, encoded)


def _certificate_context(certificate):
    return {
        'certificate': certificate,
        'pbo': donation_settings.S18A_PBO,
        'logo_uri': _image_data_uri("donationPage/groundup-logo.png"),
        'signature_uri': _image_data_uri("donationPage/nathan_sig.jpg"),
    }


FONT_SIZES = (17, 16, 15, 14, 13, 12, 11, 10)


def render_certificate_pdf(certificate):
    """Render a certificate to PDF bytes using WeasyPrint.

    page size and margins come from the @page rule in the template;
    images are embedded as data URIs
    """
    html = render_to_string('donationPage/certificate_pdf.html',
                            _certificate_context(certificate))
    document = HTML(string=html)
    for font_size in FONT_SIZES:
        sheet = CSS(string="html {{ font-size: {}px !important; }}"
                    .format(font_size))
        rendered = document.render(stylesheets=[sheet])
        if len(rendered.pages) == 1:
            break
    return rendered.write_pdf()


def certificate_filename(certificate):
    """Filename for the issued PDF.

    the donor name is donor-supplied, so we strip it down to characters
    that are safe to drop into a Content-Disposition header and a file path.
    """
    ref = certificate.receipt_number or "draft"
    fy = "-FY{}".format(certificate.tax_year) if certificate.tax_year else ""
    name = "GroundUp-{}-S18A-{}{}".format(ref, certificate.donor_name, fy)
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')
    return (name or "GroundUp-S18A") + ".pdf"


def certificate_pdf_bytes(certificate):
    """The bytes to serve/attach - the archived file once approved"""
    if certificate.pdf_file:
        try:
            with certificate.pdf_file.open('rb') as fh:
                return fh.read()
        except (OSError, ValueError):
            pass
    return render_certificate_pdf(certificate)
