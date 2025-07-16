from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_author/', views.add_author, name='add_author'),
    path('add_quote/', views.add_quote, name='add_quote'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('tag/<str:tag_name>/', views.quotes_by_tag, name='tag_quotes'),
    path('top_tags/', views.top_tags, name='top_tags'),
    path('scrape/', views.scrape_site, name='scrape'),
]
