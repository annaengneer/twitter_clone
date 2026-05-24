from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q, Prefetch
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from .forms import SignUpForm, ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post,Profile
from twitter_app.models import Post, Like, Relation, Bookmark, Conversation, Message, Notification, Comment
from twitter_app.utils import send_notification_email

User=get_user_model()

def get_post_annotations(user):
    if not user.is_authenticated:
        return {}

    return {
        "is_liked": Exists(Like.objects.filter(post=OuterRef('pk'), user=user)),
        "is_repost": Exists(Post.objects.filter(user=user,repost_from=OuterRef("pk"))),
        "is_following": Exists(Relation.objects.filter(followers=user,followings=OuterRef("user_id"))),
        "is_bookmarked": Exists(Bookmark.objects.filter(user=user, post=OuterRef('pk'))),
    }

def top(request):
    if request.user.is_authenticated and request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('twitter_app:top')
    elif request.user.is_authenticated:
        form = PostForm()
    else:
        form = None

    posts = Post.objects.all().order_by('-id').select_related(
        "user",
        "user__profile",
        "repost_from__user",
        "repost_from__user__profile",
    )
    following_posts = Post.objects.none()

    if request.user.is_authenticated:
        post_annotations = get_post_annotations(request.user)
        posts = posts.annotate(**post_annotations)
        following_posts = (Post.objects.filter(user__following__followers=request.user)
            .exclude(user=request.user)
            .annotate(**post_annotations)
            .order_by('-id')
            .select_related(
                "user",
                "user__profile",
                "repost_from__user",
                "repost_from__user__profile",
            ))

    template_name = 'top_authenticated.html' if request.user.is_authenticated else 'top_unauthenticated.html'
    return render(request, template_name,{
        "form":form,
        "object_list":posts,
        "following_posts": following_posts,
    })

def search(request):
    query = request.GET.get("q", "").strip()
    posts = Post.objects.none()
    users = User.objects.none()

    if query:
        posts = Post.objects.filter(
            Q(content__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__display_name__icontains=query)
        ).order_by("-id").select_related(
            "user",
            "user__profile",
            "repost_from__user",
            "repost_from__user__profile",
        )
        post_annotations = get_post_annotations(request.user)
        if post_annotations:
            posts = posts.annotate(**post_annotations)

        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(display_name__icontains=query)
            | Q(profile__introduce_content__icontains=query)
        ).select_related("profile").order_by("username")

    return render(request, "search.html", {
        "query": query,
        "posts": posts,
        "users": users,
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
    posts = Post.objects.filter(user=profile.user).order_by('-created_at').select_related(
        "user",
        "user__profile",
        "repost_from__user",
        "repost_from__user__profile",
    )
    media_posts = Post.objects.filter(user=profile.user, image__isnull=False).exclude(image="").order_by('-created_at').select_related(
        "user",
        "user__profile",
        "repost_from__user",
        "repost_from__user__profile",
    )
    liked_posts = Post.objects.filter(likes__user=profile.user).order_by('-likes__created_at').select_related(
        "user",
        "user__profile",
        "repost_from__user",
        "repost_from__user__profile",
    )
    replies = (Comment.objects.filter(user=profile.user)
        .select_related("user", "user__profile", "post", "post__user")
        .order_by("-created_at"))

    if request.user.is_authenticated:
        post_annotations = {
            "is_liked": Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
            "is_repost": Exists(Post.objects.filter(user=request.user,repost_from=OuterRef("pk"))),
            "is_following": Exists(Relation.objects.filter(followers=request.user,followings=OuterRef("user_id"))),
            "is_bookmarked": Exists(Bookmark.objects.filter(user=request.user, post=OuterRef('pk'))),
        }
        posts = posts.annotate(**post_annotations)
        media_posts = media_posts.annotate(**post_annotations)
        liked_posts = liked_posts.annotate(**post_annotations)

    context = {
        "profile": profile,
        "object_list": posts,
        "media_posts": media_posts,
        "liked_posts": liked_posts,
        "replies": replies,
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
            ),
            is_bookmarked=Exists(Bookmark.objects.filter(user=request.user, post=OuterRef('pk')))
            ).first()
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
            if post.user != request.user:
                Notification.objects.create(
                    to_user=post.user,
                    from_user=request.user,
                    post=post,
                    comment=new_comment,
                    notification_type=Notification.COMMENT,
                )

                send_notification_email(
                    to_user=post.user,
                    from_user=request.user,
                    notification_type="comment",
                    extra_text=new_comment.content
                )
            return redirect('twitter_app:post_detail', post_id=post.id)
    else:
        form = CommentForm()
        comments = (
        post.comments
        .select_related("user", "user__profile")
        .order_by('-created_at')
    )

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
    else:
        if post.user != request.user:
            Notification.objects.create(
                to_user=post.user,
                from_user=request.user,
                post=post,
                notification_type=Notification.LIKE
            )

            send_notification_email(
                to_user=post.user,
                from_user=request.user,
                notification_type='like'
            )
    
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
    relation, created = Relation.objects.get_or_create(followers=request.user,followings=user_to_follow)

    if created and user_to_follow !=request.user:
        Notification.objects.create(
            to_user=user_to_follow,
            from_user=request.user,
            notification_type=Notification.FOLLOW,
        )

        send_notification_email(
            to_user=user_to_follow,
            from_user=request.user,
            notification_type='follow'
        )

    return redirect(request.META.get('HTTP_REFERER') or reverse('twitter_app:top'))

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
        Conversation.objects
        .filter(participants=request.user)
        .order_by('-updated_at')
        .prefetch_related(
            Prefetch(
                'participants',
                queryset=User.objects.select_related('profile')
            ) ,
            'messages'
        )
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
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )

            Conversation.objects.filter(id=conversation.id).update(
                updated_at=message.created_at
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

@login_required
def notification_list(request):
    notifications =(
        request.user.notifications
        .select_related('from_user', 'post', 'comment')
        .order_by('-created_at')
    )
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notification_list.html',{
        'notifications': notifications
    })
