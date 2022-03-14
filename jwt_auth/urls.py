from django.urls import path
from jwt_auth.views import *


urlpatterns = [
    path('register/', register),
    path('login/', login_view),
    path('logout/', logout_view),
    path('refresh/', refresh),
    path('vk_auth/', vk_auth),
    path('facebook_auth/', facebook_auth),
    path('register_confirm/', register_confirm),
    path('send_reg_code_again/', send_reg_code_again)
]