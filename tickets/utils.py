import qrcode
import os
from django.conf import settings


def generate_qr_code(ticket_code, ticket_id):
    """
    Generate a QR code image for a ticket.
    QR contains the ticket_code for validation.
    Saves to media/qrcodes/ folder.
    Returns the relative file path.
    """

    # ── Data encoded in QR ───────────────────────────────────
    qr_data = f"EVENTIFY-TICKET:{ticket_code}"

    # ── QR Code settings ─────────────────────────────────────
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # ── Generate image ───────────────────────────────────────
    img = qr.make_image(
        fill_color="#1F3864",   # navy blue
        back_color="white"
    )

    # ── Save to media folder ─────────────────────────────────
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)

    filename  = f"ticket_{ticket_id}_{ticket_code}.png"
    file_path = os.path.join(qr_dir, filename)
    img.save(file_path)

    return f"qrcodes/{filename}"