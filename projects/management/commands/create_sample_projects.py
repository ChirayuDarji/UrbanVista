# projects/management/commands/create_sample_projects.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import ProjectCategory, CityProject, ProjectUpdate, ProjectDocument
from reports.models import Department
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile
import requests
from io import BytesIO

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample projects for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing projects before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Deleting existing projects...')
            CityProject.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted existing projects'))
        
        self.stdout.write('Creating sample projects...')
        
        # Get or create admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('No staff user found. Creating a test user...'))
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=True
            )
        
        # Create categories
        categories_data = [
            {'name': 'Infrastructure', 'description': 'Roads, bridges, and major infrastructure projects', 'icon': 'fas fa-road'},
            {'name': 'Parks & Recreation', 'description': 'Parks, playgrounds, and recreational facilities', 'icon': 'fas fa-tree'},
            {'name': 'Water & Sanitation', 'description': 'Water supply, drainage, and sanitation projects', 'icon': 'fas fa-tint'},
            {'name': 'Public Facilities', 'description': 'Community centers, libraries, and public buildings', 'icon': 'fas fa-building'},
            {'name': 'Smart City', 'description': 'Digital infrastructure and smart city initiatives', 'icon': 'fas fa-wifi'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = ProjectCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Get or create a department
        department, _ = Department.objects.get_or_create(
            name='Public Works',
            defaults={
                'email': 'publicworks@ahmedabad.gov.in',
                'contact_number': '+91 79 2658 0000'
            }
        )
        
        # Helper function to download and set image
        def set_project_image(project, image_url, description):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(image_url, timeout=15, headers=headers)
                if response.status_code == 200 and response.content:
                    img_name = f"{project.slug}_featured.jpg"
                    project.featured_image.save(
                        img_name,
                        ContentFile(response.content),
                        save=True
                    )
                    self.stdout.write(f'  ✓ Added image for {project.title}')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Failed to download image for {project.title}: Status {response.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Could not download image for {project.title}: {str(e)}'))
        
        # Sample projects with image URLs - Projects from across India
        projects_data = [
            {
                'title': 'Mumbai Metro Line 4 Extension',
                'image_url': 'https://images.unsplash.com/photo-1557223562-6c77ef16210f?w=800&h=600&fit=crop',
                'short_description': 'Extension of Mumbai Metro Line 4 connecting eastern suburbs to the city center',
                'description': '''The Mumbai Metro Line 4 Extension project will connect the eastern suburbs to the city center, providing better public transportation access. This project includes:

- 12 km of new metro line
- 8 new metro stations with modern amenities
- Integration with existing metro network
- Real-time passenger information systems
- Accessible design for differently-abled passengers

This extension will serve approximately 200,000 daily commuters and significantly reduce traffic congestion on major routes.''',
                'category': 'Infrastructure',
                'status': 'in_progress',
                'priority': 'high',
                'location': 'Mumbai, Maharashtra',
                'ward': 'Multiple Wards',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'start_date': timezone.now().date() - timedelta(days=120),
                'expected_completion_date': timezone.now().date() + timedelta(days=300),
                'estimated_budget': 1200000000,
                'actual_cost': 450000000,
                'progress_percentage': 55,
                'benefits': 'Improved public transport, reduced traffic, better connectivity, environmental benefits',
                'challenges': 'Land acquisition, coordination with traffic department, maintaining service during construction',
                'project_manager': 'Mr. Vikram Desai',
                'contact_email': 'metro@mumbai.gov.in',
                'contact_phone': '+91 22 2262 1234',
            },
            {
                'title': 'Delhi Smart Street Lighting Initiative',
                'image_url': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&h=600&fit=crop',
                'short_description': 'Installation of LED smart street lights with IoT sensors across Delhi',
                'description': '''The Delhi Smart Street Lighting Initiative involves replacing traditional street lights with energy-efficient LED lights equipped with IoT sensors. This project includes:

- Installation of 200,000 LED street lights across all zones
- IoT sensors for automatic dimming and monitoring
- Centralized control system
- Mobile app for reporting issues
- Energy savings of up to 65%

The smart lighting system will improve safety, reduce energy consumption, and enable predictive maintenance across the capital.''',
                'category': 'Smart City',
                'status': 'in_progress',
                'priority': 'high',
                'location': 'Delhi NCR',
                'ward': 'All Zones',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'start_date': timezone.now().date() - timedelta(days=90),
                'expected_completion_date': timezone.now().date() + timedelta(days=270),
                'estimated_budget': 800000000,
                'actual_cost': 280000000,
                'progress_percentage': 40,
                'benefits': 'Energy savings, improved safety, reduced maintenance costs, smart city integration',
                'challenges': 'Coordination across multiple zones, ensuring quality installation, training maintenance staff',
                'project_manager': 'Ms. Anjali Mehta',
                'contact_email': 'lighting@delhi.gov.in',
                'contact_phone': '+91 11 2396 2345',
            },
            {
                'title': 'Bangalore Namma Metro Phase 3',
                'image_url': 'https://images.unsplash.com/photo-1557223562-6c77ef16210f?w=800&h=600&fit=crop',
                'short_description': 'Expansion of Namma Metro network to connect IT corridors and residential areas',
                'description': '''Namma Metro Phase 3 will expand the existing metro network to better serve IT corridors and residential areas. The project includes:

- 25 km of new metro lines
- 15 new metro stations
- Integration with existing Phase 1 and 2
- Park-and-ride facilities
- Last-mile connectivity solutions

This expansion will significantly improve connectivity for IT professionals and reduce traffic congestion in the tech capital.''',
                'category': 'Infrastructure',
                'status': 'approved',
                'priority': 'high',
                'location': 'Bangalore, Karnataka',
                'ward': 'Multiple Wards',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'start_date': timezone.now().date() + timedelta(days=60),
                'expected_completion_date': timezone.now().date() + timedelta(days=600),
                'estimated_budget': 1500000000,
                'progress_percentage': 3,
                'benefits': 'Improved connectivity, reduced traffic, better access to IT parks, environmental benefits',
                'challenges': 'Land acquisition, coordination with multiple agencies, maintaining service during construction',
                'project_manager': 'Mr. Ramesh Kumar',
                'contact_email': 'metro@bmtc.gov.in',
                'contact_phone': '+91 80 2297 3456',
            },
            {
                'title': 'Hyderabad Metro Rail Phase 2',
                'image_url': 'https://images.unsplash.com/photo-1557223562-6c77ef16210f?w=800&h=600&fit=crop',
                'short_description': 'Expansion of Hyderabad Metro to connect Old City and IT Corridor',
                'description': '''Hyderabad Metro Rail Phase 2 will extend the existing metro network to connect the historic Old City with the IT Corridor. The project includes:

- 18 km of new metro lines
- 10 new metro stations
- Heritage-friendly station designs in Old City
- Integration with existing Phase 1
- Multi-modal transport hubs

This expansion will improve connectivity between the historic and modern parts of the city.''',
                'category': 'Infrastructure',
                'status': 'planned',
                'priority': 'high',
                'location': 'Hyderabad, Telangana',
                'ward': 'Multiple Wards',
                'latitude': 17.3850,
                'longitude': 78.4867,
                'start_date': timezone.now().date() + timedelta(days=90),
                'expected_completion_date': timezone.now().date() + timedelta(days=540),
                'estimated_budget': 1200000000,
                'progress_percentage': 0,
                'benefits': 'Better connectivity, reduced traffic, heritage preservation, economic development',
                'challenges': 'Heritage site considerations, land acquisition, coordination with multiple stakeholders',
                'project_manager': 'Ms. Kavita Reddy',
                'contact_email': 'metro@hyderabad.gov.in',
                'contact_phone': '+91 40 2323 4567',
            },
            {
                'title': 'Chennai Coastal Road Project',
                'image_url': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop',
                'short_description': 'Development of coastal road with cycling tracks and promenades',
                'description': '''The Chennai Coastal Road Project will create a scenic coastal road with dedicated cycling tracks and pedestrian promenades. The project includes:

- 20 km of coastal road
- Dedicated cycling lanes
- Pedestrian promenades with seating areas
- Viewing decks and rest areas
- Beach access points
- Enhanced lighting and security

This project will provide a beautiful recreational space while improving connectivity along the coast.''',
                'category': 'Parks & Recreation',
                'status': 'in_progress',
                'priority': 'medium',
                'location': 'Chennai, Tamil Nadu',
                'ward': 'Coastal Wards',
                'latitude': 13.0827,
                'longitude': 80.2707,
                'start_date': timezone.now().date() - timedelta(days=150),
                'expected_completion_date': timezone.now().date() + timedelta(days=300),
                'estimated_budget': 800000000,
                'actual_cost': 320000000,
                'progress_percentage': 50,
                'benefits': 'Enhanced public spaces, increased tourism, improved connectivity, recreational facilities',
                'challenges': 'Coastal regulations, environmental clearances, maintaining quality standards',
                'project_manager': 'Mr. Suresh Iyer',
                'contact_email': 'coastal@chennai.gov.in',
                'contact_phone': '+91 44 2538 5678',
            },
            {
                'title': 'Kolkata Metro East-West Corridor',
                'image_url': 'https://images.unsplash.com/photo-1557223562-6c77ef16210f?w=800&h=600&fit=crop',
                'short_description': 'Completion of East-West Metro corridor connecting Howrah to Salt Lake',
                'description': '''The Kolkata Metro East-West Corridor will complete the connection between Howrah and Salt Lake, passing under the Hooghly River. The project includes:

- 16 km of metro line including underwater tunnel
- 12 metro stations
- India's first underwater metro tunnel
- Integration with existing North-South line
- Modern station designs

This corridor will significantly reduce travel time between Howrah and Salt Lake.''',
                'category': 'Infrastructure',
                'status': 'completed',
                'priority': 'high',
                'location': 'Kolkata, West Bengal',
                'ward': 'Multiple Wards',
                'latitude': 22.5726,
                'longitude': 88.3639,
                'start_date': timezone.now().date() - timedelta(days=720),
                'expected_completion_date': timezone.now().date() - timedelta(days=60),
                'actual_completion_date': timezone.now().date() - timedelta(days=60),
                'estimated_budget': 5000000000,
                'actual_cost': 4800000000,
                'progress_percentage': 100,
                'benefits': 'Reduced travel time, underwater tunnel achievement, better connectivity, reduced traffic',
                'challenges': 'Underwater tunnel construction, technical complexity, coordination with multiple agencies',
                'project_manager': 'Mr. Amit Banerjee',
                'contact_email': 'metro@kolkata.gov.in',
                'contact_phone': '+91 33 2243 6789',
            },
            {
                'title': 'Pune Smart City Cycling Network',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
                'short_description': 'Development of dedicated cycling tracks connecting IT parks and residential areas',
                'description': '''The Pune Smart City Cycling Network will create 40 km of dedicated cycling infrastructure:

- 6 major cycling corridors connecting IT parks
- Dedicated lanes separated from traffic
- Cycle sharing stations
- Cycle parking facilities at key locations
- Signage and safety features
- Integration with public transport

This initiative promotes eco-friendly transportation and healthy lifestyle while reducing traffic congestion in the IT hub.''',
                'category': 'Infrastructure',
                'status': 'in_progress',
                'priority': 'medium',
                'location': 'Pune, Maharashtra',
                'ward': 'Multiple Wards',
                'latitude': 18.5204,
                'longitude': 73.8567,
                'start_date': timezone.now().date() - timedelta(days=90),
                'expected_completion_date': timezone.now().date() + timedelta(days=180),
                'estimated_budget': 200000000,
                'actual_cost': 85000000,
                'progress_percentage': 65,
                'benefits': 'Promotes cycling, reduces pollution, healthy lifestyle, traffic reduction, IT park connectivity',
                'challenges': 'Space constraints, ensuring safety, maintenance, changing commuter habits',
                'project_manager': 'Mr. Rajesh Kulkarni',
                'contact_email': 'cycling@pune.gov.in',
                'contact_phone': '+91 20 2553 7890',
            },
            {
                'title': 'Jaipur Heritage Walkway Development',
                'image_url': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop',
                'short_description': 'Development of heritage walkway connecting major historical monuments',
                'description': '''The Jaipur Heritage Walkway Development will create a pedestrian-friendly route connecting major historical monuments. The project includes:

- 8 km of heritage walkway
- Restoration of historical facades
- Street furniture and signage
- Lighting and security systems
- Tourist information centers
- Rest areas and cafes

This project will enhance the tourist experience while preserving the Pink City's heritage.''',
                'category': 'Parks & Recreation',
                'status': 'approved',
                'priority': 'medium',
                'location': 'Jaipur, Rajasthan',
                'ward': 'Heritage Zone',
                'latitude': 26.9124,
                'longitude': 75.7873,
                'start_date': timezone.now().date() + timedelta(days=45),
                'expected_completion_date': timezone.now().date() + timedelta(days=450),
                'estimated_budget': 350000000,
                'progress_percentage': 5,
                'benefits': 'Heritage preservation, increased tourism, improved pedestrian experience, economic boost',
                'challenges': 'Heritage site regulations, coordination with ASI, maintaining historical character',
                'project_manager': 'Ms. Priya Sharma',
                'contact_email': 'heritage@jaipur.gov.in',
                'contact_phone': '+91 141 253 8901',
            },
        ]
        
        created_projects = []
        for proj_data in projects_data:
            # Extract image_url if present
            image_url = proj_data.pop('image_url', None)
            category = categories.get(proj_data.pop('category'))
            
            project = CityProject.objects.create(
                created_by=admin_user,
                updated_by=admin_user,
                category=category,
                department=department,
                is_public=True,
                allow_comments=True,
                **proj_data
            )
            
            # Download and set image if URL provided
            if image_url:
                set_project_image(project, image_url, project.title)
            
            created_projects.append(project)
            self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))
        
        # Add some updates to in-progress projects
        in_progress_projects = [p for p in created_projects if p.status == 'in_progress']
        
        for project in in_progress_projects[:3]:  # Add updates to first 3 in-progress projects
            if 'Mumbai Metro' in project.title:
                ProjectUpdate.objects.create(
                    project=project,
                    title='Tunnel Boring Machine Deployed',
                    content='The tunnel boring machine has been successfully deployed and tunnel construction has begun. First 2 km of tunnel completed.',
                    progress_percentage=55,
                    created_by=admin_user
                )
                ProjectUpdate.objects.create(
                    project=project,
                    title='Station Construction Started',
                    content='Construction of the first 4 metro stations has commenced. Foundation work is progressing well.',
                    progress_percentage=60,
                    created_by=admin_user
                )
            elif 'Coastal Road' in project.title:
                ProjectUpdate.objects.create(
                    project=project,
                    title='Coastal Road Foundation Completed',
                    content='The foundation work for the coastal road has been completed. Road construction and cycling track installation is now in progress.',
                    progress_percentage=50,
                    created_by=admin_user
                )
            elif 'Cycling Network' in project.title:
                ProjectUpdate.objects.create(
                    project=project,
                    title='First Corridor Completed',
                    content='The first cycling corridor connecting Hinjewadi IT Park has been completed and is now open for public use. Feedback has been very positive!',
                    progress_percentage=65,
                    created_by=admin_user
                )
        
        # Add a document to one project
        if created_projects:
            self.stdout.write(self.style.SUCCESS(f'\nCreated {len(created_projects)} sample projects'))
            self.stdout.write(self.style.SUCCESS(f'Created {ProjectUpdate.objects.count()} project updates'))
            self.stdout.write('\nYou can now view the projects at: /projects/')

