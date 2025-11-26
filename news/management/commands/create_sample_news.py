# news/management/commands/create_sample_news.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.models import News
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample news articles for testing'

    def handle(self, *args, **options):
        # Get or create a staff user for author
        staff_user = User.objects.filter(is_staff=True).first()
        if not staff_user:
            # Create a staff user if none exists
            staff_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created staff user: {staff_user.username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing staff user: {staff_user.username}'))

        # Sample news articles
        sample_news = [
            {
                'title': 'New Road Construction Project on SG Highway',
                'content': '''Ahmedabad Municipal Corporation (AMC) has announced a major road construction project on SG Highway to improve connectivity and reduce traffic congestion. The project will span 5 kilometers and is expected to be completed within 6 months.

The construction will include:
- Widening of existing lanes
- Installation of modern street lighting
- Improved drainage systems
- Dedicated cycling lanes

Residents are advised to use alternative routes during construction hours (6 AM - 10 PM). For updates, please visit the AMC website or call the helpline number 155303.''',
                'category': 'Roads',
                'is_published': True,
            },
            {
                'title': 'Water Supply Improvement Initiative in Satellite Area',
                'content': '''The Ahmedabad Municipal Corporation has launched a comprehensive water supply improvement initiative in the Satellite area. This initiative aims to provide 24/7 water supply and improve water quality.

Key features of the initiative:
- New water treatment plant installation
- Pipeline upgrades and repairs
- Water quality monitoring stations
- Public awareness campaigns

The project is expected to benefit over 50,000 households in the area. Residents will receive updates via SMS and email regarding any temporary water supply interruptions.''',
                'category': 'Water',
                'is_published': True,
            },
            {
                'title': 'New Health Center Opens in Maninagar',
                'content': '''A new state-of-the-art health center has been inaugurated in Maninagar, Ahmedabad. The facility will provide comprehensive healthcare services to residents in the area.

Services available:
- General consultations
- Vaccination programs
- Health check-ups
- Emergency care
- Maternal and child health services

The center is open from 8 AM to 8 PM, Monday to Saturday. For appointments, residents can call 079-12345678 or visit the center directly.''',
                'category': 'Health',
                'is_published': True,
            },
            {
                'title': 'Green Initiative: Tree Plantation Drive in Vastrapur',
                'content': '''AMC has organized a massive tree plantation drive in Vastrapur area to combat air pollution and improve the environment. Over 5000 saplings will be planted across parks and roadside areas.

The initiative includes:
- Native tree species selection
- Community participation programs
- Maintenance and monitoring
- Environmental education sessions

Residents are encouraged to participate in the drive scheduled for this weekend. Volunteers can register online or contact the AMC environment department.''',
                'category': 'Environment',
                'is_published': True,
            },
        ]

        created_count = 0
        for news_data in sample_news:
            # Check if article already exists
            if not News.objects.filter(title=news_data['title']).exists():
                news = News.objects.create(
                    title=news_data['title'],
                    content=news_data['content'],
                    category=news_data['category'],
                    author=staff_user,
                    is_published=news_data['is_published'],
                    published_at=timezone.now() if news_data['is_published'] else None,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {news.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {news_data["title"]}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} news articles!'))
        self.stdout.write(self.style.SUCCESS(f'Total news articles: {News.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Published articles: {News.objects.filter(is_published=True).count()}'))

