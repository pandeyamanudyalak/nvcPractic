from hashlib import blake2b
from django.contrib.auth.models import Group
from pyexpat import model
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser


#  Custom User Manager
class UserManager(BaseUserManager):
  def create_user(self, email, user_name,user_city,user_zip_code,user_company_name, password=None, password2=None):
     
      if not email:
          raise ValueError('User must have an email address')

      user = self.model(
          email=self.normalize_email(email),
          user_name=user_name,
          user_city = user_city,
          user_zip_code = user_zip_code,
          user_company_name = user_company_name
         
      )

      user.set_password(password)
      user.save(using=self._db)
      return user

  def create_superuser(self, email,  user_name,user_city,user_zip_code,user_company_name,  password=None):
     
      user = self.create_user(
          email,
          password=password,
          user_name=user_name,
          user_city = user_city,
          user_zip_code = user_zip_code,
          user_company_name = user_company_name
          
      )
      user.is_active = True
      user.is_admin = True
      #user.is_staff = True
      user.save(using=self._db)
      return user



class GroupModel(models.Model):
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return self.group_name


class PositionModel(models.Model):
    position_name = models.CharField(max_length=100)

    def __str__(self):
        return self.position_name

class ZoneModel(models.Model):
    zone_name = models.CharField(max_length=100)

    def __str__(self):
        return self.zone_name


# class FcmtokenModel(models.Model):
#     fcm = models.CharField(max_length=300)



#  Custom User Model
class User(AbstractBaseUser):
  email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
  )
  user_name = models.CharField(max_length=200)
  user_company_name = models.CharField(max_length=200)
  user_city = models.CharField(max_length=100)
  user_zip_code = models.IntegerField()
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  fcm_token = models.CharField(max_length=400,null=True,blank=True)

#Group
  user_group_name = models.ForeignKey(GroupModel,on_delete=models.CASCADE,null=True,blank=True)
  user_position_name = models.ForeignKey(PositionModel,on_delete=models.CASCADE,null=True,blank=True)
  user_zone_name = models.ForeignKey(ZoneModel,on_delete=models.CASCADE,null=True,blank=True)


  

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['user_name', 'user_company_name','user_city','user_zip_code']

  def __str__(self):
      return self.email

  def has_perm(self, perm, obj=None):
      "Does the user have a specific permission?"
      # Simplest possible answer: Yes, always
      return self.is_admin

  def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return True

  @property
  def is_staff(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_admin





class TicketModel(models.Model):
    type = (
        ('installation','Installation'),
        ('service','Service'),
        ('spares','Spares'),
        ('sales snquiry','Sales Enquiry')
    )

    receving_status = (
        ('Yes','yes'),
        ('No','No')
    )
    ticket_id = models.AutoField(primary_key=True)
    query_type = models.CharField(choices=type,max_length=30)
    ticket_email = models.EmailField(
      verbose_name='ticket_email',
      max_length=255,
      
    )
    ticket_number = models.CharField(max_length=200,null=True,blank=True)
    ticket_creator_name = models.CharField(max_length=200)
    ticket_creator_address = models.CharField(max_length=500)
    ticket_user_name = models.CharField(max_length=200,null=True,blank=True)
    ticket_creator_zip = models.IntegerField()

    # Fields for query type installation

    equipment_name = models.CharField(max_length=200,null=True,blank=True)
    equipment_sr_no = models.CharField(max_length=200,null=True,blank=True)
    equipment_model_no = models.CharField(max_length=200,null=True,blank=True)
    problem_description = models.CharField(max_length=200,null=True,blank=True)
    production_temprorary_running = models.BooleanField(default=False)
    running_with_rejection = models.BooleanField(default=False)
    #running_with_rejection = models.BooleanField(default=False)
    production_breakdown = models.BooleanField(default=False)

    # Fields for query type sales

    sales_production_name = models.CharField(max_length=200,null=True,blank=True)
    process_mc_type = models.CharField(max_length=200,null=True,blank=True)
    max_kg_or_hrs = models.CharField(max_length=200,null=True,blank=True)
    material_denticty =  models.CharField(max_length=200,null=True,blank=True)

    # Production Status for sales enquiry

    virgin = models.BooleanField(default=False)
    regrind =  models.BooleanField(default=False)
    falkes =  models.BooleanField(default=False)
    master_batch =  models.BooleanField(default=False)
    additives_1 =  models.BooleanField(default=False)
    additives_2 =  models.BooleanField(default=False)

    # Fields for query type installation
    work_order_no = models.IntegerField(null=True,blank=True)
    packing_slip_no = models.IntegerField(null=True,blank=True)
    receive_in_good_condition = models.CharField(choices=receving_status,default='Yes',max_length=10)
    equipment_description = models.CharField(max_length=400,null=True,blank=True)
    production_trial_readliness_date = models.DateField(null=True,blank=True)

    # Pre installation CheckList status
    pending = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)
    during_engg_visit = models.BooleanField(default=False)
    not_understood_list = models.BooleanField(default=False)
    further_tech_guidence_needed = models.BooleanField(default=False)

    # Fields for query type spares
    spare_name = models.CharField(max_length=200,null=True,blank=True)
    spare_sr_no = models.CharField(max_length=200,null=True,blank=True)
    spare_model_name = models.CharField(max_length=200,null=True,blank=True)
    #Parts details
    part_name = models.CharField(max_length=200,null=True,blank=True)
    part_description = models.CharField(max_length=200,null=True,blank=True)
    part_quantity = models.IntegerField(null=True,blank=True)

    # Flag Values
    closed_ticket = models.BooleanField(default=False)
    on_call_ticket = models.BooleanField(default=False)
    visit_and_closed = models.BooleanField(default=False)
    visit_scheduled = models.BooleanField(default=False)
    waiting_for_spares = models.BooleanField(default=False)

    #Step 3 Status of ticket

    ticket_status = (
        ('telephonic resolution','Telephonic Resolution'),
        ('require spare utilities','Require Spare Utilities'),
        ('payment pending','Payment Pending'),
        ('received by customer','Received By Customer'),
        ('revisit','Revisit'),
        ('resolved','Resolved')
    )


    status_of_ticket = models.CharField(choices=ticket_status,max_length=200)
    priorty = models.IntegerField(null=True,blank=True)
    attach_file = models.FileField(upload_to='attachments')

    #Review
    review = models.CharField(max_length=500,null=True,blank=True)

   


    def __str__(self):
        return str(self.ticket_id)







class Photo(models.Model):
    
    image = models.ImageField(upload_to='attachments')






