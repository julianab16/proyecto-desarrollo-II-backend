from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializer import RegisterSerializer, UserSerializer
import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Solo admins

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.ADMINISTRADOR:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
        except Exception as e:
            errors = None
            try:
                serializer = self.get_serializer(data={k: v for k, v in request.data.items() if k != 'password'})
                serializer.is_valid(raise_exception=False)
                errors = serializer.errors
            except Exception:
                errors = None
            logger.warning(
                "Register failed. username=%s email=%s errors=%s exception=%s",
                request.data.get('username'), request.data.get('email'), errors, str(e)
            )
            raise
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        # Elimina la cuenta del usuario autenticado
        user = request.user
        user.delete()
        return Response(
            {"detail": "Cuenta eliminada correctamente."}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            # No loggeamos la contraseña. Registramos que faltan credenciales y las claves recibidas.
            logger.warning("Login failed - missing credentials. data_keys=%s", list(request.data.keys()))
            return Response(
                {"detail": "Usuario y contraseña son obligatorios."}, status=400
            )

        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            logger.info("Login failed - invalid credentials for username=%s", username)
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=401
            )

        if not user.is_active:
            logger.warning("Login failed - inactive user username=%s id=%s", username, user.id)
            return Response(
                {"detail": "Usuario inactivo. Contacta al administrador."}, status=403
            )

        refresh = RefreshToken.for_user(user)
        logger.info("User login successful username=%s id=%s", username, user.id)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_staff': user.is_staff
             }
        }, status=200)
