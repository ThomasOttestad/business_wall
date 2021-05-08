from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import UpdateView,ListView
from django.db.models import Count
from business_wall.settings import MEDIA_ROOT, MEDIA_URL
from userprofile.models import Avatar
from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm, BoardForm
from departments.models import Department

@login_required
def board_home(request):
    groups = request.user.groups.filter(name="supervisor")

    if len(groups) > 0:
        boardquery = Board.objects.all()
        supervisor = True
    else:
        queryset = Department.objects.exclude(users=request.user)
        boardquery = Board.objects.exclude(pk__in=[q.board.pk for q in queryset])
        supervisor = False

    context = {'boards': boardquery, 'supervisor': supervisor}
    return render(request, 'boards.html', context)

@login_required
def new_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = Board.objects.create(
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
            )
            return redirect('board_topics', pk=board.pk)
    form = BoardForm()
    return render(request, 'new_board.html', {'form': form})

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.original_poster = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})

@login_required
def topic_posts(request, pk, topic_pk):
    topics = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic, 'avatars': avatars})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.reply = True
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

@method_decorator(login_required, name='dispatch')
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))

        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

        return queryset

@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    # paginate_by = 4

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))

        queryset = self.topic.posts.order_by('-created_at')
        return queryset

@login_required
def delete_comfirm(request, post_pk):
    post = get_object_or_404(Post, id=post_pk)

    return render(request, 'delete_post.html', {'post': post})

@login_required
def delete(request):
    postpk = request.POST['post_pk']
    topicpk = request.POST['topic_pk']

    if request.method == 'POST':
        post = get_object_or_404(Post, id=postpk)

        #this test is a double check for ensuring that the only one who can delete a message is the owner.
        #is already handled by inline python in html, but this ensures that you cannot send a custom form and delete message when not owner.
        if post.created_by != request.user:
            return render(request, 'delete_failure.html', status=401)

        if post.reply == False:
            topic = get_object_or_404(Topic, id=topicpk)
            topic.delete()
        try:
            post.delete()
        except:
            print("except")

    return redirect('board_home')

@login_required
def pinned(request):
    queryset = Topic.objects.filter(pinned=True).order_by('-last_updated').annotate(replies=Count('posts') - 1)

    return render(request, 'pinned_topics.html', {'topics': queryset})
