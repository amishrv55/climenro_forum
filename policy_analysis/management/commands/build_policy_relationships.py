from django.core.management.base import BaseCommand
from policy_analysis.compute_policy_relationships import build_relationships


class Command(BaseCommand):
    help = 'Build relationships among existing policies'

    def handle(self, *args, **kwargs):
        build_relationships()
        self.stdout.write(self.style.SUCCESS('Policy relationships computed.'))
