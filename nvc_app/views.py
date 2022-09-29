from functools import partial
import json
from multiprocessing import context
import re
from socketserver import UDPServer
from urllib import response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from nvc_app import serializers
from nvc_app.serializers import SendPasswordResetEmailSerializer, TicketSerializer, UserLoginSerializer, UserRegistrationSerializer , UserPasswordResetSerializer , CloseTicketDetailSerializer,UserChangePasswordSerializer, UserSerializer , FcmTokenSaveSerializer
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import TicketModel, User, ZoneModel
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser,FormParser
from .utils import SendEmail, Util
from rest_framework import status
import requests
from rest_framework import generics


# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    status_code = status.HTTP_201_CREATED
    #token = get_tokens_for_user(user)
    response={
      "success":True
,     "message":"User Registration Successfull",
      "status":status_code
    }
    return Response(response, status=status.HTTP_201_CREATED)

def save_fcm(fcm,email):
  user = User.objects.filter(email=email).update(fcm_token=fcm)
  serializer = FcmTokenSaveSerializer(data=user)
  if serializer.is_valid():
    serializer.save()
  

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    fcm = serializer.data.get('fcm_token')   
    user = authenticate(email=email, password=password)
    if user is not None:
      save_fcm(fcm,email)
      
      token = get_tokens_for_user(user)
      response = {
        "email": serializer.data.get('email'),
        "name":user.user_name,
        "company_name":user.user_company_name,
        "user_zip_code":user.user_zip_code,
        "is_active":user.is_active,
        "is_admin":user.is_admin

      }
      
      return Response({'token':token,"user_details":response, 'msg':'Login Success',"status":status.HTTP_200_OK})
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class EmailPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self,request,*args,**kwargs):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    if serializer.is_valid():
      print(serializer.data)
      email = serializer.data.get('email')
      return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
  renderer_classes = [UserRenderer]
  def post(self,request,*args,uid,token,**kwargs):
    serializer = UserPasswordResetSerializer(data = request.data,context={"uid":uid,"token":token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Done'}, status=status.HTTP_200_OK)



class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def post(self,request,*args,format=None,**kwargs):
    serializer = UserChangePasswordSerializer(data=request.data,context={"user":request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Your password changed successfully.'}, status=status.HTTP_200_OK)

def send_notification(registration_ids , message_title , message_desc):
        print('Registratin_ids----',registration_ids)
        print('message_title----',message_title)
        print('message_desc----',message_desc)
        fcm_api="AAAAmwTQgrc:APA91bHFSCdbj51sAdbCoBRdU44J05H6VBXd_P03RilujZnSBYZGvRCVeR-yAbFhV5w8EgdiNHE4wp0cEdEM14_saX_DMyC7yovT2ODCRUR9r72UCxfNz62duw7hcKyhC0gZ5tM9v2P1"
        url = "https://fcm.googleapis.com/fcm/send"
        
        headers = {
        "Content-Type":"application/json",
        "Authorization": 'key='+fcm_api}
        payload = {
            "registration_ids" :registration_ids,
            "priority" : "high",
            "notification" : {
                "body" : message_desc,
                "title" : message_title,
                
            },
            
        }
    
        result = requests.post(url,  data=json.dumps(payload), headers=headers )
        



class CreateTicket(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def post(self,request,*args,**kwargs):
    serializer = TicketSerializer(data=request.data)
    
    if serializer.is_valid():
    #try:
      ticket_email = serializer.validated_data.get('ticket_email')
      print(ticket_email)
      user_pin = User.objects.get(email=ticket_email).user_zip_code
      print(user_pin)
      url = 'https://api.postalpincode.in/pincode/{}'.format(user_pin)
      data = requests.get(url)
      info = json.loads(data.text)
      district_of_user = info[0]['PostOffice'][0]['District']
      user_zone = ZoneModel.objects.get(zone_name=district_of_user).id
      print(user_zone)
      user_email = User.objects.filter(user_zone_name=user_zone)
      print(user_email)
      zone_email_list = []
      for email in user_email:
        zone_email_list.append(email.email)
      
      #for zone
      serializer.save()
      user = User.objects.get(email=request.user)
      body = "Please review this ticket which is created by"
      data = {
        'subject':'Customer Created  Ticket',
        'body':body,
        'to_email':zone_email_list
      }
      SendEmail.send(data)
      user = User.objects.filter(user_city=district_of_user)
      token = []
      for fcm in user:
        token.append(fcm.fcm_token)
              
      resgistration = token    
      print(resgistration)
      send_notification(resgistration, 'hi this is push notification' , 'PUSH NOTIFICATION')
      return Response({'msg':'Ticket created successfully.'}, status=status.HTTP_201_CREATED)
    #except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)
  
    return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)
  


class UpdateTicketStatus(APIView):
  def patch(self,request,pk):
    try:
      ticket = TicketModel.objects.get(ticket_id=pk)
      serializer = TicketSerializer(ticket,data=request.data,partial=True)
      if serializer.is_valid():
        serializer.save()
        return Response({"msg":"Ticket Updated Successfully","status":status.HTTP_200_OK})
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def get(self,request):
    try:
      user = User.objects.filter(id=request.user.id)
      serializer = UserSerializer(user,many=True)
      return Response({"data":serializer.data,"status":status.HTTP_200_OK})
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)


class AllTickets(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def get(self,request):
    try:
      ticket_data = TicketModel.objects.all()
      serializer = TicketSerializer(ticket_data,many=True)
      return Response({"data":serializer.data,"status":status.HTTP_200_OK})
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)


class TicketCreatedByUser(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def get(self,request):
    try:
      ticket_data = TicketModel.objects.filter(ticket_email=request.user.email)
      serializer = TicketSerializer(ticket_data,many=True)
      return Response({"data":serializer.data,"status":status.HTTP_200_OK})
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)

class OnCallView(APIView):
  def get(self,request):
    try:
      on_call_tickets = TicketModel.objects.filter(on_call_ticket=True)
      serializer = TicketSerializer(on_call_tickets,many=True)
      return Response(serializer.data)
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)

class ClosedTicketView(APIView):
  def get(self,request):
    try:
      closed_tickets = TicketModel.objects.filter(closed_ticket=True)
      serializer = TicketSerializer(closed_tickets,many=True)
      return Response({"data":serializer.data,"status":status.HTTP_200_OK})
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)

class VisitAndClosedView(APIView):
  def get(self,request):
    try:
      visit_and_closed_tickets = TicketModel.objects.filter(visit_and_closed=True)
      serializer = TicketSerializer(visit_and_closed_tickets,many=True)
      return Response({"data":serializer.data,"status":status.HTTP_200_OK})
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfile(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def get(self,request,pk=None):
    try:
      if pk!=None:
        user = User.objects.filter(id=pk)
        serializer = UserSerializer(user,many=True)
        return Response(serializer.data)
      else:
        user = User.objects.filter(id=request.user.id)
        serializer = UserSerializer(user,many=True)
        return Response(serializer.data)
    except:
      return Response({'message':"Something wents wrong"},status=status.HTTP_400_BAD_REQUEST)


class CloseTicketDetails(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def get(self,request,pk):
    try:
      print(request.user.is_admin)
      ticket_detail = TicketModel.objects.get(ticket_id=pk)
      serializer = CloseTicketDetailSerializer(ticket_detail)
      return Response(serializer.data)
    except:
      return Response({'msg':'Something wents wrong.'}, status=status.HTTP_400_BAD_REQUEST)

class CloseTicket(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated,]
  def post(self,request,pk):
    ticket_detail = TicketModel.objects.filter(ticket_id=pk).update(closed_ticket=True,on_call_ticket=False,visit_and_closed=False,visit_scheduled=False,waiting_for_spares=False,pending=False,ready=False,during_engg_visit=False,not_understood_list=False,further_tech_guidence_needed=False)
    serializer = TicketSerializer(data=ticket_detail)
    if serializer.is_valid():
      serializer.save()
      if request.user.is_admin==False:
        return Response({"msg":'Ticket Closed Successfully',"status":status.HTTP_200_OK})
      else:
        pass
    return Response({'message':"Something wents wrong","status":status.HTTP_400_BAD_REQUEST})
    
    
class Review(APIView):
  def patch(self,request,pk):
    ticket = TicketModel.objects.get(ticket_id=pk)
    serializer = TicketSerializer(ticket,data=request.data,partial=True)
    try:
      if serializer.is_valid():
        serializer.save()
        return Response({"msg":'Thank You,Your Review saved successfully',"status":status.HTTP_200_OK})
      return Response({'message':"Something wents wrong","status":status.HTTP_400_BAD_REQUEST})
    except :
      return Response({'message':"Something wents wrong","status":status.HTTP_400_BAD_REQUEST})





  


  
