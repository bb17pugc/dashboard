from django.urls import path

from . import views

urlpatterns = [
        path('', views.signin, name='signin'),
        path('signin', views.signin, name='signin'),
        path('users', views.users, name='users'),
        path('songs_streams', views.songs_streams, name='songs_streams'),
        path('reports', views.reports, name='reports'),
        path('setting', views.setting, name='setting'),
        path('dashboard', views.dashboard, name='dashboard'),
        path('logout', views.logout, name='logout'),
        path('new_user', views.newuser, name='newuser'),
        path('remove', views.remove, name='remove'),
        path('streams', views.streams, name='streams'),
        path('user_panel', views.user_panel, name='user_panel'),
        path('user_report', views.user_report, name='user_report'),
        path('upload_audio_file', views.upload_audio_file, name='upload_audio_file'),
        path('store_hashes', views.store_hashes, name='store_hashes'),
        path('find_song', views.find_song, name='find_song'),
        path('delete_song', views.delete_song, name='delete_song'),
        path('edit_profile', views.edit_profile, name='edit_profile'),
        path('change_password', views.change_password, name='change_password'),
        path('admin_reports', views.admin_reports, name='admin_reports'),

]
