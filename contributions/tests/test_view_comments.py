import json
from rest_framework.test import APITestCase

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import UserF, UserGroupF, ProjectF
from dataviews.tests.model_factories import ViewFactory, ViewGroupFactory

from .model_factories import ObservationFactory, CommentFactory
from ..views import Comments, SingleComment
from ..models import Observation


class GetComments(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })
        comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        response = CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': response
        })
        CommentFactory.create(**{
            'commentto': self.observation,
            'respondsto': comment
        })
        CommentFactory.create(**{
            'commentto': self.observation
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id)
        )
        force_authenticate(request, user=user)
        view = Comments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_get_comments_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddCommentToPrivateProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = Comments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not allowed to access this project.'
        )

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not eligable to contribute data to this project'
        )


class AddCommentToPrivateAllContributeProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'everyonecontributes': True,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = Comments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not allowed to access this project.'
        )

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToPublicProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'isprivate': False,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = Comments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not eligable to contribute data to this project'
        )

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not eligable to contribute data to this project'
        )


class AddCommentToPublicAllContributeProjectTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (self.project.id, self.observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = Comments.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id
        ).render()

    def test_add_comment_to_observation_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_contributor(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_non_member(self):
        response = self.get_response(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_observation_with_view_member(self):
        view_member = UserF.create()
        ViewGroupFactory(add_users=[view_member], **{
            'view': ViewFactory(**{
                'project': self.project
            })
        })
        response = self.get_response(view_member)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AddCommentToInactiveProject(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'status': 'inactive',
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create(**{
            'project': project
        })

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are not allowed to access this project.'
        )


class AddCommentToDeletedProject(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'status': 'deleted',
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create(**{
            'project': project
        })

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddCommentToWrongObservation(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddResponseToCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create(**{
            'commentto': observation
        })

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('respondsto'),
            comment.id
        )


class AddResponseToWrongCommentTest(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.post(
            '/api/projects/%s/observations/%s/comments/' %
            (project.id, observation.id),
            {
                'text': 'Response to a comment',
                'respondsto': comment.id
            }
        )
        force_authenticate(request, user=admin)
        view = Comments.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'The comment you try to respond to is not a comment to the '
            'observation.'
        )


class DeleteCommentTest(APITestCase):
    def setUp(self):
        self.contributor = UserF.create()
        self.admin = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF.create(**{
            'isprivate': False,
            'everyonecontributes': True,
            'admins': UserGroupF(add_users=[self.admin]),
            'contributors': UserGroupF(add_users=[self.contributor]),
        })
        self.observation = ObservationFactory.create(**{
            'project': self.project
        })
        self.comment = CommentFactory.create(**{
            'commentto': self.observation
        })
        self.comment_to_remove = CommentFactory.create(**{
            'commentto': self.observation,
            'creator': self.contributor
        })

    def get_response(self, user):
        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/observations/%s/comments/%s/' %
            (self.project.id, self.observation.id, self.comment_to_remove.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=user)
        view = SingleComment.as_view()
        return view(
            request,
            project_id=self.project.id,
            observation_id=self.observation.id,
            comment_id=self.comment_to_remove.id
        ).render()

    def test_delete_comment_with_admin(self):
        response = self.get_response(self.admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_comment_creator(self):
        response = self.get_response(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertNotIn(self.comment_to_remove, observation.comments.all())

    def test_delete_comment_with_view_member(self):
        response = self.get_response(self.non_member)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content).get('error'),
            'You are neither the author if this comment nor a project '
            'administrator and therefore not eligable to delete this comment.'
        )

        observation = Observation.objects.get(pk=self.observation.id)
        self.assertIn(self.comment, observation.comments.all())
        self.assertIn(self.comment_to_remove, observation.comments.all())


class DeleteWrongComment(APITestCase):
    def test(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'admins': UserGroupF(add_users=[admin])
        })
        observation = ObservationFactory.create(**{
            'project': project
        })
        comment = CommentFactory.create()

        factory = APIRequestFactory()
        request = factory.delete(
            '/api/projects/%s/observations/%s/comments/%s/' %
            (project.id, observation.id, comment.id),
            {'text': 'A comment to the observation'}
        )
        force_authenticate(request, user=admin)
        view = SingleComment.as_view()
        response = view(
            request,
            project_id=project.id,
            observation_id=observation.id,
            comment_id=comment.id
        ).render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
