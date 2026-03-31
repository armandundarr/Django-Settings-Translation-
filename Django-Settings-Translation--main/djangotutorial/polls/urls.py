from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("<int:question_id>/comment/", views.add_comment, name="add_comment"),
    path("register/", views.register, name="register"),
    path("create/", views.create_poll, name="create"),
    path("leaderboard/", views.LeaderboardView.as_view(), name="leaderboard"),
    path("<int:question_id>/api/results/", views.poll_results_api, name="results_api"),
    path("<int:question_id>/react/", views.add_reaction, name="add_reaction"),
    path("api/ai-suggest/", views.ai_suggest_choices, name="ai_suggest"),
    path("<int:question_id>/api/timeline/", views.poll_timeline_api, name="timeline_api"),
    # New Features 7 & 8
    path("<int:question_id>/chat/feed/", views.poll_chat_feed, name="chat_feed"),
    path("<int:question_id>/chat/send/", views.send_chat_message, name="chat_send"),
    path("<int:question_id>/share/image.png", views.poll_share_image, name="share_image"),
]
