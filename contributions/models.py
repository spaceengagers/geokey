from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core.exceptions import ValidationError

from django_hstore import hstore
from simple_history.models import HistoricalRecords

from core.exceptions import InputError

from .base import LOCATION_STATUS, OBSERVATION_STATUS, COMMENT_STATUS
from .manager import LocationManager, ObservationManager, CommentManager


class Location(models.Model):
    """
    Represents a location to which an arbitrary number of observations can be
    attached.
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    geometry = gis.GeometryField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    version = models.IntegerField(default=1)
    private = models.BooleanField(default=False)
    private_for_project = models.ForeignKey('projects.Project', null=True)
    status = models.CharField(
        choices=LOCATION_STATUS,
        default=LOCATION_STATUS.active,
        max_length=20
    )

    objects = LocationManager()


class Observation(models.Model):
    """
    Stores a single observation.
    """
    location = models.ForeignKey('Location', related_name='locations')
    project = models.ForeignKey(
        'projects.Project', related_name='observations'
    )
    observationtype = models.ForeignKey('observationtypes.ObservationType')
    status = models.CharField(
        choices=OBSERVATION_STATUS,
        default=OBSERVATION_STATUS.active,
        max_length=20
    )
    review_comment = models.TextField(blank=True, null=True)
    attributes = hstore.DictionaryField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='creator'
    )
    updator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updator',
        null=True
    )
    version = models.IntegerField(default=1)

    history = HistoricalRecords()
    objects = ObservationManager()

    @classmethod
    def create(cls, attributes=None, creator=None, location=None,
               observationtype=None, project=None):
        """
        Creates a new observation. Validates all fields first and raises a
        ValidationError if at least one field did not validate.
        Creates the object if all fields are valid.
        """
        is_valid = True
        error_messages = []

        for field in observationtype.fields.all():
            try:
                field.validate_input(attributes.get(field.key))
            except InputError, error:
                is_valid = False
                error_messages.append(error)

        if is_valid:
            location.save()
            observation = cls.objects.create(
                location=location,
                observationtype=observationtype,
                project=project,
                attributes=attributes,
                creator=creator
            )
            return observation
        else:
            raise ValidationError(error_messages)

    def validate_update(self, data):
        is_valid = True
        error_messages = []

        for field in self.observationtype.fields.all():
            if field.key in data:
                try:
                    field.validate_input(data.get(field.key))
                except InputError, error:
                    is_valid = False
                    error_messages.append(error)

        if not is_valid:
            raise ValidationError(error_messages)

    def update(self, attributes, updator, review_comment=None, status=None):
        version = self.version + 1

        update = self.attributes.copy()
        update.update(attributes)

        self.validate_update(update)

        self.attributes = update
        self.version = version
        self.updator = updator

        self.review_comment = review_comment
        self.status = status or self.status

        self.save()

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = OBSERVATION_STATUS.deleted
        self.save()


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    commentto = models.ForeignKey('Observation', related_name='comments')
    respondsto = models.ForeignKey('Comment', null=True, blank=True,
                                   related_name='responses')
    status = models.CharField(
        choices=COMMENT_STATUS,
        default=COMMENT_STATUS.active,
        max_length=20
    )

    objects = CommentManager()

    def delete(self):
        """
        Deletes the comment by setting it's `status` to `DELETED`
        """
        self.status = COMMENT_STATUS.deleted
        self.save()
