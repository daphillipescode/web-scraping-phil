from django.urls import path

from app.views import home, unprocess_urls, process_urls, view_listing

urlpatterns = [
    path('', home, name='home'),
    path('listing/view/<int:pk>', view_listing, name='view_listing'),
    path('unprocess/urls/', unprocess_urls, name='unprocess_urls'),
    path('process/urls/', process_urls, name='process-urls')
]