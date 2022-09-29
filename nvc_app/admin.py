from django.contrib import admin
from .models import GroupModel, PositionModel, User , TicketModel, ZoneModel
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('id', 'email', 'user_name', 'user_zip_code', 'is_admin')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('user_name', 'user_company_name','user_zip_code','fcm_token','user_city','user_zone_name')}),
      ('Permissions', {'fields': ('is_admin',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'user_name', 'user_company_name','user_city','user_zip_code', 'password1', 'password2','user_group_name','user_position_name','user_zone_name'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email', 'id')
  filter_horizontal = ()


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)


admin.site.register(TicketModel)
admin.site.register(GroupModel)
admin.site.register(PositionModel)
admin.site.register(ZoneModel)