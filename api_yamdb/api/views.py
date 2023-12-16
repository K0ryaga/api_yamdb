from django.http import HttpResponse
from rest_framework import viewsets
from reviews.models import User
from rest_framework.permissions import IsAdminUser
from .serializers import UserSignupSerializer
from django.core.mail import send_mail
import string
import random


def code_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class UserSignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []
    allowed_methods = ['POST']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        confirmation_code = code_generator()
        if serializer.is_valid() is False:
            User(confirmation_code=confirmation_code).save
        else:
            serializer.save(confirmation_code=confirmation_code)

        send_mail(
            subject='Confirmation code',
            message=f'Your confirmation code is {confirmation_code}',
            from_email='from@example.com',
            recipient_list=[request.data.get('email')],
            fail_silently=True,
        )
        return HttpResponse("На почту был отправлен код подтверждения")


class UserSignupByAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    allowed_methods = ['POST']
    permission_classes = (IsAdminUser,)
