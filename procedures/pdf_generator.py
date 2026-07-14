import io
from datetime import timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from django.utils import timezone


def generate_license_pdf(case_file) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'LicenseTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=2 * mm,
        textColor=colors.HexColor('#0B508C'),
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'LicenseSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=1 * mm,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        textColor=colors.HexColor('#0B508C'),
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#555555'),
    )

    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1C1C1E'),
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER,
    )

    elements = []

    elements.append(Paragraph("MUNICIPALIDAD DE LOS OLIVOS", title_style))
    elements.append(Paragraph("Area de Desarrollo Economico", subtitle_style))
    elements.append(Paragraph("Subgerencia de Comercializacion", subtitle_style))

    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0B508C')))
    elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph("LICENCIA DE FUNCIONAMIENTO", title_style))
    elements.append(Paragraph(f"N° {case_file.tracking_code}", subtitle_style))

    elements.append(Spacer(1, 4 * mm))

    establishment = case_file.establishment
    company = establishment.company
    citizen = case_file.citizen
    user = citizen.user

    def _field(label, value):
        return [
            Paragraph(label, label_style),
            Paragraph(str(value), value_style),
        ]

    data_titular = [
        _field("Titular:", f"{user.first_name} {user.last_name}"),
        _field("Documento:", f"{citizen.document_type} {citizen.document_number}"),
    ]

    table_titular = Table(data_titular, colWidths=[3.5 * cm, 13 * cm])
    table_titular.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("DATOS DEL TITULAR", section_title_style))
    elements.append(table_titular)

    data_empresa = [
        _field("Empresa:", company.business_name),
        _field("RUC:", company.ruc),
        _field("Establecimiento:", establishment.name),
        _field("Direccion:", establishment.address),
        _field("Categoria:", establishment.get_business_category_display()),
        _field("Superficie:", f"{establishment.square_meters} m²"),
    ]

    table_empresa = Table(data_empresa, colWidths=[3.5 * cm, 13 * cm])
    table_empresa.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("DATOS DEL ESTABLECIMIENTO", section_title_style))
    elements.append(table_empresa)

    approval_date = timezone.now()

    vigencia_inicio = approval_date.strftime('%d/%m/%Y')
    vigencia_fin = (approval_date + timedelta(days=365)).strftime('%d/%m/%Y')

    data_tramite = [
        _field("Codigo de seguimiento:", case_file.tracking_code),
        _field("Tipo de tramite:", case_file.get_procedure_type_display()),
        _field("Nivel de riesgo:", case_file.get_risk_level_display()),
        _field("Fecha de aprobacion:", vigencia_inicio),
        _field("Vigencia:", f"{vigencia_inicio} al {vigencia_fin}"),
    ]

    table_tramite = Table(data_tramite, colWidths=[3.5 * cm, 13 * cm])
    table_tramite.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("DATOS DE LA LICENCIA", section_title_style))
    elements.append(table_tramite)

    elements.append(Spacer(1, 15 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC')))
    elements.append(Spacer(1, 10 * mm))

    signature_data = [
        [
            Paragraph("_________________________", ParagraphStyle('SigLine', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)),
            '',
            Paragraph("_________________________", ParagraphStyle('SigLine', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)),
        ],
        [
            Paragraph("Gerente de Administracion", ParagraphStyle('SigLabel', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#555555'))),
            '',
            Paragraph("Subgerente de Comercializacion", ParagraphStyle('SigLabel', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#555555'))),
        ],
    ]

    sig_table = Table(signature_data, colWidths=[7 * cm, 2 * cm, 7 * cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)

    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(
        f"Documento generado el {timezone.now().strftime('%d/%m/%Y %H:%M')} - Sistema MuniGO",
        footer_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
