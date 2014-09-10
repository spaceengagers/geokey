from django.conf.urls import patterns, url

from projects import views as project_views
from observationtypes import views as observationtypes_views
from dataviews import views as view_views
from users import views as user_views
from applications import views as app_views

urlpatterns = patterns(
    '',
    # ###########################
    # PROJECTS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/$',
        project_views.ProjectUpdate.as_view(),
        name='project'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/admins/$',
        project_views.ProjectAdmins.as_view(),
        name='project_admins'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/admins/(?P<user_id>[0-9]+)/$',
        project_views.ProjectAdminsUser.as_view(),
        name='project_admins_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/$',
        user_views.UserGroup.as_view(),
        name='usergroup'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/$',
        user_views.UserGroupUsers.as_view(),
        name='usergroup_users'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/users/(?P<user_id>[0-9]+)/$',
        user_views.UserGroupSingleUser.as_view(),
        name='usergroup_single_user'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/views/$',
        user_views.UserGroupViews.as_view(),
        name='usergroup_views'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/views/(?P<view_id>[0-9]+)/$',
        user_views.UserGroupSingleView.as_view(),
        name='usergroup_single_view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/usergroups/(?P<group_id>[0-9]+)/views/all-contributions/$',
        user_views.UserGroupAllContributionsView.as_view(),
        name='usergroup_allcontributions_view'),

    # ###########################
    # OBSERVATION TYPES & FIELDS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/$',
        observationtypes_views.ObservationTypeUpdate.as_view(),
        name='observationtype'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/check-key/$',
        observationtypes_views.FieldKeyCheck.as_view(),
        name='key_check'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/$',
        observationtypes_views.FieldUpdate.as_view(),
        name='observationtype_field'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/$',
        observationtypes_views.FieldLookups.as_view(),
        name='observationtype_lookupvalues'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/observationtypes/(?P<observationtype_id>[0-9]+)/fields/(?P<field_id>[0-9]+)/lookupvalues/(?P<value_id>[0-9]+)/$',
        observationtypes_views.FieldLookupsUpdate.as_view(),
        name='observationtype_lookupvalues_detail'),

    # ###########################
    # VIEWS
    # ###########################
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/(?P<view_id>[0-9]+)/$',
        view_views.ViewUpdate.as_view(),
        name='view'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/views/all-contributions/$',
        view_views.AllContributionsViewUpdate.as_view(),
        name='all_contributions_view'),

    # ###########################
    # USER
    # ###########################
    url(r'^users/$', user_views.QueryUsers.as_view(), name='users_users'),
)
