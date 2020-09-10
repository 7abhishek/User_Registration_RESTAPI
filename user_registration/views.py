import hashlib

from django.shortcuts import render
from rest_framework import viewsets
from .models import User, Verification, Login
from .serializers import UserSerializer, VerificationSerializer, LoginSerializer

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .sms import send_sms
import logging
import crypt
logger = logging.getLogger(__name__)

#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

''''
class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
'''


@csrf_exempt
def register(request):
    logger.error('register called....')
    print("register called....", flush=True)
    if request.method == 'POST':
        data = JSONParser().parse(request)
        password_hash = hashlib.sha224(str.encode(data['password'])).hexdigest() #encyption using sha224
        data['password'] = password_hash
        print("len of password", len(data['password']))
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            saved_user = serializer.data
            print("saved_user: {}".format(saved_user), flush=True)
            send_sms(saved_user)
            return JsonResponse(saved_user, status=202)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def verify(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = VerificationSerializer(data=data)
        if serializer.is_valid():
            logger.error('serializer is valid {}'.format(data))
            db_user = User.objects.get(id=data['user_id'])
            print("db_user {}".format(db_user))
            logger.error("db_user {}".format(db_user))
            logger.error("res3 {}".format(Verification.objects.all()))
            try:
                verification = Verification.objects.filter(user=db_user)
                logger.error('verification is', verification)
                if verification is not None and len(verification) == 1:
                    db_user.is_verified = True
                    db_user.save()
                    return JsonResponse({}, status=200)
                else:
                    return JsonResponse({"msg": "invalid otp"}, status=400)
            except Verification.DoesNotExist:
                logger.error('verification object doesnt exist....')
        return JsonResponse({"msg": "Doesnt exist"}, status=404)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def login(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        password_hash = hashlib.sha224(str.encode(data['password'])).hexdigest()
        serializer = LoginSerializer(data=data)
        logger.error('data {}'.format(data))
        logger.error(password_hash)
        if serializer.is_valid():
            logger.error('is valid....')
            db_user = User.objects.filter(email=data['email'], password=password_hash, is_verified=True)
            logger.error('db_user {} len {}'.format(db_user, len(db_user)))
            if db_user is not None and len(db_user) >= 1:
                return JsonResponse({"msg": "success"}, status=200)
            return JsonResponse({}, status=404)
        return JsonResponse(serializer.error, status=400)
    return JsonResponse({}, status=404)
