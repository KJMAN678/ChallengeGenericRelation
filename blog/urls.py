from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('create/', views.BlogCreateView.as_view(), name='blog_create'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),
    path('<int:pk>/edit/', views.BlogUpdateView.as_view(), name='blog_edit'),
    path('<int:pk>/delete/', views.BlogDeleteView.as_view(), name='blog_delete'),
    path('comment/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_edit'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]
