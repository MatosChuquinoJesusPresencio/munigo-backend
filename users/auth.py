from django.contrib.auth.backends import BaseBackend

from users.models import Citizen


class DocumentBackend(BaseBackend):
    def authenticate(self, request, document_type=None, document_number=None, password=None, **kwargs):
        try:
            citizen = Citizen.objects.get(
                document_type=document_type,
                document_number=document_number,
            )
        except Citizen.DoesNotExist:
            return None

        user = citizen.user
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        from users.models import User
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
