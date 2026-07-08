from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role
from citizens.models import Citizen
from employees.models import Employee
from records.models import ProcedureType
from requirements.models import Requirement

User = get_user_model()

REQUISITOS_DATA = [
    # Licencia de Funcionamiento
    {"nombre": "DNI del Representante Legal", "descripcion": "Documento Nacional de Identidad del representante legal del establecimiento", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    {"nombre": "RUC (Persona Jurídica)", "descripcion": "Registro Único de Contribuyente (si aplica para persona jurídica)", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": False},
    {"nombre": "Declaración Jurada de No Infraestructura", "descripcion": "Declaración jurada que acredita que el local no requiere ITSE", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    {"nombre": "Croquis de Ubicación", "descripcion": "Plano o croquis que indica la ubicación exacta del establecimiento", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    {"nombre": "Plano de Distribución Interior", "descripcion": "Plano arquitectónico de la distribución interior del local", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    {"nombre": "Certificado de Propiedad o Contrato de Alquiler", "descripcion": "Documento que acredita la propiedad o posesión del local", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    {"nombre": "ITSE (si aplica)", "descripcion": "Inspección Técnica de Seguridad Estructural (si el local lo requiere)", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": False},
    {"nombre": "Pago de Derechos Municipales", "descripcion": "Comprobante de pago de los derechos municipales correspondientes", "aplica_a": ProcedureType.OPERATING_LICENSE, "es_obligatorio": True},
    # ITSE
    {"nombre": "DNI del Propietario", "descripcion": "Documento Nacional de Identidad del propietario del inmueble", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
    {"nombre": "Plano Arquitectónico", "descripcion": "Planos arquitectónicos aprobados del inmueble", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
    {"nombre": "Plano Estructural", "descripcion": "Planos estructurales con cálculos de ingeniería", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
    {"nombre": "Certificado de Suelos", "descripcion": "Estudio de mecánica de suelos del terreno", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
    {"nombre": "Memoria Descriptiva", "descripcion": "Memoria descriptiva y de cálculo estructural", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
    {"nombre": "Pago de Derechos ITSE", "descripcion": "Comprobante de pago de los derechos por Inspección Técnica", "aplica_a": ProcedureType.ITSE, "es_obligatorio": True},
]


class Command(BaseCommand):
    help = "Carga datos iniciales: requisitos, admin y empleados"

    def handle(self, *args, **options):
        self._seed_requisitos()
        self._seed_admin()
        self.stdout.write(self.style.SUCCESS("Datos cargados exitosamente"))

    def _seed_requisitos(self):
        created = 0
        for data in REQUISITOS_DATA:
            _, created_flag = Requirement.objects.get_or_create(
                name=data["nombre"],
                defaults={
                    "description": data["descripcion"],
                    "is_mandatory": data["es_obligatorio"],
                    "applies_to": data["aplica_a"],
                },
            )
            if created_flag:
                created += 1

        self.stdout.write(f"  Requisitos: {created} creados, {len(REQUISITOS_DATA) - created} ya existían")

    def _seed_admin(self):
        admin_email = "admin@munigo.com"
        user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                "username": admin_email,
                "role": Role.MANAGER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("admin123")
            user.save()

            Employee.objects.create(
                user=user,
                first_name="Administrador",
                last_name="Sistema",
                position="gerente",
                area="Gerencia General",
            )

            self.stdout.write(f"  Admin creado: {admin_email} / admin123")
        else:
            self.stdout.write(f"  Admin ya existía: {admin_email}")
