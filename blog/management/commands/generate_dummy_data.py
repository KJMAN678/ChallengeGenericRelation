from django.core.management.base import BaseCommand
from faker import Faker
from blog.models import Blog, Comment
import random


class Command(BaseCommand):
    help = 'Generate dummy data for Blog and Comment models'
    
    def add_arguments(self, parser):
        parser.add_argument('--blogs', type=int, default=10, help='Number of blogs to create')
        parser.add_argument('--comments', type=int, default=50, help='Number of comments to create')
    
    def handle(self, *args, **options):
        fake = Faker('ja_JP')
        
        blogs_count = options['blogs']
        
        blog_list = []
        for _ in range(blogs_count):
            blog_list.append(Blog(
                title=fake.sentence(nb_words=6),
                content=fake.text(max_nb_chars=1000)
            ))
        
        Blog.objects.bulk_create(blog_list)
        
        comments_count = options['comments']
        blogs = list(Blog.objects.all())
        
        if not blogs:
            self.stdout.write(self.style.ERROR('No blogs found. Create blogs first.'))
            return
        
        comment_list = []
        for _ in range(comments_count):
            comment_list.append(Comment(
                content=fake.text(max_nb_chars=300),
                blog=random.choice(blogs)
            ))
        
        Comment.objects.bulk_create(comment_list)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {blogs_count} blogs and {comments_count} comments using bulk_create()'
            )
        )
