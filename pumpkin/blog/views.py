from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,\
 PageNotAnInteger

from django.views.generic import ListView
from .forms import EmailPostForm,  CommentForm

from django.core.mail import send_mail

from django.views.decorators.http import require_POST

#функция отправки коментария

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                    id=post_id,
                    status=Post.Status.PUBLISHED)
    
    
    
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
    # Создать объект класса Comment, не сохраняя его в базе данных
     comment = form.save(commit=False)
    # Назначить пост комментарию
     comment.post = post
    # Сохранить комментарий в базе данных
     comment.save()
    return render(request, 'blog/post/comment.html',
            {'post': post,
            'form': form,
            'comment': comment})




class PostListView(ListView):
 """
 Альтернативное представление списка постов
 """
 queryset = Post.published.all()
 context_object_name = 'posts'
 paginate_by = 3
 template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} рекомендует вам прочесть " \
                      f"{post.title}"
            message = f"Читать {post.title} at {post_url}\n\n" \
                      f" комментарий  от {cd['name']}\': {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})






def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                                status=Post.Status.PUBLISHED,
                                slug=post,
                                publish__year=year,
                                publish__month=month,
                                publish__day=day)
# Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    return render(request,
            'blog/post/detail.html',
            {'post': post,
            'comments': comments,
            'form': form})
