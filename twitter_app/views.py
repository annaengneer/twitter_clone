from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef,Q
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post,Profile
from twitter_app.models import Post, Like, Relation, Bookmark, Conversation, Message

User=get_user_model()

@login_required
def top(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('twitter_app:top')
    else:
        form = PostForm()

    posts = (Post.objects.all().order_by('-id').annotate(
        is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
        is_repost=Exists(Post.objects.filter(user=request.user,repost_from=OuterRef("pk"))),
        is_following=Exists(Relation.objects.filter(followers=request.user,followings=OuterRef("user_id"))),
        is_bookmarked=Exists(Bookmark.objects.filter(user=request.user, post=OuterRef('pk')))
    ).order_by('-id').select_related("user", "user__profile"))


    return render(request, 'top_authenticated.html',{
        "form":form,
        "object_list":posts,
    })

class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy("account_login")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response

def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    posts = (Post.objects.filter(user=profile.user).order_by('-created_at').annotate(
        is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
        is_repost=Exists(Post.objects.filter(user=request.user,repost_from=OuterRef("pk")))
    ))

    context = {
        "profile": profile,
        "object_list": posts,
    }

    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user= request.user)
        if form.is_valid():

            request.user.username = form.cleaned_data['username']
            if hasattr(request.user,'display_name'):
                request.user.display_name = form.cleaned_data['display_name']
            request.user.save()

            form.save()
            return redirect('twitter_app:profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile, user=request.user)
        
    return render(request, 'profile_edit.html', {'form': form, 'profile': profile})

@login_required
def post_detail(request, post_id):
    post = (
        Post.objects.filter(id=post_id).annotate(is_liked=Exists(
            Like.objects.filter(post=OuterRef('pk'), user=request.user)),
            is_repost=Exists(Post.objects.filter(user=request.user, repost_from=OuterRef('pk'))
            )).first()
    )
    if post is None:
        raise Http404()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect('twitter_app:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    comments = post.comments.order_by('-created_at')

    return render(request, 'post_detail.html',{
        "post": post,
        "form": form,
        "comments": comments,
    })

@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
    
    base_url = request.META.get('HTTP_REFERER', '/')

    return redirect(f"{base_url}#post-{post.id}")

@login_required
def post_repost(request, post_id):
    original_post = get_object_or_404(Post, id=post_id)

    existing_repost = Post.objects.filter(user=request.user, repost_from=original_post).first()
    
    if existing_repost:
        existing_repost.delete()
    else:
        Post.objects.create(user=request.user,content="", repost_from=original_post)
    return redirect(f"{request.META.get('HTTP_REFERER', '/') }#post-{post_id}")

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    Relation.objects.get_or_create(followers=request.user,followings=user_to_follow)
    return redirect(request.META.get('HTTP_REFERER', 'twitter_app:top'))

@login_required
def unfollow_user(request,username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Relation.objects.filter(followers=request.user,followings=user_to_unfollow).delete()
    return redirect(request.META.get('HTTP_REFERER', 'twitter_app:top'))

@login_required
def bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark,created = Bookmark.objects.get_or_create(
    user=request.user,
    post=post
)
    if not created:
        bookmark.delete()
    
    return redirect(f"{request.META.get('HTTP_REFERER', '/')}#post-{post_id}")

@login_required
def bookmark_list(request):
    posts = (
        Post.objects.filter(bookmarked__user=request.user).order_by('id').annotate(
            is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
        is_repost=Exists(Post.objects.filter(user=request.user,repost_from=OuterRef("pk"))),
        is_following=Exists(Relation.objects.filter(followers=request.user,followings=OuterRef("user_id"))),
        is_bookmarked=Exists(Bookmark.objects.filter(user=request.user, post=OuterRef('pk'))),
        ).select_related('user', 'user__profile')
    )

    return render(request, "bookmark_list.html", {
        "object_list": posts
    })

@login_required
def conversation_list(request):
    conversations_raw = (
        Conversation.objects.filter(participants=request.user).order_by('-updated_at').prefetch_related('participants', 'messages')
    )

    conversations = []

    for conv in conversations_raw:
        other_user = conv.participants.exclude(id=request.user.id).first()

        last_message = conv.messages.order_by('created_at').last()

        conversations.append({
            'conversation': conv,
            'other_user':other_user,
            'last_message': last_message,
        })

    return render(request, 'conversation_list.html',{
        'conversations': conversations
    })

@login_required
def conversation_select(request):
    users = User.objects.all().select_related('profile')

    return render(request, 'conversation_select.html',{
        'users': users
    })

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, participants=request.user
    )

    other_user = conversation.participants.exclude(id=request.user.id).first()

    messages = conversation.messages.order_by('created_at')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            dm = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )

            Conversation.objects.filter(id=conversation.id).update(
                updated_at=dm.created_at
            )
        return redirect('twitter_app:conversation_detail', conversation_id=conversation.id)

    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    return render(request, 'conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user
    })

@login_required
def start_conversation(request, username):
    other_user =get_object_or_404(User, username=username)

    if not other_user or other_user == request.user:
        return redirect('twitter_app:top')

    conversation=(
    Conversation.objects
    .filter(participants=request.user)
    .filter(participants=other_user)
    .first()
    )
    if request.method == 'POST':
        text = request.POST.get('text')
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)

        if text:
            dm = Message.objects.create (
                conversation=conversation,
                sender=request.user,
                text=text,
            )
            Conversation.objects.filter(id=conversation.id).update(
                updated_at=dm.created_at
            )
        return redirect('twitter_app:conversation_detail', conversation.id)

    return render(request, 'conversation_new.html',{
        'other_user': other_user,
        'conversation': conversation,
    })