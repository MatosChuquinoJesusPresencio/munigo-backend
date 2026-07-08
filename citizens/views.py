from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Citizen
from .serializers import CitizenSerializer


@api_view(['GET', 'PUT'])
def citizen_profile(request):
    try:
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        return Response(
            {"detail": "Perfil de ciudadano no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = CitizenSerializer(citizen)
        return Response(serializer.data)

    serializer = CitizenSerializer(citizen, data=request.data, partial=True, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
