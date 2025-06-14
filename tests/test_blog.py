from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog, Comment, Favorite
from blog.management.commands.generate_dummy_data import Command


class BlogModelTest(TestCase):
    def test_blog_creation(self):
        blog = Blog.objects.create(
            title="Test Blog",
            content="Test content"
        )
        self.assertEqual(blog.title, "Test Blog")
        self.assertEqual(str(blog), "Test Blog")
        self.assertTrue(blog.created_at)
        self.assertTrue(blog.updated_at)
    
    def test_comment_creation(self):
        blog = Blog.objects.create(title="Test", content="Content")
        comment = Comment.objects.create(
            content="Test comment",
            blog=blog
        )
        self.assertEqual(comment.blog, blog)
        self.assertIn(comment, blog.comments.all())
        self.assertEqual(str(comment), f"Comment on {blog.title}")
    
    def test_favorite_generic_relation(self):
        blog = Blog.objects.create(title="Test", content="Content")
        comment = Comment.objects.create(content="Test", blog=blog)
        
        blog_ct = ContentType.objects.get_for_model(Blog)
        blog_favorite = Favorite.objects.create(
            content_type=blog_ct,
            object_id=blog.pk
        )
        self.assertEqual(blog_favorite.content_object, blog)
        self.assertIn(blog_favorite, blog.favorites.all())
        
        comment_ct = ContentType.objects.get_for_model(Comment)
        comment_favorite = Favorite.objects.create(
            content_type=comment_ct,
            object_id=comment.pk
        )
        self.assertEqual(comment_favorite.content_object, comment)
        self.assertIn(comment_favorite, comment.favorites.all())
    
    def test_favorite_unique_constraint(self):
        blog = Blog.objects.create(title="Test", content="Content")
        blog_ct = ContentType.objects.get_for_model(Blog)
        
        Favorite.objects.create(
            content_type=blog_ct,
            object_id=blog.pk
        )
        
        with self.assertRaises(Exception):
            Favorite.objects.create(
                content_type=blog_ct,
                object_id=blog.pk
            )


class BlogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.blog = Blog.objects.create(
            title="Test Blog",
            content="Test content"
        )
    
    def test_blog_list_view(self):
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Blog")
        self.assertContains(response, "ブログ一覧")
    
    def test_blog_detail_view(self):
        response = self.client.get(
            reverse('blog:blog_detail', kwargs={'pk': self.blog.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Blog")
        self.assertContains(response, "Test content")
    
    def test_blog_create_view(self):
        response = self.client.get(reverse('blog:blog_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "新規ブログ作成")
        
        response = self.client.post(reverse('blog:blog_create'), {
            'title': 'New Blog',
            'content': 'New content'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Blog.objects.filter(title='New Blog').exists())
    
    def test_blog_update_view(self):
        response = self.client.get(
            reverse('blog:blog_edit', kwargs={'pk': self.blog.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ブログ編集")
        
        response = self.client.post(
            reverse('blog:blog_edit', kwargs={'pk': self.blog.pk}),
            {
                'title': 'Updated Blog',
                'content': 'Updated content'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Updated Blog')
    
    def test_blog_delete_view(self):
        response = self.client.get(
            reverse('blog:blog_delete', kwargs={'pk': self.blog.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "削除確認")
        
        response = self.client.post(
            reverse('blog:blog_delete', kwargs={'pk': self.blog.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())
    
    def test_favorite_toggle(self):
        blog_ct = ContentType.objects.get_for_model(Blog)
        response = self.client.post(reverse('blog:toggle_favorite'), {
            'content_type_id': blog_ct.id,
            'object_id': self.blog.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['favorited'])
        self.assertTrue(
            Favorite.objects.filter(
                content_type=blog_ct,
                object_id=self.blog.pk
            ).exists()
        )
        
        response = self.client.post(reverse('blog:toggle_favorite'), {
            'content_type_id': blog_ct.id,
            'object_id': self.blog.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['favorited'])
        self.assertFalse(
            Favorite.objects.filter(
                content_type=blog_ct,
                object_id=self.blog.pk
            ).exists()
        )
    
    def test_comment_creation_in_blog_detail(self):
        response = self.client.post(
            reverse('blog:blog_detail', kwargs={'pk': self.blog.pk}),
            {
                'content': 'Test comment content'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                blog=self.blog,
                content='Test comment content'
            ).exists()
        )


class CommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.blog = Blog.objects.create(
            title="Test Blog",
            content="Test content"
        )
        self.comment = Comment.objects.create(
            content="Test comment",
            blog=self.blog
        )
    
    def test_comment_update_view(self):
        response = self.client.get(
            reverse('blog:comment_edit', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "コメント編集")
        
        response = self.client.post(
            reverse('blog:comment_edit', kwargs={'pk': self.comment.pk}),
            {
                'content': 'Updated comment'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment')
    
    def test_comment_delete_view(self):
        response = self.client.get(
            reverse('blog:comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "削除確認")
        
        response = self.client.post(
            reverse('blog:comment_delete', kwargs={'pk': self.comment.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class ManagementCommandTest(TestCase):
    def test_generate_dummy_data_command(self):
        command = Command()
        command.handle(blogs=5, comments=10)
        
        self.assertEqual(Blog.objects.count(), 5)
        self.assertEqual(Comment.objects.count(), 10)
        
        for comment in Comment.objects.all():
            self.assertIn(comment.blog, Blog.objects.all())
    
    def test_generate_dummy_data_no_blogs(self):
        command = Command()
        
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        command.handle(blogs=0, comments=10)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn('No blogs found', output)
        self.assertEqual(Comment.objects.count(), 0)


class GenericPrefetchTest(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Test Blog",
            content="Test content"
        )
        self.comment = Comment.objects.create(
            content="Test comment",
            blog=self.blog
        )
        
        blog_ct = ContentType.objects.get_for_model(Blog)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        Favorite.objects.create(
            content_type=blog_ct,
            object_id=self.blog.pk
        )
        Favorite.objects.create(
            content_type=comment_ct,
            object_id=self.comment.pk
        )
    
    def test_generic_prefetch_optimization(self):
        from django.contrib.contenttypes.prefetch import GenericPrefetch
        
        with self.assertNumQueries(3):
            blogs = Blog.objects.prefetch_related(
                GenericPrefetch(
                    'favorites',
                    [Favorite.objects.all()]
                ),
                'comments'
            )
            
            for blog in blogs:
                list(blog.favorites.all())
                for comment in blog.comments.all():
                    list(comment.favorites.all())
