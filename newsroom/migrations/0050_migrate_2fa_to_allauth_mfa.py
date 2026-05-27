import base64
import binascii

from django.db import migrations


def migrate_totp_secrets(apps, schema_editor):
    """
    Migrate TOTP secrets from django_otp's otp_totp_totpdevice table
    to allauth.mfa's allauth_mfa_authenticator table.

    django_otp stores the key as a hex-encoded string.
    allauth.mfa stores the secret as base32 in a JSON data field.
    """
    Authenticator = apps.get_model("mfa", "Authenticator")
    connection = schema_editor.connection

    if "otp_totp_totpdevice" not in connection.introspection.table_names():
        print("\n2FA migration: no django-otp TOTP table found; skipped.")
        return

    migrated = 0
    skipped = 0

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT user_id, key
            FROM otp_totp_totpdevice
            WHERE confirmed = %s
            """,
            [True],
        )
        devices = cursor.fetchall()

    for user_id, key in devices:
        # conv hex key -> raw bytes -> base32 string
        try:
            secret_b32 = base64.b32encode(binascii.unhexlify(key)).decode("ascii")
        except (binascii.Error, ValueError):
            skipped += 1
            continue

        # we skip if curr user already has a TOTP authenticator (avoid duplicates)
        if Authenticator.objects.filter(user_id=user_id, type="totp").exists():
            skipped += 1
            continue

        Authenticator.objects.create(
            user_id=user_id,
            type="totp",
            data={"secret": secret_b32},
        )
        migrated += 1

    print(f"\n2FA migration: {migrated} TOTP secrets migrated, {skipped} skipped.")


class Migration(migrations.Migration):

    dependencies = [
        ("newsroom", "0049_alter_article_copyright"),
        ("mfa", "__first__"),
    ]

    operations = [
        migrations.RunPython(migrate_totp_secrets, migrations.RunPython.noop),
    ]
