from django.conf.urls import patterns
from django.conf.urls import url

from astutedashboard.dashboards.project.subscribed_plans import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<id>[^/]+)/plan_details/$', views.UserSubPlanDetailsView.as_view(), name='user_sub_plan_details'),
)
