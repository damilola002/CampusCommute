from django.urls import path
from . import views

urlpatterns = [
    path('create/',                    views.create_order,           name='create_order'),
    path('offer/',                     views.offer_ride,             name='offer_ride'),
    path('tag-along/<int:order_id>/',  views.tag_along,              name='tag_along'),
    path('board/',                     views.community_board,        name='community_board'),
    path('driver/',                    views.driver_board,           name='driver_board'),
    path('accept/<int:order_id>/',     views.accept_order,           name='accept_order'),
    path('update-location/',           views.update_driver_location, name='update_driver_location'),
    path('notifications/',             views.notifications_list,     name='notifications'),
    path('notifications/count/',       views.notification_count,     name='notification_count'),
    path('history/',                   views.ride_history,           name='ride_history'),
    path('ordering_service/',          views.discussions,            name='discussions'),
    path('chat/<int:ride_order_id>/',  views.chat_room,              name='chat_room'),
    path('chat/<int:ride_order_id>/messages/', views.get_messages_api, name='get_messages_api'),
    path('chat/<int:ride_order_id>/send/', views.send_message_api, name='send_message_api'),
    path('map/',                       views.map_view,               name='map_view'),
    path('map-data/',                  views.map_data,               name='map_data'),
    path('my-trips/',                  views.my_trips,               name='my_trips'),
    path('end/<int:ride_order_id>/',   views.end_ride,               name='end_ride'),
]
