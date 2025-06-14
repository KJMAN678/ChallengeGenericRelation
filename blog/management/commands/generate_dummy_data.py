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
        for _ in range(blogs_count):
            Blog.objects.create(
                title=fake.sentence(nb_words=6),
                content=fake.text(max_nb_chars=1000)
            )
        
        comments_count = options['comments']
        blogs = list(Blog.objects.all())
        
        if not blogs:
            self.stdout.write(self.style.ERROR('No blogs found. Create blogs first.'))
            return
            
        for _ in range(comments_count):
            Comment.objects.create(
                content=fake.text(max_nb_chars=300),
                blog=random.choice(blogs)
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {blogs_count} blogs and {comments_count} comments'
            )
        )
