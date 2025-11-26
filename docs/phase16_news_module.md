# Phase 16: News Module Documentation

## Overview
The News module is a Django application that provides civic and city update information specifically for Ahmedabad. It allows administrators to create, manage, and publish news articles, while providing citizens with a user-friendly interface to browse and read news.

## Created Files

### 1. Django App Structure
- **`news/`** - Main application directory
  - `models.py` - News model with all required fields
  - `views.py` - Views for list, detail, category, and admin management
  - `urls.py` - URL routing configuration
  - `admin.py` - Django admin integration
  - `management/commands/create_sample_news.py` - Management command for sample data

### 2. Templates
- **`templates/news/news_list.html`** - Main news listing page with search and category filters
- **`templates/news/news_detail.html`** - Full article view with related news
- **`templates/news/category_list.html`** - Category-filtered news listing
- **`templates/news/admin_news_manage.html`** - Admin interface for managing articles

### 3. Configuration Files
- **`mysite/settings.py`** - Updated with `news` app in `INSTALLED_APPS`
- **`mysite/urls.py`** - Added news URL routing
- **`templates/nav.html`** - Added News link to navigation

## Model: News

### Fields
- `title` (CharField, 200 chars) - News article title
- `slug` (SlugField, 250 chars, unique) - URL-friendly identifier (auto-generated)
- `content` (TextField) - Full news article content
- `category` (CharField with choices) - News category:
  - Roads
  - Water
  - Health
  - Environment
  - Transport
  - Infrastructure
  - Education
  - Safety
  - General
- `author` (ForeignKey to User) - Article author
- `created_at` (DateTimeField, auto) - Creation timestamp
- `updated_at` (DateTimeField, auto) - Last update timestamp
- `is_published` (BooleanField) - Publication status
- `published_at` (DateTimeField, nullable) - Publication date
- `excerpt` (CharField, 300 chars) - Short summary (auto-generated if blank)
- `featured_image` (ImageField, optional) - Featured image
- `views_count` (PositiveIntegerField) - View tracking

### Model Methods
- `save()` - Auto-generates slug and excerpt if not provided
- `get_absolute_url()` - Returns detail page URL
- `get_category_url()` - Returns category filter URL
- `increment_views()` - Safely increments view count

### Indexes
- Category and created_at (composite)
- is_published and created_at (composite)
- created_at (single)
- Individual indexes on category, is_published, views_count, created_at

## Views

### 1. `news_list(request)`
- **URL**: `/news/`
- **Purpose**: Display paginated list of published news articles
- **Features**:
  - Search functionality
  - Category filtering
  - Pagination (12 articles per page)
  - Category count display

### 2. `news_detail(request, slug)`
- **URL**: `/news/<slug>/`
- **Purpose**: Display full content of a single article
- **Features**:
  - View count tracking
  - Related news (same category)
  - Next/Previous navigation
  - Admin edit link (if staff)

### 3. `category_list(request, category)`
- **URL**: `/news/category/<category>/`
- **Purpose**: Display news filtered by category
- **Features**:
  - Category validation
  - Pagination
  - Breadcrumb navigation

### 4. `admin_news_manage(request)`
- **URL**: `/news/admin/manage/`
- **Purpose**: Admin interface for managing news articles
- **Features**:
  - View all articles (published and drafts)
  - Filter by status (all/published/draft)
  - Filter by category
  - Search functionality
  - Statistics dashboard
  - Quick edit links
- **Access**: Staff users only

## URL Patterns

```python
urlpatterns = [
    path('', views.news_list, name='list'),
    path('<slug:slug>/', views.news_detail, name='detail'),
    path('category/<str:category>/', views.category_list, name='category'),
    path('admin/manage/', views.admin_news_manage, name='admin_manage'),
]
```

## Admin Integration

### Features
- Model registered in Django admin
- List display: title, category, author, status, created date, views
- Filters: category, is_published, created_at, author
- Search: title, content, excerpt
- Read-only fields: created_at, updated_at, published_at, views_count
- Preview link in list view
- Auto-set author on creation
- Staff-only permissions

## Location Restriction (Ahmedabad)

### Current Implementation
- Warning notice displayed on all news pages
- Function `check_ahmedabad_location()` prepared for future IP geolocation
- All users can currently access (shows warning notice)

### Future Enhancement
To implement strict location-based access:
1. Integrate with IP geolocation service (ipapi.co, ip-api.com, MaxMind GeoIP2)
2. Check user IP on each request
3. Redirect or block access if outside Ahmedabad
4. Store location preference in user session

## Template Features

### Shared Features
- Consistent styling with UrbanSite theme
- Responsive design (mobile-first)
- Dark/light theme support
- Loading animations and transitions
- Font Awesome icons

### news_list.html
- Search box
- Category filter buttons
- Grid layout (responsive)
- Pagination
- Empty state handling

### news_detail.html
- Full article content
- Featured image display
- Author and date metadata
- Related articles section
- Navigation buttons (prev/next)
- Category link

### category_list.html
- Breadcrumb navigation
- Category-specific header
- Article count display
- Same grid layout as list page

### admin_news_manage.html
- Statistics cards (total, published, drafts)
- Advanced filtering (status, category)
- Search functionality
- Table view with all article details
- Quick action buttons (edit, view)
- Staff access check

## Sample Data

### Management Command
- **Command**: `python manage.py create_sample_news`
- **Purpose**: Create sample news articles for testing
- **Sample Articles**:
  1. New Road Construction Project on SG Highway (Roads)
  2. Water Supply Improvement Initiative in Satellite Area (Water)
  3. New Health Center Opens in Maninagar (Health)
  4. Green Initiative: Tree Plantation Drive in Vastrapur (Environment)

### Usage
```bash
python manage.py create_sample_news
```

## Navigation Integration

### Navigation Link
- Added "News" link to main navigation (`templates/nav.html`)
- Active state highlighting when on news pages
- Mobile menu support
- URL: `{% url 'news:list' %}`

## Testing Checklist

### ✅ Completed
- [x] App created and added to INSTALLED_APPS
- [x] Model created with all required fields
- [x] Migrations created and applied
- [x] Views implemented for all 4 pages
- [x] URL patterns configured
- [x] Templates created (4 files)
- [x] Admin integration complete
- [x] Navigation link added
- [x] Sample data created
- [x] Location restriction placeholder (warning notice)

### 🔄 To Test
- [ ] Access `/news/` - should show list of articles
- [ ] Click on article - should show detail page
- [ ] Test category filtering
- [ ] Test search functionality
- [ ] Test pagination
- [ ] Access `/news/admin/manage/` as staff user
- [ ] Create/edit article in Django admin
- [ ] Verify published articles appear, drafts don't
- [ ] Test responsive design on mobile

## File Summary

### Created Files (Total: 12)
1. `news/__init__.py`
2. `news/models.py`
3. `news/views.py`
4. `news/urls.py`
5. `news/admin.py`
6. `news/management/__init__.py`
7. `news/management/commands/__init__.py`
8. `news/management/commands/create_sample_news.py`
9. `templates/news/news_list.html`
10. `templates/news/news_detail.html`
11. `templates/news/category_list.html`
12. `templates/news/admin_news_manage.html`

### Modified Files (Total: 3)
1. `mysite/settings.py` - Added `news` to INSTALLED_APPS
2. `mysite/urls.py` - Added news URL routing
3. `templates/nav.html` - Added News navigation link

## Database Migrations

### Migration File
- `news/migrations/0001_initial.py`
- Creates `news_news` table with all fields and indexes

### Apply Migrations
```bash
python manage.py migrate news
```

## Future Enhancements

1. **IP Geolocation**: Implement strict location-based access control
2. **Email Notifications**: Notify subscribers when new articles are published
3. **Comments System**: Allow users to comment on articles
4. **Tags System**: Add tagging for better categorization
5. **Rich Text Editor**: Integrate WYSIWYG editor for content
6. **Image Gallery**: Support multiple images per article
7. **Social Sharing**: Add share buttons for social media
8. **RSS Feed**: Generate RSS feed for news articles
9. **Newsletter**: Weekly/monthly newsletter with latest news
10. **Analytics**: Track article performance and engagement

## Security Considerations

1. **Staff-Only Access**: Admin management page restricted to staff users
2. **XSS Protection**: All user-generated content is auto-escaped by Django
3. **CSRF Protection**: All forms include CSRF tokens
4. **SQL Injection**: Protected by Django ORM
5. **File Upload**: Image uploads restricted to image formats only
6. **Permission Checks**: Views check user permissions before allowing actions

## Performance Optimizations

1. **Database Indexes**: Multiple indexes on frequently queried fields
2. **select_related**: Used in views to reduce database queries
3. **Pagination**: Limits results per page to prevent large queries
4. **Image Optimization**: Featured images stored in organized directory structure
5. **Caching Ready**: Views can be easily cached using Django's cache framework

## Maintenance

### Regular Tasks
- Review and moderate unpublished articles
- Update featured images
- Monitor view counts and popular articles
- Clean up old draft articles
- Backup database regularly

### Admin Access
- Access Django admin at `/admin/news/news/`
- Or use custom management interface at `/news/admin/manage/`

---

**Created**: November 2025  
**Version**: 1.0  
**Status**: ✅ Complete and Ready for Testing

