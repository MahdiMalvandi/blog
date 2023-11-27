from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib.auth import login, authenticate, logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Max


# Create your views here.
def get_all_category():
    return Category.objects.all()


def home(request):
    if request.GET.get('q'):
        post = get_object_or_404(Post, id=request.GET.get('q'))
        return redirect('blog_app:blog page', post.slug)
    most_popular_posts = Post.objects.annotate(avg_points=Avg('post_comments__point')).order_by('avg_points')
    context = {
        'most_popular_post': most_popular_posts[:1].first(),
        'popular_posts': most_popular_posts[1:5],
        'categories': get_all_category(),
    }
    return render(request, 'blog_app/index.html', context)


def blogs(request):

    posts = Post.objects.annotate(avg_points=Avg('post_comments__point')).select_related('author', 'category').order_by('avg_points').all()
    context = {
        'posts': posts,
        'categories': get_all_category(),
    }
    return render(request, 'blog_app/blog.html', context)


def get_blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    similar_posts = Post.objects.select_related('author', 'category').filter(category=post.category).exclude(id=post.id)
    short_link = request.build_absolute_uri('/')[:-1] + f'?q={post.id}'
    comments = Comment.objects.select_related('user', 'post').filter(post=post, reply__post=None)

    context = {
        'post': post,
        'categories': get_all_category(),
        'similar_posts': similar_posts,
        'short_link': short_link,
        'comments': comments
    }
    return render(request, 'blog_app/post.html', context)


def get_category_posts(request, category_name):
    posts = Post.objects.select_related('author', 'category').filter(category__text=category_name)
    context = {
        'category': category_name,
        'posts': posts
    }
    return render(request, 'blog_app/filtered_post.html', context)


def services(request):
    return render(request, 'blog_app/services.html')


def about_us(request):
    return render(request, 'blog_app/about.html')


def contact(request):
    return render(request, 'blog_app/contact.html')


def get_user_info(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'user': user
    }
    return render(request, 'blog_app/user-profile.html', context=context)


@login_required( redirect_field_name='next_page')
def profile(request):
    return render(request, 'blog_app/dashboard.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            login(request)
            return redirect('blog_app:home')
    else:
        form = SignUpForm()
    context = {
        'form': form
    }
    return render(request, 'forms/signup.html', context=context)


def login_view(request):

    if request.method == 'POST':

        form = LoginForm(request.POST)
        if form.is_valid():

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                if request.GET.get('next_page'):
                    return redirect(request.GET.get('next_page'))

            return redirect('blog_app:home')
    else:
        form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'forms/signin.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('blog_app:home')
