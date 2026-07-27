from django.urls import path
from . import views

urlpatterns = [
    path('create/',                    views.create_order,           name='create_order'),
    path('board/',                     views.community_board,        name='community_board'),
    path('driver/',                    views.driver_board,           name='driver_board'),
    path('accept/<int:order_id>/',     views.accept_order,           name='accept_order'),
    path('update-location/',           views.update_driver_location, name='update_driver_location'),
    path('notifications/',             views.notifications_list,     name='notifications'),
    path('history/', views.ride_history, name='ride_history'),
    path('discussions/', views.discussions, name='discussions'),
]
