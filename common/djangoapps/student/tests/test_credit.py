"""
Tests for credit courses on the student dashboard.
"""
import unittest
import datetime

from mock import patch
import pytz

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from student.models import CourseEnrollmentAttribute
from student.tests.factories import UserFactory, CourseEnrollmentFactory

from openedx.core.djangoapps.credit.models import CreditCourse, CreditProvider, CreditEligibility
from openedx.core.djangoapps.credit import api as credit_api


TEST_CREDIT_PROVIDER_SECRET_KEY = "931433d583c84ca7ba41784bad3232e6"


@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
@override_settings(CREDIT_PROVIDER_SECRET_KEYS={
    "hogwarts": TEST_CREDIT_PROVIDER_SECRET_KEY,
})
@patch.dict(settings.FEATURES, {"ENABLE_CREDIT_ELIGIBILITY": True})
class CreditCourseDashboardTest(ModuleStoreTestCase):
    """
    Tests for credit courses on the student dashboard.
    """

    USERNAME = "ron"
    PASSWORD = "mobiliarbus"

    PROVIDER_ID = "hogwarts"
    PROVIDER_NAME = "Hogwarts School of Witchcraft and Wizardry"
    PROVIDER_STATUS_URL = "http://credit.example.com/status"

    def setUp(self):
        """Create a course and an enrollment. """
        super(CreditCourseDashboardTest, self).setUp()

        # Create a user and log in
        self.user = UserFactory.create(username=self.USERNAME, password=self.PASSWORD)
        result = self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.assertTrue(result, msg="Could not log in")

        # Create a course and configure it as a credit course
        self.course = CourseFactory()
        CreditCourse.objects.create(course_key=self.course.id, enabled=True)  # pylint: disable=no-member

        # Configure a credit provider
        CreditProvider.objects.create(
            provider_id=self.PROVIDER_ID,
            display_name=self.PROVIDER_NAME,
            provider_status_url=self.PROVIDER_STATUS_URL,
            enable_integration=True,
        )

        # Configure a single credit requirement (minimum passing grade)
        credit_api.set_credit_requirements(
            self.course.id,  # pylint: disable=no-member
            [
                {
                    "namespace": "grade",
                    "name": "grade",
                    "display_name": "Final Grade",
                    "criteria": {
                        "min_grade": 0.8
                    }
                }
            ]
        )

        # Enroll the user in the course as "verified"
        self.enrollment = CourseEnrollmentFactory(
            user=self.user,
            course_id=self.course.id,  # pylint: disable=no-member
            mode="verified"
        )

    def test_not_eligible_for_credit(self):
        # The user is not yet eligible for credit, so no additional information should be displayed on the dashboard.
        response = self._load_dashboard()
        self.assertNotContains(response, "credit")

    def test_eligible_for_credit(self):
        # Simulate that the user has completed the only requirement in the course
        # so the user is eligible for credit.
        self._make_eligible()

        # The user should have the option to purchase credit
        response = self._load_dashboard()
        self.assertContains(response, "credit-eligibility-msg")
        self.assertContains(response, "purchase-credit-btn")

        # Move the eligibility deadline so it's within 30 days
        eligibility = CreditEligibility.objects.get(username=self.USERNAME)
        eligibility.deadline = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=29)
        eligibility.save()

        # The user should still have the option to purchase credit,
        # but there should also be a message urging the user to purchase soon.
        response = self._load_dashboard()
        self.assertContains(response, "credit-eligibility-msg")
        self.assertContains(response, "purchase-credit-btn")
        self.assertContains(response, "purchase credit for this course expires")

    def test_purchased_credit(self):
        # Simulate that the user has purchased credit, but has not
        # yet initiated a request to the credit provider
        self._make_eligible()
        self._purchase_credit()

        # Expect that the user's status is "pending"
        response = self._load_dashboard()
        self.assertContains(response, "credit-request-pending-msg")

    def test_purchased_credit_and_request_pending(self):
        # Simulate that the user has purchased credit and initiated a request,
        # but we haven't yet heard back from the credit provider.
        self._make_eligible()
        self._purchase_credit()
        self._initiate_request()

        # Expect that the user's status is "pending"
        response = self._load_dashboard()
        self.assertContains(response, "credit-request-pending-msg")

    def test_purchased_credit_and_request_approved(self):
        # Simulate that the user has purchased credit and initiated a request,
        # and had that request approved by the credit provider
        self._make_eligible()
        self._purchase_credit()
        request_uuid = self._initiate_request()
        self._set_request_status(request_uuid, "approved")

        # Expect that the user's status is "approved"
        response = self._load_dashboard()
        self.assertContains(response, "credit-request-approved-msg")

    def test_purchased_credit_and_request_rejected(self):
        # Simulate that the user has purchased credit and initiated a request,
        # and had that request rejected by the credit provider
        self._make_eligible()
        self._purchase_credit()
        request_uuid = self._initiate_request()
        self._set_request_status(request_uuid, "rejected")

        # Expect that the user's status is "approved"
        response = self._load_dashboard()
        self.assertContains(response, "credit-request-rejected-msg")

    def test_credit_status_error(self):
        # Simulate an error condition: the user has a credit enrollment
        # but no enrollment attribute indicating which provider the user
        # purchased credit from.
        self._make_eligible()
        self._purchase_credit()
        CourseEnrollmentAttribute.objects.all().delete()

        # Expect an error message
        response = self._load_dashboard()
        self.assertContains(response, "credit-error-msg")

    def _load_dashboard(self):
        """Load the student dashboard and return the HttpResponse. """
        return self.client.get(reverse("dashboard"))

    def _make_eligible(self):
        """Make the user eligible for credit in the course. """
        credit_api.set_credit_requirement_status(
            self.USERNAME,
            self.course.id,  # pylint: disable=no-member
            "grade", "grade",
            status="satisfied",
            reason={
                "final_grade": 0.95
            }
        )

    def _purchase_credit(self):
        """Purchase credit from a provider in the course. """
        self.enrollment.mode = "credit"
        self.enrollment.save()  # pylint: disable=no-member

        CourseEnrollmentAttribute.objects.create(
            enrollment=self.enrollment,
            namespace="credit",
            name="provider_id",
            value=self.PROVIDER_ID,
        )

    def _initiate_request(self):
        """Initiate a request for credit from a provider. """
        request = credit_api.create_credit_request(
            self.course.id,  # pylint: disable=no-member
            self.PROVIDER_ID,
            self.USERNAME
        )
        return request["parameters"]["request_uuid"]

    def _set_request_status(self, uuid, status):
        """Set the status of a request for credit, simulating the notification from the provider. """
        credit_api.update_credit_request_status(uuid, self.PROVIDER_ID, status)
