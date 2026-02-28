import pathlib
from io import BytesIO

from django.conf import settings
from django.utils.translation import gettext as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Colors
OLIVE = colors.HexColor("#8B9A46")
DARK = colors.HexColor("#1a1a1a")
GRAY = colors.HexColor("#888888")
LIGHT_GRAY = colors.HexColor("#eeeeee")

_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    fonts_dir = pathlib.Path(settings.STATICFILES_DIRS[0]) / "deps" / "fonts"
    pdfmetrics.registerFont(
        TTFont("DejaVu", str(fonts_dir / "DejaVuSans.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("DejaVu-Bold", str(fonts_dir / "DejaVuSans-Bold.ttf"))
    )
    pdfmetrics.registerFontFamily(
        "DejaVu",
        normal="DejaVu",
        bold="DejaVu-Bold",
        italic="DejaVu",
        boldItalic="DejaVu-Bold",
    )
    _FONTS_REGISTERED = True


def _style(name, **kwargs):
    defaults = dict(fontName="DejaVu", fontSize=11, leading=14, textColor=DARK)
    defaults.update(kwargs)
    return ParagraphStyle(name, **defaults)


def generate_receipt_pdf(order) -> BytesIO:
    """Генерує PDF чек для замовлення. Повертає BytesIO."""
    _register_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    items = list(order.orderitem_set.all())
    payment = getattr(order, "payment", None)
    total = sum(item.products_price() for item in items)

    s_normal = _style("normal")
    s_bold = _style("bold", fontName="DejaVu-Bold")
    s_small = _style("small", fontSize=9, textColor=GRAY)

    elems = []

    # ── Header
    header_data = [
        [
            Paragraph(
                "<b>MILITARY</b>",
                _style(
                    "logo", fontName="DejaVu-Bold", fontSize=22, textColor=DARK
                ),
            ),
            Paragraph(
                f"<b>#{order.id}</b>",
                _style(
                    "num",
                    fontName="DejaVu-Bold",
                    fontSize=20,
                    textColor=OLIVE,
                    alignment=2,
                ),
            ),
        ],
        [
            Paragraph(
                _("ЧЕК / RECEIPT"),
                _style("sub", fontSize=9, textColor=GRAY, letterSpacing=3),
            ),
            Paragraph(
                order.created_timestamp.strftime("%d.%m.%Y"),
                _style("date", fontSize=9, textColor=GRAY, alignment=2),
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=["60%", "40%"])
    header_table.setStyle(
        TableStyle(
            [
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 1), (-1, 1), 1.5, OLIVE),
            ]
        )
    )
    elems.append(header_table)
    elems.append(Spacer(1, 0.4 * cm))

    # ── Info grid
    paid_at = (
        payment.paid_at.strftime("%d.%m.%Y %H:%M")
        if payment and payment.paid_at
        else "—"
    )
    payment_method = (
        _("При отриманні") if order.payment_on_get else _("Онлайн (Stripe)")
    )
    delivery = (
        order.delivery_address
        if order.requires_delivery and order.delivery_address
        else (
            _("Потрібна доставка")
            if order.requires_delivery
            else _("Самовивіз")
        )
    )
    customer = order.user.get_full_name() or order.user.username

    info_data = [
        [
            Paragraph(_("Замовлення:"), s_small),
            Paragraph(f"<b>#{order.id}</b>", s_bold),
            Paragraph(_("Клієнт:"), s_small),
            Paragraph(f"<b>{customer}</b>", s_bold),
        ],
        [
            Paragraph(_("Дата замовлення:"), s_small),
            Paragraph(
                f"<b>{order.created_timestamp.strftime('%d.%m.%Y %H:%M')}</b>",
                s_bold,
            ),
            Paragraph("Email:", s_small),
            Paragraph(f"<b>{order.email}</b>", s_bold),
        ],
        [
            Paragraph(_("Дата оплати:"), s_small),
            Paragraph(f"<b>{paid_at}</b>", s_bold),
            Paragraph(_("Телефон:"), s_small),
            Paragraph(f"<b>{order.phone_number}</b>", s_bold),
        ],
        [
            Paragraph(_("Спосіб оплати:"), s_small),
            Paragraph(f"<b>{payment_method}</b>", s_bold),
            Paragraph(_("Доставка:"), s_small),
            Paragraph(f"<b>{delivery}</b>", s_bold),
        ],
    ]
    info_table = Table(info_data, colWidths=["22%", "28%", "18%", "32%"])
    info_table.setStyle(
        TableStyle(
            [
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elems.append(info_table)
    elems.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=LIGHT_GRAY,
            spaceAfter=0.3 * cm,
            spaceBefore=0.3 * cm,
        )
    )

    # ── Items table
    s_th = _style(
        "th", fontName="DejaVu-Bold", fontSize=9, textColor=colors.white
    )
    s_th_c = _style(
        "th_c",
        fontName="DejaVu-Bold",
        fontSize=9,
        textColor=colors.white,
        alignment=1,
    )
    s_th_r = _style(
        "th_r",
        fontName="DejaVu-Bold",
        fontSize=9,
        textColor=colors.white,
        alignment=2,
    )
    s_td_c = _style("td_c", alignment=1)
    s_td_r = _style("td_r", alignment=2)
    s_total_label = _style(
        "tot_l", fontName="DejaVu-Bold", fontSize=12, alignment=2
    )
    s_total_val = _style(
        "tot_v",
        fontName="DejaVu-Bold",
        fontSize=12,
        textColor=OLIVE,
        alignment=2,
    )

    total_usd = sum(item.products_price_usd() for item in items)

    def price_cell(uah, usd):
        """Клітинка з ціною: UAH жирним, USD дрібніше знизу."""
        usd_line = (
            f'<br/><font size="8" color="#CC3333">${usd:.2f}</font>'
            if usd
            else ""
        )
        return Paragraph(f"{uah}{usd_line}", s_td_r)

    rows = [
        [
            Paragraph(_("Товар"), s_th),
            Paragraph(_("К-сть"), s_th_c),
            Paragraph(_("Ціна (грн.)"), s_th_r),
            Paragraph(_("Сума (грн.)"), s_th_r),
        ]
    ]
    for item in items:
        unit_usd = (
            item.products_price_usd() / item.quantity if item.quantity else 0
        )
        rows.append(
            [
                Paragraph(item.name, s_normal),
                Paragraph(str(item.quantity), s_td_c),
                price_cell(item.price, unit_usd),
                price_cell(item.products_price(), item.products_price_usd()),
            ]
        )
    rows.append(
        [
            Paragraph("", s_normal),
            Paragraph("", s_normal),
            Paragraph(_("РАЗОМ:"), s_total_label),
            Paragraph(
                f"{total} {_('грн.')}<br/><font size='10' "
                f"color='#CC3333'>${total_usd:.2f}</font>",
                s_total_val,
            ),
        ]
    )

    items_table = Table(rows, colWidths=["45%", "15%", "20%", "20%"])
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
                ("LINEBELOW", (0, 1), (-1, -2), 0.5, LIGHT_GRAY),
                ("LINEABOVE", (0, -1), (-1, -1), 1.5, OLIVE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elems.append(items_table)
    elems.append(Spacer(1, 0.6 * cm))

    # ── Paid stamp
    stamp_table = Table(
        [
            [
                Paragraph(
                    _("✓  ОПЛАЧЕНО"),
                    _style(
                        "stamp",
                        fontName="DejaVu-Bold",
                        fontSize=13,
                        textColor=OLIVE,
                        alignment=2,
                    ),
                )
            ]
        ],
        colWidths=["100%"],
    )
    stamp_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 2, OLIVE),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elems.append(
        Table(
            [[Paragraph("", s_normal), stamp_table]],
            colWidths=["55%", "45%"],
        )
    )
    elems.append(Spacer(1, 0.6 * cm))

    # ── Footer
    elems.append(
        HRFlowable(
            width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=0.2 * cm
        )
    )
    elems.append(
        Paragraph(
            _("MILITARY — Тактичне спорядження преміум класу"),
            _style("footer", fontSize=9, textColor=GRAY, alignment=1),
        )
    )
    elems.append(
        Paragraph(
            "© 2024 Nazarii Humen",
            _style("footer2", fontSize=8, textColor=GRAY, alignment=1),
        )
    )

    doc.build(elems)
    buffer.seek(0)
    return buffer


def send_receipt_email(order) -> None:
    """Відправляє PDF чек на email замовлення."""
    from django.core.mail import EmailMessage

    pdf_buffer = generate_receipt_pdf(order)

    subject = _("Ваш чек для замовлення #%(id)s") % {"id": order.id}
    body = _(
        "Дякуємо за ваше замовлення!\n\n"
        "Ваш чек додається до цього листа у форматі PDF.\n\n"
        "З повагою,\nMILITARY"
    )

    msg = EmailMessage(
        subject=subject,
        body=body,
        to=[order.email],
    )
    msg.attach(
        f"receipt_{order.id}.pdf",
        pdf_buffer.read(),
        "application/pdf",
    )
    msg.send(fail_silently=True)
