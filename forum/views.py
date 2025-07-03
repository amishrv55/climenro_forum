# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Subreddit, Post, Comment, Vote, CommentVote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

from django.core.paginator import Paginator


from .models import Post, Subreddit
from django.core.paginator import Paginator
from django.db import models

def home(request):
    sort = request.GET.get('sort', 'new')
    subreddit_name = request.GET.get('subreddit')
    country_code = request.GET.get('country')

    posts = Post.objects.all()

    if subreddit_name:
        posts = posts.filter(subreddit__name=subreddit_name)
    if country_code:
        posts = posts.filter(country=country_code)

    if sort == 'top':
        posts = posts.order_by('-upvotes')
    elif sort == 'hot':
        posts = posts.annotate(score=models.F('upvotes') - models.F('downvotes')).order_by('-score')
    else:
        posts = posts.order_by('-created_at')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    subreddits = Subreddit.objects.all()
    countries = Post.select_country  # ✅ Here’s the missing line

    return render(request, 'forum/home.html', {
        'posts': posts,
        'sort': sort,
        'subreddit_name': subreddit_name,
        'country_code': country_code,
        'countries': countries,
        'subreddits': subreddits,
    })


def subreddit(request, subreddit_name):
    subreddit = get_object_or_404(Subreddit, name=subreddit_name)
    posts = subreddit.posts.order_by('-created_at')
    return render(request, 'forum/subreddit.html', {'subreddit': subreddit, 'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.order_by('created_at')

    # Add vote counts to each comment manually
    for comment in comments:
        comment.upvotes = comment.commentvote_set.filter(value=1).count()
        comment.downvotes = comment.commentvote_set.filter(value=-1).count()

    return render(request, 'forum/post_detail.html', {'post': post, 'comments': comments})


@login_required
def create_post(request):
    if request.method == 'POST':
        subreddit_name = request.POST.get('subreddit')
        subreddit = get_object_or_404(Subreddit, name=subreddit_name)
        Post.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            subreddit=subreddit,
            author=request.user,
            country=request.POST.get('country'),
        )
        return redirect('subreddit', subreddit_name=subreddit.name)

    subreddits = Subreddit.objects.all()
    countries = Post.select_country  # <-- use the class-level choices
    return render(request, 'forum/create_post.html', {'subreddits': subreddits, 'countries': countries})


@login_required
def vote_post(request, post_id, direction):
    post = get_object_or_404(Post, id=post_id)

    # Ensure it's a POST request
    if request.method != "POST":
        return redirect('post_detail', post_id=post.id)

    vote_value = 1 if direction == "up" else -1

    vote, created = Vote.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={'value': vote_value}
    )

    # If already exists, update value if different
    if not created:
        if vote.value != vote_value:
            vote.value = vote_value
            vote.save()

    # Update post vote counts
    post.upvotes = Vote.objects.filter(post=post, value=1).count()
    post.downvotes = Vote.objects.filter(post=post, value=-1).count()
    post.save()

    return redirect('post_detail', post_id=post.id)

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')  # for nested replies

    if content:
        parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None
        Comment.objects.create(
            post=post,
            parent=parent_comment,
            author=request.user,
            content=content
        )
    return redirect('post_detail', post_id=post.id)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('post_detail', post_id=post.id)

    return render(request, 'forum/edit_post.html', {'post': post})


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('post_detail', post_id=comment.post.id)

    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.save()
        return redirect('post_detail', post_id=comment.post.id)

    return render(request, 'forum/edit_comment.html', {'comment': comment})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.title = "[deleted]"
        post.content = "[deleted]"
        post.save()
    return redirect('home')


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author:
        comment.content = "[deleted]"
        comment.save()
    return redirect('post_detail', post_id=comment.post.id)


@login_required
def create_subreddit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            Subreddit.objects.create(name=name, description=description)
            return redirect('subreddit', subreddit_name=name)

    return render(request, 'forum/create_subreddit.html')

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    
    post_karma = Vote.objects.filter(post__author=user).aggregate(score=models.Sum('value'))['score'] or 0
    comment_count = comments.count()

    return render(request, 'forum/user_profile.html', {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'karma': post_karma,
        'comment_count': comment_count
    })

def search(request):
    query = request.GET.get('q', '').strip()
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ) if query else []

    subreddits = Subreddit.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else []

    return render(request, 'forum/search_results.html', {
        'query': query,
        'posts': posts,
        'subreddits': subreddits,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'forum/register.html', {'form': form})

@login_required
def vote_comment(request, comment_id, direction):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method != 'POST':
        return redirect('post_detail', post_id=comment.post.id)

    vote_value = 1 if direction == 'up' else -1

    vote, created = CommentVote.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'value': vote_value}
    )

    if not created and vote.value != vote_value:
        vote.value = vote_value
        vote.save()

    return redirect('post_detail', post_id=comment.post.id)
