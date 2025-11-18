from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializer import RegisterSerializer, UserSerializer


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
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data["id"])
        refresh = RefreshToken.for_user(user)
        response.data["refresh"] = str(refresh)
        response.data["access"] = str(refresh.access_token)
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
        # elimina la cuenta del usuario autenticado
        user = request.user
        user.delete()
        return Response(
            {"detail": "Cuenta eliminada correctamente."}, status=204)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Usuario y contraseña son obligatorios."}, status=400
            )

        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return Response({"detail": "Credenciales inválidas."}, status=401)

        if not user.is_active:
            return Response(
                {"detail": "Usuario inactivo. Contacta al administrador."}, status=403
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_staff": user.is_staff,
                },
            },
            status=200,
        )
