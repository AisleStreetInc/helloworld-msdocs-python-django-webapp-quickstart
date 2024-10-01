from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hello', views.hello, name='hello'),
    path('standalone_button', views.standalone_button, name='standalone_button'),
    path('redirect_button', views.redirect_button, name='redirect_button'),
    path('create-checkout-session', views.create_checkout_session, name='redirect_button'),
    path('success', views.success, name='success'),
    path('cancel', views.cancel, name='cancel'),
    
]