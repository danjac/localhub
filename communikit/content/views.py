from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import Count, Prefetch, QuerySet
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from notifications.models import Notification
from notifications.signals import notify

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.content import app_settings
from communikit.content.forms import PostForm
from communikit.content.models import Post
from communikit.types import ContextDict
from communikit.users.views import ProfileUserMixin


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Post.objects.filter(
            community=self.request.community
        ).select_related("author", "community")


class PostCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):

    model = Post
    form_class = PostForm
    permission_required = "content.create_post"
    success_url = reverse_lazy("content:list")

    def get_permission_object(self) -> Community:
        return self.request.community

    def notify(self):

        members = self.request.community.members.all().exclude(
            pk=self.request.user.pk
        )

        notify.send(
            self.request.user,
            recipient=members,
            verb="post_created",
            action_object=self.object,
            target=self.request.community,
        )

        mentions = self.object.extract_mentions()

        if mentions:
            notify.send(
                self.request.user,
                recipient=members.filter(username__in=mentions),
                verb="post_mentioned",
                action_object=self.object,
                target=self.request.community,
            )

    def form_valid(self, form) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.community = self.request.community
        self.object.save()

        self.notify()

        messages.success(self.request, _("Your update has been posted"))
        return HttpResponseRedirect(self.get_success_url())


post_create_view = PostCreateView.as_view()


class PostListView(CommunityPostQuerySetMixin, ListView):
    paginate_by = app_settings.PAGINATE_BY
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_comments=Count("comment"), num_likes=Count("likes"))
            .order_by("-created")
            .select_subclasses()
        )


post_list_view = PostListView.as_view()


class PostSearchView(CommunityPostQuerySetMixin, ListView):
    template_name = "content/search.html"

    def get_queryset(self) -> QuerySet:

        hashtag = self.request.GET.get("hashtag", "").strip()
        if hashtag:
            self.query = "#" + hashtag
        else:
            self.query = self.request.GET.get("q", "").strip()

        if not self.query:
            return Post.objects.none()
        search_vector = SearchVector("title", "description")
        search_query = SearchQuery(self.query)
        return (
            super()
            .get_queryset()
            .annotate(
                num_comments=Count("comment"),
                num_likes=Count("likes"),
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
            )
            .filter(search=search_query)
            .order_by("-rank")
            .select_subclasses()
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data.update({"search_query": self.query})
        return data


post_search_view = PostSearchView.as_view()


class ProfilePostListView(ProfileUserMixin, ListView):
    paginate_by = app_settings.PAGINATE_BY
    allow_empty = True

    template_name = "content/profile_post_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            Post.objects.filter(
                author=self.object, community=self.request.community
            )
            .annotate(num_comments=Count("comment"), num_likes=Count("likes"))
            .order_by("-created")
            .select_subclasses()
        )


profile_post_list_view = ProfilePostListView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, DetailView):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_comments=Count("comment"), num_likes=Count("likes"))
            .prefetch_related(
                Prefetch(
                    "comment_set",
                    to_attr="comments",
                    queryset=Comment.objects.select_related(
                        "author", "post", "post__community"
                    )
                    .annotate(num_likes=Count("likes"))
                    .order_by("created"),
                )
            )
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data


post_detail_view = PostDetailView.as_view()


class PostUpdateView(
    LoginRequiredMixin, CommunityPostQuerySetMixin, UpdateView
):
    form_class = PostForm
    permission_required = "content.change_post"


post_update_view = PostUpdateView.as_view()


class PostDeleteView(
    LoginRequiredMixin,
    CommunityPostQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    permission_required = "content.delete_post"
    success_url = reverse_lazy("content:list")

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.get_success_url())


post_delete_view = PostDeleteView.as_view()


class PostLikeView(
    LoginRequiredMixin,
    CommunityPostQuerySetMixin,
    PermissionRequiredMixin,
    SingleObjectMixin,
    View,
):
    permission_required = "content.like_post"

    def post(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        is_liked = self.object.like(request.user)
        if is_liked:
            notify.send(
                self.request.user,
                recipient=self.object.author,
                verb="post_liked",
                action_object=self.object,
                target=self.request.community,
            )
        if request.is_ajax():
            return JsonResponse(
                {"status": _("Unlike") if is_liked else _("Like")}
            )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


post_like_view = PostLikeView.as_view()


class ActivityView(LoginRequiredMixin, CommunityRequiredMixin, TemplateView):
    template_name = "content/activity.html"

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)

        # TBD: performance here is horrible, fix duplicate queries etc
        data["notifications"] = Notification.objects.filter(
            recipient=self.request.user,
            target_content_type=ContentType.objects.get_for_model(
                self.request.community
            ),
            target_object_id=self.request.community.id,
        )
        return data


activity_view = ActivityView.as_view()
