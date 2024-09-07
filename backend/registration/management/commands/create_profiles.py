from django.core.management.base import BaseCommand
from registration.models import User, Profile

class Command(BaseCommand):
    help = 'Create profile for users who do not have one'

    def handle(self, *args, **options):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            Profile.objects.create(user=user, user_type='student')  # Assign a default role if needed
        self.stdout.write(self.style.SUCCESS('Successfully created profiles for users'))



