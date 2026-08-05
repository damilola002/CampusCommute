from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.forms import ValidationError

class EduEmailOnlyAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        if not email or not email.lower().endswith('.edu'):
            raise ValidationError("Only .edu email addresses are allowed on CampusCommute.")
        return super().clean_email(email)

class EduSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Retrieve email from social login user data
        email = sociallogin.user.email
        if not email or not email.lower().endswith('.edu'):
            raise ValidationError("Only .edu email addresses are allowed on CampusCommute.")
        super().pre_social_login(request, sociallogin)
