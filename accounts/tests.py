from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.test import SimpleTestCase


class EmailAppearanceTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set the email backend to SMTP
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        # You can also configure other SMTP settings here if needed

    def test_resend_verification_email(self):
        """Test resending the verification email appearance to multiple recipients."""

        # Define the recipients
        recipients = [
            'mohamed@izhar.xyz',
            'melegend.forever@protonmail.com',
            'melegend.forever@gmail.com',
        ]

        # Use a static token and user placeholder for testing
        token = 'x.com'
        user = {
            'username': 'dj_test_user',
            'email': 'test_user@django.drf'
        }

        html_message = render_to_string('emails/account_verification.html', {
            'user': user,
            'token': token,
            'frontend_url': "https://agavi.in"
        })

        subject = "Resend Email Verification"

        # Send the email to the defined recipients
        mail.send_mail(
            subject,
            "",  # Plain text message can be empty if only HTML is used
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
            html_message=html_message
        )

        self.assertEqual(len(mail.outbox), 1)

        # Optionally check the content of the first email
        for i, recipient in enumerate(recipients):
            sent_email = mail.outbox[i]
            self.assertIn('Resend Email Verification', sent_email.subject)
            self.assertIn('x.com', sent_email.body)  # Ensure token is present
            # Ensure username is present
            self.assertIn(user['username'], sent_email.body)
