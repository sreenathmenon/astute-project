from django.conf.urls import patterns
from django.conf.urls import url

from astutedashboard.dashboards.project.available_plans import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<id>[^/]+)/plan_details/$', views.UserAvblPlanDetailsView.as_view(), name='user_avbl_plan_details'),
    url(r'^(?P<id>[^/]+)/activate_plan/$',views.PlanActivationByUserView.as_view(),name='activate_user_plan'),
)
