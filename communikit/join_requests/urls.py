from django.urls import path

from communikit.join_requests.views import (
    join_request_create_view,
    join_request_list_view,
    join_request_accept_view,
    join_request_reject_view,
)

app_name = "join_requests"
