# UrbanSite/tests/test_models.py
"""
Unit tests for UrbanSite models: Authority, UserReport, and Feedback.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from UrbanSite.models import Authority, UserReport, Feedback

User = get_user_model()


class AuthorityModelTest(TestCase):
    """Test cases for Authority model."""

    def setUp(self):
        """Set up test data."""
        self.authority = Authority.objects.create(
            name="Ahmedabad Municipal Corporation",
            email="amc@ahmedabad.gov.in",
            phone="+919876543210",
            area="Navrangpura",
            department="Roads",
            is_active=True
        )

    def test_authority_creation(self):
        """Test that Authority object is created correctly."""
        self.assertIsNotNone(self.authority.pk)
        self.assertEqual(self.authority.name, "Ahmedabad Municipal Corporation")
        self.assertEqual(self.authority.email, "amc@ahmedabad.gov.in")
        self.assertEqual(self.authority.area, "Navrangpura")
        self.assertEqual(self.authority.department, "Roads")
        self.assertTrue(self.authority.is_active)

    def test_authority_str_representation(self):
        """Test Authority __str__ method."""
        expected = "Ahmedabad Municipal Corporation - Roads"
        self.assertEqual(str(self.authority), expected)

    def test_authority_default_values(self):
        """Test Authority default values."""
        new_authority = Authority.objects.create(
            name="Test Authority",
            email="test@example.com",
            phone="+919876543211",
            area="Test Area",
            department="Test Dept"
        )
        self.assertTrue(new_authority.is_active)  # Default should be True
        self.assertIsNotNone(new_authority.created_at)
        self.assertIsNotNone(new_authority.updated_at)

    def test_authority_ordering(self):
        """Test Authority ordering by name."""
        authority2 = Authority.objects.create(
            name="B Department",
            email="b@example.com",
            phone="+919876543212",
            area="Area B",
            department="Dept B"
        )
        authorities = list(Authority.objects.all())
        # Should be ordered by name
        self.assertEqual(authorities[0].name, "Ahmedabad Municipal Corporation")
        self.assertEqual(authorities[1].name, "B Department")


class UserReportModelTest(TestCase):
    """Test cases for UserReport model."""

    def setUp(self):
        """Set up test data."""
        self.authority = Authority.objects.create(
            name="Test Authority",
            email="test@example.com",
            phone="+919876543210",
            area="Test Area",
            department="Roads"
        )
        
        self.report = UserReport.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="+919876543211",
            area="Navrangpura",
            pincode="380009",
            problem_type="Roads",
            description="Pothole on the road",
            authority=self.authority,
            status="Pending"
        )

    def test_report_creation(self):
        """Test that UserReport object is created correctly."""
        self.assertIsNotNone(self.report.pk)
        self.assertEqual(self.report.name, "John Doe")
        self.assertEqual(self.report.email, "john@example.com")
        self.assertEqual(self.report.pincode, "380009")
        self.assertEqual(self.report.problem_type, "Roads")
        self.assertEqual(self.report.status, "Pending")
        self.assertEqual(self.report.authority, self.authority)

    def test_report_str_representation(self):
        """Test UserReport __str__ method."""
        str_repr = str(self.report)
        self.assertIn("John Doe", str_repr)
        self.assertIn("Roads", str_repr)
        self.assertIn("Navrangpura", str_repr)

    def test_report_default_values(self):
        """Test UserReport default values."""
        new_report = UserReport.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone="+919876543212",
            area="Satellite",
            pincode="380015",
            problem_type="Water",
            description="Water leakage"
        )
        self.assertEqual(new_report.status, "Pending")  # Default status
        self.assertIsNone(new_report.authority)  # Can be None
        self.assertIsNone(new_report.resolved_at)
        self.assertIsNotNone(new_report.timestamp)
        self.assertIsNotNone(new_report.updated_at)

    def test_report_problem_type_choices(self):
        """Test that problem_type uses valid choices."""
        valid_choices = [choice[0] for choice in UserReport.PROBLEM_TYPE_CHOICES]
        self.assertIn(self.report.problem_type, valid_choices)

    def test_report_status_choices(self):
        """Test that status uses valid choices."""
        valid_choices = [choice[0] for choice in UserReport.STATUS_CHOICES]
        self.assertIn(self.report.status, valid_choices)

    def test_report_ordering(self):
        """Test that reports are ordered by timestamp (newest first)."""
        report2 = UserReport.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone="+919876543212",
            area="Satellite",
            pincode="380015",
            problem_type="Water",
            description="Water issue"
        )
        reports = list(UserReport.objects.all())
        # Newest should be first
        self.assertEqual(reports[0].name, "Jane Doe")
        self.assertEqual(reports[1].name, "John Doe")

    def test_mark_resolved(self):
        """Test mark_resolved method."""
        self.assertEqual(self.report.status, "Pending")
        self.assertIsNone(self.report.resolved_at)
        
        self.report.mark_resolved()
        self.report.refresh_from_db()
        
        self.assertEqual(self.report.status, "Resolved")
        self.assertIsNotNone(self.report.resolved_at)
        # Should be recent (within 1 second)
        self.assertLess((timezone.now() - self.report.resolved_at).total_seconds(), 1)


class FeedbackModelTest(TestCase):
    """Test cases for Feedback model."""

    def setUp(self):
        """Set up test data."""
        self.authority = Authority.objects.create(
            name="Test Authority",
            email="test@example.com",
            phone="+919876543210",
            area="Test Area",
            department="Roads"
        )
        
        self.report = UserReport.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="+919876543211",
            area="Navrangpura",
            pincode="380009",
            problem_type="Roads",
            description="Test issue"
        )
        
        self.feedback = Feedback.objects.create(
            report=self.report,
            authority=self.authority,
            message="We are working on this issue.",
            is_public=False
        )

    def test_feedback_creation(self):
        """Test that Feedback object is created correctly."""
        self.assertIsNotNone(self.feedback.pk)
        self.assertEqual(self.feedback.report, self.report)
        self.assertEqual(self.feedback.authority, self.authority)
        self.assertEqual(self.feedback.message, "We are working on this issue.")
        self.assertFalse(self.feedback.is_public)

    def test_feedback_str_representation(self):
        """Test Feedback __str__ method."""
        str_repr = str(self.feedback)
        self.assertIn("Feedback for Report", str_repr)
        self.assertIn(str(self.report.id), str_repr)

    def test_feedback_default_values(self):
        """Test Feedback default values."""
        new_feedback = Feedback.objects.create(
            report=self.report,
            authority=self.authority,
            message="Another feedback"
        )
        self.assertFalse(new_feedback.is_public)  # Default should be False
        self.assertIsNotNone(new_feedback.created_at)
        self.assertIsNotNone(new_feedback.updated_at)

    def test_feedback_ordering(self):
        """Test that feedbacks are ordered by created_at (newest first)."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create second feedback with explicit timestamp to ensure ordering
        feedback2 = Feedback.objects.create(
            report=self.report,
            authority=self.authority,
            message="Second feedback"
        )
        # Refresh to ensure timestamps are set
        self.feedback.refresh_from_db()
        feedback2.refresh_from_db()
        
        feedbacks = list(Feedback.objects.all())
        # Should be ordered by created_at (newest first)
        # Verify ordering by checking timestamps
        self.assertGreaterEqual(feedbacks[0].created_at, feedbacks[1].created_at)

    def test_feedback_relationship_with_report(self):
        """Test that feedback is properly related to report."""
        self.assertEqual(self.feedback.report, self.report)
        # Test reverse relationship
        self.assertIn(self.feedback, self.report.feedbacks.all())

    def test_feedback_cascade_delete(self):
        """Test that feedback is deleted when report is deleted."""
        feedback_id = self.feedback.pk
        self.report.delete()
        # Feedback should be deleted (CASCADE)
        self.assertFalse(Feedback.objects.filter(pk=feedback_id).exists())

