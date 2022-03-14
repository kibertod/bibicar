from django.urls import path
from api.views import *


urlpatterns = [
    path('load_cars/', load_cars),
    path('get_marks/', get_marks),
    path('get_models/', get_models),
    path('get_cars/', get_cars),
    path('view_car/', view_car),
    path('get_profile/', get_profile),
    path('update_profile/', update_profile),
    path('delete_profile/', delete_profile),
    path('add_car/', add_car),
    path('add_review/', add_review),
    path('change_email/', change_email),
    path('change_email_confirm/', change_email_confirm),
    path('reset_password/', reset_password),
    path('change_password/', change_password),
    path('change_password_confirm/', change_password_confirm),
    path('send_message/', send_message),
    path('get_messages/', get_messages),
    path('add_favorite/', add_favorite),
    path('del_favorite/', del_favorite),
    path('get_lists/', get_lists),
    path('get_list_values/<str:list_name>/', get_list_values),
    path('deposit/', deposit),
    path('payment_callback', сallback),
    path('get_vip/', get_vip),
    path('get_ads/', get_ads),
    path('extend_car_ad/', extend_car_ad),
    path('boost_car/', boost_car),
    path('get_prices/', get_prices),
]