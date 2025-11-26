# UrbanSite/management/commands/backup_data.py
"""
Management command to backup database and media files.
Usage: python manage.py backup_data [--media-only] [--db-only]
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from pathlib import Path
import shutil
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Backup database and media files for UrbanSite'

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-only',
            action='store_true',
            help='Backup only media files',
        )
        parser.add_argument(
            '--db-only',
            action='store_true',
            help='Backup only database',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Output directory for backups (default: backups/ in project root)',
        )

    def handle(self, *args, **options):
        """Execute backup command."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = Path(settings.BASE_DIR)
        
        # Determine output directory
        if options['output_dir']:
            backup_dir = Path(options['output_dir'])
        else:
            backup_dir = base_dir / 'backups'
        
        backup_dir.mkdir(exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS(f'Starting backup at {timestamp}'))
        
        # Backup database
        if not options['media_only']:
            self.backup_database(base_dir, backup_dir, timestamp)
        
        # Backup media files
        if not options['db_only']:
            self.backup_media(base_dir, backup_dir, timestamp)
        
        self.stdout.write(self.style.SUCCESS(f'Backup completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Backup location: {backup_dir}'))

    def backup_database(self, base_dir, backup_dir, timestamp):
        """Backup database file."""
        db_path = base_dir / 'db.sqlite3'
        
        if not db_path.exists():
            self.stdout.write(self.style.WARNING('Database file not found. Skipping database backup.'))
            return
        
        db_backup_path = backup_dir / f'db_backup_{timestamp}.sqlite3'
        
        try:
            shutil.copy2(db_path, db_backup_path)
            self.stdout.write(self.style.SUCCESS(f'Database backed up to: {db_backup_path}'))
            
            # Keep only last 7 backups (weekly retention)
            self.cleanup_old_backups(backup_dir, pattern='db_backup_*.sqlite3', keep=7)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error backing up database: {str(e)}'))

    def backup_media(self, base_dir, backup_dir, timestamp):
        """Backup media files."""
        media_dir = Path(settings.MEDIA_ROOT)
        
        if not media_dir.exists():
            self.stdout.write(self.style.WARNING('Media directory not found. Skipping media backup.'))
            return
        
        media_backup_dir = backup_dir / f'media_backup_{timestamp}'
        
        try:
            # Copy media directory
            shutil.copytree(media_dir, media_backup_dir, dirs_exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'Media files backed up to: {media_backup_dir}'))
            
            # Keep only last 4 media backups (monthly retention)
            self.cleanup_old_backups(backup_dir, pattern='media_backup_*', keep=4, is_dir=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error backing up media: {str(e)}'))

    def cleanup_old_backups(self, backup_dir, pattern, keep=7, is_dir=False):
        """Remove old backup files, keeping only the most recent ones."""
        import glob
        
        if is_dir:
            backups = sorted([Path(p) for p in backup_dir.glob(pattern) if Path(p).is_dir()], reverse=True)
        else:
            backups = sorted([Path(p) for p in backup_dir.glob(pattern) if Path(p).is_file()], reverse=True)
        
        if len(backups) > keep:
            for old_backup in backups[keep:]:
                try:
                    if old_backup.is_dir():
                        shutil.rmtree(old_backup)
                    else:
                        old_backup.unlink()
                    self.stdout.write(self.style.WARNING(f'Removed old backup: {old_backup.name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error removing old backup {old_backup.name}: {str(e)}'))

