from .models import Notification


def create_notification(citizen, type, message, record=None):
    return Notification.objects.create(
        citizen=citizen,
        record=record,
        type=type,
        message=message,
    )


def notificar_expediente_enviado(citizen, record):
    mensaje = f"Tu expediente {record.tracking_code} ha sido enviado a revisión."
    create_notification(citizen, "EXPEDIENTE_ENVIADO", mensaje, record)


def notificar_documento_observado(citizen, nombre_documento, observaciones, record=None):
    mensaje = f"El documento '{nombre_documento}' tiene observaciones: {observaciones}"
    create_notification(citizen, "DOCUMENTO_OBSERVADO", mensaje, record)


def notificar_expediente_observado(citizen, record):
    mensaje = f"Tu expediente {record.tracking_code} ha sido observado. Por favor revisa los documentos."
    create_notification(citizen, "EXPEDIENTE_OBSERVADO", mensaje, record)


def notificar_expediente_aprobado(citizen, record):
    mensaje = f"¡Felicidades! Tu expediente {record.tracking_code} ha sido aprobado."
    create_notification(citizen, "EXPEDIENTE_APROBADO", mensaje, record)


def notificar_expediente_rechazado(citizen, record, motivo):
    mensaje = f"Tu expediente {record.tracking_code} ha sido rechazado. Motivo: {motivo}"
    create_notification(citizen, "EXPEDIENTE_RECHAZADO", mensaje, record)


def notificar_cita_programada(citizen, fecha, hora, record=None):
    mensaje = f"Tienes una cita programada para el {fecha} a las {hora}."
    create_notification(citizen, "CITA_PROGRAMADA", mensaje, record)


def notificar_cita_cancelada(citizen, fecha, hora, record=None):
    mensaje = f"Tu cita del {fecha} a las {hora} ha sido cancelada."
    create_notification(citizen, "CITA_CANCELADA", mensaje, record)
