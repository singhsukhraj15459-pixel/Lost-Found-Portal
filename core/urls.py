from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('report/lost/', views.report_lost_view, name='report_lost'),
    path('report/found/', views.report_found_view, name='report_found'),
    path('browse/lost/', views.browse_lost_view, name='browse_lost'),
    path('browse/found/', views.browse_found_view, name='browse_found'),
    path('item/lost/<int:item_id>/', views.lost_item_detail_view, name='lost_item_detail'),
    path('item/found/<int:item_id>/', views.found_item_detail_view, name='found_item_detail'),
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/<int:user_id>/', views.conversation_view, name='conversation'),
    path('contact/<str:item_type>/<int:item_id>/', views.start_conversation_view, name='start_conversation'),
    path('my-reports/lost/', views.my_lost_reports_view, name='my_lost_reports'),
    path('my-reports/found/', views.my_found_reports_view, name='my_found_reports'),
    path('my-reports/lost/<int:item_id>/recovered/', views.mark_lost_recovered_view, name='mark_lost_recovered'),
    path('my-reports/found/<int:item_id>/recovered/', views.mark_found_recovered_view, name='mark_found_recovered'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-stats/', views.admin_statistics_view, name='admin_statistics'),
]