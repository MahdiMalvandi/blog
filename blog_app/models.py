from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.urls import reverse


# region users model
class User(AbstractUser):
    positions = (
        ('admin', 'admin'),
        ('user', 'user'),
    )
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')
    profile = models.ImageField(upload_to='users_profile/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=1000)
    job = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f'{self.username}'


# endregion

# region category models
class Category(models.Model):
    text = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return f'{self.text}'


# endregion

# region post model
class Post(models.Model):
    title = models.CharField(max_length=1000)
    body = RichTextUploadingField()
    description = models.TextField(max_length=10000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    created = models.DateTimeField(auto_now_add=True)
    short_link = models.CharField(max_length=100)
    slug = models.SlugField(max_length=1000, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='article-thumbnail/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]

    # def save(self, *args, **kwargs):
    #     super(Post, self).save(*args, **kwargs)
    #     self.slug = self.title.replace(' ', '-') + '-' + str(self.pk)
    #
    #     super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_app:blog page', args=[self.slug])


# endregion

# region comments model
class Comment(models.Model):
    point_choices = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    user = models.ForeignKey(User, related_name='user_comments', on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='post_comments', on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    point = models.PositiveIntegerField(choices=point_choices, default=5)

    def __str__(self):
        return f'a comment for {self.post} by {self.user}'


# endregion


# region ticket

class Ticket(models.Model):
    type_of_tickets = (
        ('Bug', 'Bug'),
        ('Proposal', 'Proposal'),
        ('Support', 'Support'),
        ('Criticism', 'Criticism'),
    )
    type = models.CharField(choices=type_of_tickets, max_length=25, default='Support')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    answer = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='answers')
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=1000)
    is_open = models.BooleanField(default=True)
    class Meta:
        indexes = [models.Index(fields=['-created'])]
        ordering = ('-created',)

    def __str__(self):
        return f'ticket {self.type}'
# endregion
