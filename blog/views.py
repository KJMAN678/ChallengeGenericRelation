from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Blog, Comment, Favorite
from .forms import BlogForm, CommentForm


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 10
    
    def get_queryset(self):
        return Blog.objects.prefetch_related(
            GenericPrefetch(
                'favorites',
                [Favorite.objects.all()]
            ),
            'comments'
        )


class BlogCreateView(CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')


class BlogUpdateView(UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'
    
    def get_success_url(self):
        return reverse('blog:blog_detail', kwargs={'pk': self.object.pk})


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')


def blog_detail(request, pk):
    blog = get_object_or_404(
        Blog.objects.prefetch_related(
            GenericPrefetch(
                'favorites',
                [Favorite.objects.all()]
            ),
            'comments__favorites'
        ),
        pk=pk
    )
    
    blog_ct = ContentType.objects.get_for_model(Blog)
    is_blog_favorited = Favorite.objects.filter(
        content_type=blog_ct,
        object_id=blog.pk
    ).exists()
    
    comment_ct = ContentType.objects.get_for_model(Comment)
    comment_favorites = {}
    for comment in blog.comments.all():
        comment_favorites[comment.pk] = Favorite.objects.filter(
            content_type=comment_ct,
            object_id=comment.pk
        ).exists()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.save()
            return redirect('blog:blog_detail', pk=blog.pk)
    else:
        form = CommentForm()
    
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'is_blog_favorited': is_blog_favorited,
        'comment_favorites': comment_favorites,
        'form': form,
        'blog_content_type_id': blog_ct.id,
        'comment_content_type_id': comment_ct.id,
    })


@require_POST
def toggle_favorite(request):
    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')
    
    content_type = get_object_or_404(ContentType, id=content_type_id)
    
    favorite, created = Favorite.objects.get_or_create(
        content_type=content_type,
        object_id=object_id
    )
    
    if not created:
        favorite.delete()
        favorited = False
    else:
        favorited = True
    
    return JsonResponse({'favorited': favorited})


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def get_success_url(self):
        return reverse('blog:blog_detail', kwargs={'pk': self.object.blog.pk})


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('blog:blog_detail', kwargs={'pk': self.object.blog.pk})
