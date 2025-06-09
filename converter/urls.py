from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
    path('image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    path('pdf-to-image/', views.pdf_to_image, name='pdf_to_image'),
    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),

    path('protect-pdf/', views.protect_pdf, name='protect_pdf'),

    path('compress-file/', views.compress_file, name='compress_file'),
    path('extract-from-pdf/', views.extract_from_pdf, name='extract_from_pdf'),
    path('delete-pdf-pages/', views.delete_pdf_pages, name='delete_pdf_pages'),




]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
