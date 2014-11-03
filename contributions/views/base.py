from projects.models import Project
from dataviews.models import View
from contributions.models import Observation


class SingleAllContribution(object):
    def get_object(self, user, project_id, observation_id):
        project = Project.objects.get_single(user, project_id)

        if project.can_moderate(user):
            return project.get_all_contributions(
                user).for_moderator(user).get(pk=observation_id)
        else:
            return project.get_all_contributions(
                user).for_viewer(user).get(pk=observation_id)


class SingleGroupingContribution(object):
    def get_object(self, user, project_id, view_id, observation_id):
        view = View.objects.get_single(user, project_id, view_id)

        if view.project.can_moderate(user):
            return view.data.for_moderator(user).get(pk=observation_id)
        else:
            return view.data.for_viewer(user).get(pk=observation_id)


class SingleMyContribution(object):
    def get_object(self, user, project_id, observation_id):
        observation = Project.objects.get_single(
            user, project_id).observations.get(pk=observation_id)

        if observation.creator == user:
            return observation
        else:
            raise Observation.DoesNotExist('You are not the creator of this '
                                           'contribution or the contribution '
                                           'has been deleted.')