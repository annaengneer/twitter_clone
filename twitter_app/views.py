from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q, Prefetch
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.utils import timezone
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

def calm_character(request):
    mood_options = [
        {"id": "tired", "label": "ちょっと疲れた"},
        {"id": "anxious", "label": "不安"},
        {"id": "foggy", "label": "もやもやする"},
        {"id": "sleepy", "label": "眠い"},
        {"id": "worked", "label": "今日頑張れた"},
        {"id": "beforePost", "label": "投稿前に落ち着きたい"},
        {"id": "talk", "label": "誰かに話したい"},
        {"id": "refresh", "label": "気分を切り替えたい"},
        {"id": "good", "label": "いい感じ"},
    ]
    calm_characters = [
        {
            "id": "rabbit",
            "name": "らん",
            "image": "rabit.png",
            "theme": "rabbit",
            "message": "らんらん♪ 楽しい気持ちを少し足して、前向きな一日にしよう",
            "hero_title": "らんと、今日の小さな楽しみを見つけよう",
            "hero_description": "気持ちが揺れたら、楽しい方へ少しだけ目を向ける場所だよ。無理に元気にならなくていいから、今できそうな小さなことから始めよう。",
            "fortune_title": "小さな楽しみが見つかりやすい日",
            "lucky_items": [
                "あたたかい飲み物",
                "お気に入りの曲",
                "小さなメモ帳",
                "甘いおやつ",
                "明るい色の小物",
                "お気に入りの画像",
                "窓ぎわの光",
            ],
            "tiny_joys": [
                "好きな曲を1曲だけ聴く",
                "あたたかい飲み物を作る",
                "肩をゆっくり3回まわす",
                "今日よかったことを1つだけメモする",
                "5分だけ好きなことをする時間を決める",
                "自分に短いほめ言葉を書く",
                "次にやることを一番軽い形にする",
            ],
            "daily_messages": [
                "らんらん♪ 小さく楽しいことをひとつ見つけよう",
                "今日は前向きな気持ちを少しだけ足してみよう",
                "やさしい言葉をひとつ、自分にも向けてあげよう",
                "小さな休憩も、明日の楽しい気持ちにつながるよ",
                "深呼吸できたら、それだけで気持ちは少し明るくなる",
                "あたたかい飲み物みたいに、心をゆっくりほどこう",
                "今日は少しだけ自分に甘くしてもいい日",
                "うまく話せない気持ちも、ここに置いていっていいよ",
                "ひと息つけたら、それだけでちゃんと前に進んでる",
                "楽しい方を選べる余白を、少しだけ残しておこう",
            ],
            "responses": {
                "tired": "今日もおつかれさま。らんと一緒に、まずは楽な方へ少し寄ろう",
                "anxious": "不安があるんだね。大丈夫、らんらん♪って言えるくらいまで少しずつ戻ろう",
                "foggy": "もやもやは急に消さなくて大丈夫。楽しい小物をひとつ思い出すだけでも軽くなるよ",
                "sleepy": "眠い日は体が休みたいサインかも。ちょっと休んだら、また明るい方へ行こう",
                "worked": "頑張れた日だね。その一歩、らんはちゃんと前向きポイントだと思う",
                "beforePost": "投稿前に立ち止まれたの、すごくいいね。言葉を少しだけ明るく整えてみよう",
                "talk": "話したい気持ちがあるんだね。まずは一文だけ、らんに預ける感じで出してみよう",
                "refresh": "切り替えたい時は、楽しいことをひとつ足そう。好きな曲を1曲だけでもいいよ",
                "good": "いい感じの日だね。らんらん♪ その軽さを大事に進もう",
            },
        },
        {
            "id": "hedgehog",
            "name": "のん",
            "image": "harinezumi2.png",
            "theme": "hedgehog",
            "message": "のんびりいこう 焦らなくて大丈夫、自分のペースを大切にしよう",
            "hero_title": "のんと、自分のペースに戻ろう",
            "hero_description": "焦りそうな時に、少し立ち止まって安心できる距離を選ぶ場所だよ。急がなくていいから、今の気持ちをゆっくり見ていこう。",
            "fortune_title": "焦らず進むほど整いやすい日",
            "lucky_items": [
                "小さなノート",
                "落ち着く色のペン",
                "あたたかい靴下",
                "静かな音楽",
                "手になじむマグカップ",
                "通知オフのスマホ",
                "やらないことメモ",
            ],
            "tiny_joys": [
                "机の上をひとつだけ片付ける",
                "通知を少しだけ閉じる",
                "今やらないことを1つ決める",
                "落ち着く飲み物をゆっくり飲む",
                "ひとことだけメモに書く",
                "安心できる場所に少し移動する",
                "返事を少し後にする",
            ],
            "daily_messages": [
                "のんびり進む日があっても大丈夫",
                "焦らなくていい 自分のペースを大切にしよう",
                "今日はここまで、って決められるのも立派な前進",
                "心がちくちくする日は、安心できる距離を選ぼう",
                "落ち着いて見直す時間は、ちゃんとあなたを守ってくれるよ",
                "急いで返さなくてもいい 言葉は少し置くと見え方が変わる",
                "自分の気持ちを守る選択も、ちゃんとやさしさだよ",
                "今日は静かに整える日でもいい",
                "無理に強くならなくていい まずは安全な場所を選ぼう",
                "迷ったら一歩引いて見てみる それも十分いい判断",
            ],
            "responses": {
                "tired": "疲れた日は、無理に元気なふりをしなくていいよ。のんびり休む方を選ぼう",
                "anxious": "不安な時は、決めることを少し減らそう。のんと一緒に、今はひとつだけでいい",
                "foggy": "もやもやしてるなら、すぐ答えを出さなくていい。少し置いてから見よう",
                "sleepy": "眠い時は判断も重くなるよ。大事なことは起きてからでも遅くない",
                "worked": "今日できたことを、静かに認めてあげよう。自分のペースで進めたの、ちゃんといい",
                "beforePost": "その投稿、今の気持ちを守りながら届けられそう？のんびり一回読み直そ",
                "talk": "誰かに話したい時は、全部きれいに言えなくていい 最初の一言だけ考えよう",
                "refresh": "切り替えたい時は、足元に意識を戻してみよう。のんびり戻れたら十分",
                "good": "いい感じなら、そのペースを守ろう。調子がいい日ほど無理しすぎなくていい",
            },
        },
        {
            "id": "squirrel",
            "name": "るん",
            "image": "squiirrel.png",
            "theme": "squirrel",
            "message": "るんるん♪ 小さな幸せを見つけて、ちょっとワクワクしよう",
            "hero_title": "るんと、小さな幸せを拾おう",
            "hero_description": "気分を少し明るくしたい時に、身近なワクワクを探す場所だよ。大きなことじゃなくていいから、今そばにある小さな楽しみを見つけよう。",
            "fortune_title": "小さな行動がいい流れにつながる日",
            "lucky_items": [
                "カラフルな付箋",
                "冷たい水",
                "歩きやすい靴",
                "小さなお菓子",
                "明るい色のアイコン",
                "5分タイマー",
                "チェックリスト",
            ],
            "tiny_joys": [
                "空を少し見る",
                "水を飲んでから次を始める",
                "小さなおやつを用意する",
                "部屋の一角だけ整える",
                "行きたい場所を1つ思い浮かべる",
                "好きな画像を1枚眺める",
                "できたことを1つだけ数える",
            ],
            "daily_messages": [
                "るんるん♪ 今日の小さな幸せをひとつ見つけよう",
                "気持ちの切り替えは、小さなワクワクから始めても大丈夫",
                "少しでも動けたなら、それは明日の自分へのいい準備だよ",
                "うれしかったことをひとつ拾うだけで、気持ちは少し軽くなる",
                "焦らず、今できる小さな一歩を選んでみよう",
                "水を飲む、立つ、窓を見る 小さな行動で流れは変わるよ",
                "できたことメモをひとつだけ残しておこう",
                "気分が重い時こそ、すぐできる小さいことから始めよう",
                "今の自分に渡せる小さなごほうびを探してみよう",
                "前向きになれない日も、ワクワクの種なら見つかるかも",
            ],
            "responses": {
                "tired": "疲れた時は、今日できた小さなことをひとつだけ拾っておこ。るんが一緒に集めるよ",
                "anxious": "不安な時は、今できる準備をひとつだけ集めよう。小さいので大丈夫",
                "foggy": "もやもやはメモに出すと少し軽くなるよ。単語だけでも置いてみよう",
                "sleepy": "眠いなら、まず休む準備をひとつ。明日の自分が助かるよ",
                "worked": "頑張れた日だね。るんるん♪ 小さな前進をちゃんと集められてる",
                "beforePost": "投稿前に一度見直せたの、いい準備だよ。届けたい気持ちが伝わる形に少し整えよう",
                "talk": "誰かに話したい時は、送る前にメモで一回集めよう。伝えたいことが見えやすくなるよ",
                "refresh": "切り替えるなら、小さなワクワクをひとつ。水を飲む、立つ、窓を見る。そこから始めよう",
                "good": "いい感じなら、その勢いで小さな楽しみをひとつ増やそう。気持ちよく進めるよ",
            },
        },
    ]
    today_ordinal = timezone.localdate().toordinal()

    for index, character in enumerate(calm_characters):
        daily_messages = character["daily_messages"]
        lucky_items = character["lucky_items"]
        tiny_joys = character["tiny_joys"]
        character["daily_message"] = daily_messages[(today_ordinal + index) % len(daily_messages)]
        character["lucky_item"] = lucky_items[(today_ordinal + index * 2) % len(lucky_items)]
        character["tiny_joy"] = tiny_joys[(today_ordinal + index * 3) % len(tiny_joys)]

    return render(request, "calm_character.html", {
        "calm_characters": calm_characters,
        "mood_options": mood_options,
    })

def search(request):
    query = request.GET.get("q", "").strip()
    result_type = request.GET.get("type", "all")
    if result_type not in {"all", "users", "posts"}:
        result_type = "all"

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
        "result_type": result_type,
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
