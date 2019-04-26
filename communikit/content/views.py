from django.views.generic import ListView

from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post


class PostListView(CommunityRequiredMixin, ListView):
    paginate_by = 12

    def get_queryset(self):
        return (
            Post.objects.filter(community=self.request.community)
            .order_by("-created")
            .select_related("author", "community")
            .select_subclasses()
        )


post_list_view = PostListView.as_view()
