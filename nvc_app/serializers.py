from cmath import isnan
from dataclasses import field
from multiprocessing import context
from urllib import request
from xml.dom import ValidationErr
from rest_framework import serializers
from nvc_app.models import Photo, TicketModel, User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
  # We are writing this becoz we need confirm password field in our Registratin Request
  password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
  class Meta:
    model = User
    fields=['email', 'user_name', 'password', 'password2', 'user_city','user_zip_code','user_company_name']
    extra_kwargs={
      'password':{'write_only':True}
    }

  # Validating Password and Confirm Password while Registration
  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    return attrs

  def create(self, validate_data):
    return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  
  class Meta:
    model = User
    fields = ['email', 'password','fcm_token']


class FcmTokenSaveSerializer(serializers.Serializer):
  class Meta:
    model = User
    fields = ['email', 'password','fcm_token']

    def update(self,instance,validated_data):
      instance.email = validated_data.get("email",instance.email)
      instance.password = validated_data.get("password",instance.password)
      instance.fcm_token = validated_data.get("fcm_token",instance.fcm_token)
      instance.save()
      return instance



class UserChangePasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    user = self.context.get('user')
   
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user.set_password(password)
    user.save()
    return attrs

  

class SendPasswordResetEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, attrs):
    email = attrs.get('email')
    print('--------EMail',email)
    if User.objects.filter(email=email).exists():
      user = User.objects.get(email = email)
      print('----------------User inside if',user)
      uid = urlsafe_base64_encode(force_bytes(user.id))
      print('Encoded UID', uid)
      token = PasswordResetTokenGenerator().make_token(user)
      print('Password Reset Token', token)
      link = 'http://localhost:8000/reset_password/'+uid+'/'+token
      print('Password Reset Link', link)
      # Send EMail
      body = 'Click Following Link to Reset Your Password '+link
      data = {
        'subject':'Reset Your Password',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)
      return attrs
    else:
      raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
  new_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['new_password', 'confirm_password']

  def validate(self, attrs):
    try:
      password = attrs.get('new_password')
      password2 = attrs.get('confirm_password')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != password2:
        raise serializers.ValidationError("new_password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = User.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')


    # fields = ('query_type','ticket_creator_name','ticket_email','ticket_creator_address','equipment_name','equipment_sr_no','equipment_model_no','problem_description','production_temprorary_running','running_with_rejection','production_breakdown','sales_production_name','process_mc_type','max_kg_or_hrs','material_denticty','virgin','regrind','falkes','master_batch','additives_1','additives_2','work_order_no','packing_slip_no','receive_in_good_condition','equipment_description','production_trial_readliness_date','pending','ready','during_engg_visit','not_understood_list','further_tech_guidence_needed','spare_name','spare_sr_no','spare_model_name','part_name','part_description','part_quantity','closed_ticket','on_call_ticket','visit_and_closed','visit_scheduled','waiting_for_spares')

 
class TicketSerializer (serializers.ModelSerializer ) :
    attach_file = serializers.ListField(child=serializers.FileField( max_length=100000, allow_empty_file=False,use_url=False ))
    class Meta:
      model = TicketModel
      fields = '__all__'
    def create(self, validated_data):
        attached_files = validated_data.pop('attach_file')
        for file in attached_files:
            files=TicketModel.objects.create(attach_file=file,**validated_data)
        return files

    def update(self,instance,validated_data):
      instance.ticket_id = validated_data.get("ticket_id",instance.ticket_id)
      instance.query_type = validated_data.get('query_type',instance.query_type)
      instance.ticket_email = validated_data.get('ticket_email',instance.ticket_email)
      instance.ticket_number = validated_data.get('ticket_number',instance.ticket_number)
      instance.ticket_creator_name = validated_data.get('ticket_creator_name',instance.ticket_creator_name)
      instance.ticket_creator_address = validated_data.get('ticket_creator_address',instance.ticket_creator_address)
      instance.equipment_name = validated_data.get('equipment_name',instance.equipment_name)
      instance.equipment_sr_no = validated_data.get('equipment_sr_no',instance.equipment_sr_no)
      instance.equipment_model_no = validated_data.get('equipment_model_no',instance.equipment_model_no)
      instance.problem_description = validated_data.get('problem_description',instance.problem_description)
      instance.production_temprorary_running = validated_data.get('production_temprorary_running',instance.production_temprorary_running)
      instance.running_with_rejection = validated_data.get('running_with_rejection',instance.running_with_rejection)
      instance.production_breakdown = validated_data.get('production_breakdown',instance.production_breakdown)
      instance.sales_production_name = validated_data.get('sales_production_name',instance.sales_production_name)
      instance.process_mc_type = validated_data.get('process_mc_type',instance.process_mc_type)
      instance.max_kg_or_hrs = validated_data.get('max_kg_or_hrs',instance.max_kg_or_hrs)
      instance.material_denticty = validated_data.get('material_denticty',instance.material_denticty)
      instance.virgin = validated_data.get('virgin',instance.virgin)
      instance.regrind = validated_data.get('regrind',instance.regrind)
      instance.falkes = validated_data.get('falkes',instance.falkes)
      instance.master_batch = validated_data.get('master_batch',instance.master_batch)
      instance.additives_1 = validated_data.get('additives_1',instance.additives_1)
      instance.additives_2 = validated_data.get('additives_2',instance.additives_2)
      instance.work_order_no = validated_data.get('work_order_no',instance.work_order_no)
      instance.packing_slip_no = validated_data.get('packing_slip_no',instance.packing_slip_no)
      instance.receive_in_good_condition = validated_data.get('receive_in_good_condition',instance.receive_in_good_condition)
      instance.equipment_description = validated_data.get('equipment_description',instance.equipment_description)
      instance.production_trial_readliness_date = validated_data.get('production_trial_readliness_date',instance.production_trial_readliness_date)
      instance.pending = validated_data.get('pending',instance.pending)
      instance.ready = validated_data.get('ready',instance.ready)
      instance.during_engg_visit = validated_data.get('during_engg_visit',instance.during_engg_visit)
      instance.not_understood_list = validated_data.get('not_understood_list',instance.not_understood_list)
      instance.further_tech_guidence_needed = validated_data.get('further_tech_guidence_needed',instance.further_tech_guidence_needed)
      instance.spare_name = validated_data.get('spare_name',instance.spare_name)
      instance.spare_sr_no = validated_data.get('spare_sr_no',instance.spare_sr_no)
      instance.spare_model_name = validated_data.get('spare_model_name',instance.spare_model_name)
      instance.part_name = validated_data.get('part_name',instance.part_name)
      instance.part_description = validated_data.get('part_description',instance.part_description)
      instance.part_quantity = validated_data.get('part_quantity',instance.part_quantity)
      instance.closed_ticket = validated_data.get('closed_ticket',instance.closed_ticket)
      instance.on_call_ticket = validated_data.get('on_call_ticket',instance.on_call_ticket)
      instance.visit_and_closed = validated_data.get('visit_and_closed',instance.visit_and_closed)
      instance.visit_scheduled = validated_data.get('visit_scheduled',instance.visit_scheduled)
      instance.waiting_for_spares = validated_data.get('waiting_for_spares',instance.waiting_for_spares)
      instance.status_of_ticket = validated_data.get('status_of_ticket',instance.status_of_ticket)
      instance.priorty = validated_data.get('priorty',instance.priorty)
      instance.review = validated_data.get('review',instance.review)
      instance.attach_file =validated_data.get('attach_file',instance.attach_file)
      instance.save()
      return instance


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email','user_name','user_company_name','user_city','user_zip_code','user_group_name','user_position_name','user_zone_name']
      

class CloseTicketDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = TicketModel
    fields = ['ticket_email','ticket_creator_name','query_type','ticket_creator_address']






  
