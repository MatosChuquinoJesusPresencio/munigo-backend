from datetime import datetime, timedelta, date

from django.db.models import Count, Q, F, Avg, Exists, DurationField, ExpressionWrapper, OuterRef, Subquery
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from records.models import Record, RecordStatus, RiskLevel
from users.models import User, Role
from employees.models import Employee
from inspections.models import Inspection, InspectionResult
from appointments.models import Appointment, AppointmentStatus
from .serializers import (
    StatsSerializer, AvgTimeSerializer, RiskDistributionSerializer,
    OfficerSerializer, SlowRecordSerializer, ExpiryAlertsSerializer,
    SummarySerializer,
)


def _check_role(request, roles):
    if request.user.role not in roles:
        return False
    return True


@api_view(['GET'])
def general_stats(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    total = Record.objects.count()
    by_status = {}
    for s in RecordStatus.values:
        by_status[s] = Record.objects.filter(status=s).count()

    completed = Record.objects.filter(status__in=[RecordStatus.APPROVED, RecordStatus.REJECTED]).count()
    approved = Record.objects.filter(status=RecordStatus.APPROVED).count()
    approval_rate = round((approved / completed * 100) if completed > 0 else 0, 1)

    now = timezone.now()
    new_this_month = Record.objects.filter(
        created_at__year=now.year, created_at__month=now.month
    ).count()

    total_citizens = User.objects.filter(role=Role.CITIZEN).count()
    total_inspectors = User.objects.filter(role=Role.INSPECTOR).count()
    total_officials = User.objects.filter(role=Role.OFFICIAL).count()

    return Response(StatsSerializer({
        'total': total,
        'by_status': by_status,
        'approval_rate': approval_rate,
        'new_this_month': new_this_month,
        'total_citizens': total_citizens,
        'total_inspectors': total_inspectors,
        'total_officials': total_officials,
    }).data)


@api_view(['GET'])
def avg_time(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    exec_date_subquery = Subquery(
        Inspection.objects.filter(
            record=OuterRef('pk'),
            result=InspectionResult.APPROVED,
            execution_date__isnull=False,
        ).values('execution_date')[:1]
    )

    has_approved_inspection = Exists(
        Inspection.objects.filter(
            record=OuterRef('pk'),
            result=InspectionResult.APPROVED,
            execution_date__isnull=False,
        )
    )

    approved = Record.objects.filter(
        Q(status=RecordStatus.APPROVED) & has_approved_inspection,
    ).annotate(
        days=ExpressionWrapper(
            exec_date_subquery - F('created_at'),
            output_field=DurationField(),
        )
    )

    overall = approved.aggregate(avg=Avg('days'))
    overall_avg_days = round(overall['avg'].total_seconds() / 86400, 1) if overall['avg'] else 0

    by_procedure = []
    for pt in Record.objects.values_list('procedure_type', flat=True).distinct():
        qs = approved.filter(procedure_type=pt)
        agg = qs.aggregate(avg=Avg('days'))
        days = round(agg['avg'].total_seconds() / 86400, 1) if agg['avg'] else 0
        by_procedure.append({'type': pt, 'avg_days': days})

    by_risk = []
    for rl in RiskLevel.values:
        qs = approved.filter(risk_level=rl)
        agg = qs.aggregate(avg=Avg('days'))
        days = round(agg['avg'].total_seconds() / 86400, 1) if agg['avg'] else 0
        by_risk.append({'type': rl, 'avg_days': days})

    return Response(AvgTimeSerializer({
        'overall_avg_days': overall_avg_days,
        'by_procedure_type': by_procedure,
        'by_risk_level': by_risk,
    }).data)


@api_view(['GET'])
def risk_distribution(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    total = Record.objects.count()
    risk_map = {
        RiskLevel.LOW: 'low',
        RiskLevel.MEDIUM: 'medium',
        RiskLevel.HIGH: 'high',
    }
    result = {}
    for db_val, key in risk_map.items():
        count = Record.objects.filter(risk_level=db_val).count()
        pct = round((count / total * 100), 1) if total > 0 else 0
        result[key] = {'count': count, 'percentage': pct}

    return Response(RiskDistributionSerializer({
        **result,
        'total': total,
    }).data)


@api_view(['GET'])
def officer_performance(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    employees = Employee.objects.filter(user__role__in=[Role.INSPECTOR, Role.OFFICIAL])

    data = []
    for emp in employees:
        inspections = Inspection.objects.filter(inspector=emp)
        total_assign = inspections.count()
        completed = inspections.filter(result__in=[InspectionResult.APPROVED, InspectionResult.NOT_APPROVED]).count()
        approved = inspections.filter(result=InspectionResult.APPROVED).count()
        rate = round((approved / completed * 100), 1) if completed > 0 else 0

        data.append({
            'id': emp.id,
            'name': f"{emp.first_name} {emp.last_name}",
            'position': emp.position,
            'area': emp.area,
            'inspections_assigned': total_assign,
            'inspections_completed': completed,
            'approval_rate': rate,
        })

    data.sort(key=lambda x: x['inspections_completed'], reverse=True)
    return Response(OfficerSerializer(data, many=True).data)


@api_view(['GET'])
def slow_records(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    limit = int(request.query_params.get('limit', 10))
    now = timezone.now()

    pending_statuses = [
        RecordStatus.PENDING_REVIEW, RecordStatus.PENDING_INSPECTION,
        RecordStatus.OBSERVED, RecordStatus.DOCUMENTS_APPROVED,
    ]

    records = Record.objects.filter(status__in=pending_statuses).annotate(
        days_in_state=ExpressionWrapper(
            now - F('created_at'),
            output_field=DurationField(),
        )
    ).order_by('-days_in_state')[:limit]

    data = []
    for r in records:
        data.append({
            'id': r.id,
            'tracking_code': r.tracking_code,
            'citizen': r.citizen.legal_name,
            'status': r.status,
            'risk_level': r.risk_level,
            'procedure_type': r.procedure_type,
            'days_in_state': r.days_in_state.days if r.days_in_state else 0,
            'created_at': r.created_at,
        })

    return Response(SlowRecordSerializer(data, many=True).data)


@api_view(['GET'])
def expiry_alerts(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    threshold_days = int(request.query_params.get('threshold', 15))
    now = timezone.now()

    pending_statuses = [
        RecordStatus.PENDING_REVIEW, RecordStatus.PENDING_INSPECTION,
        RecordStatus.OBSERVED, RecordStatus.DOCUMENTS_APPROVED,
    ]

    records = Record.objects.filter(status__in=pending_statuses).annotate(
        days_passed=ExpressionWrapper(
            now - F('created_at'),
            output_field=DurationField(),
        )
    ).filter(days_passed__gte=timedelta(days=1))

    expired = []
    expiring_soon = []

    for r in records:
        days = r.days_passed.days if r.days_passed else 0
        item = {
            'id': r.id,
            'tracking_code': r.tracking_code,
            'citizen': r.citizen.legal_name,
            'status': r.status,
            'days_passed': days,
        }
        if days >= threshold_days:
            expired.append(item)
        else:
            expiring_soon.append(item)

    expired.sort(key=lambda x: x['days_passed'], reverse=True)
    expiring_soon.sort(key=lambda x: x['days_passed'], reverse=True)

    return Response(ExpiryAlertsSerializer({
        'expired': expired,
        'expiring_soon': expiring_soon,
        'total_expired': len(expired),
        'total_expiring_soon': len(expiring_soon),
    }).data)


@api_view(['GET'])
def summary(request):
    if not _check_role(request, ('FUNCIONARIO', 'GERENTE', 'INSPECTOR')):
        return Response({"detail": "No tiene permisos"}, status=status.HTTP_403_FORBIDDEN)

    now = timezone.now()
    today = date.today()

    pending_review = Record.objects.filter(status=RecordStatus.PENDING_REVIEW).count()
    pending_inspection = Record.objects.filter(status=RecordStatus.PENDING_INSPECTION).count()
    observed = Record.objects.filter(status=RecordStatus.OBSERVED).count()
    approved_this_month = Record.objects.filter(
        status=RecordStatus.APPROVED,
        created_at__year=now.year,
        created_at__month=now.month,
    ).count()

    upcoming_appointments = Appointment.objects.filter(
        date__gte=today,
        status=AppointmentStatus.SCHEDULED,
    ).count()

    pending_inspections_today = Inspection.objects.filter(
        scheduled_date__date=today,
        result=InspectionResult.PENDING,
    ).count()

    return Response(SummarySerializer({
        'pending_review': pending_review,
        'pending_inspection': pending_inspection,
        'observed': observed,
        'approved_this_month': approved_this_month,
        'upcoming_appointments': upcoming_appointments,
        'pending_inspections_today': pending_inspections_today,
    }).data)
