import imp
from xml.etree.ElementInclude import include
from django.urls import path
from django.contrib import admin
from nvc_app import views
from django.conf import settings
from django.conf.urls.static import  static

from rest_framework.routers import DefaultRouter






urlpatterns = [
    path('admin/',admin.site.urls),
    #path('',include(router.urls)),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('email_password_reset/',views.EmailPasswordResetView.as_view(),name='email-password-reset'),
    path('reset_password/<uid>/<token>/',views.ResetPasswordView.as_view(),name='reset-password'),
    path('change_password/',views.UserChangePasswordView.as_view(),name='change_password'),
    path('user_profile/',views.UserProfile.as_view(),name='user-profile'),
    path('create_ticket/',views.CreateTicket.as_view(),name='create_ticket'),
    path('all_ticket/',views.AllTickets.as_view(),name='all-ticket'),
    path('on_call_ticket/',views.OnCallView.as_view(),name='on-call-ticket'),
    path('closed_ticket/',views.ClosedTicketView.as_view(),name='closed_ticket'),
    path('visit_and_closed/',views.VisitAndClosedView.as_view(),name='visit-and-closed'),
    path('user_profile/<int:pk>/',views.UserProfile.as_view(),name='user-profile'),
    path('update_ticket/<int:pk>/',views.UpdateTicketStatus.as_view(),name='update-ticket'),
    path('ticket_created_by_user/',views.TicketCreatedByUser.as_view(),name='ticket-created-by-user'),
    path('close_ticket_details/<int:pk>/',views.CloseTicketDetails.as_view(),name='close-ticket-details'),
    path('close_ticket/<int:pk>/',views.CloseTicket.as_view(),name='close-ticket'),
    path('review/<int:pk>/',views.Review.as_view(),name='review'),
   

] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)