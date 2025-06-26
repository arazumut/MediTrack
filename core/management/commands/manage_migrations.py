from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess
import sys


class Command(BaseCommand):
    help = 'Generate and apply all migrations for MediTracked system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-migrate',
            action='store_true',
            help='Only create migrations, do not apply them',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset migrations (dangerous - only for development)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Managing MediTracked Migrations...'))
        
        apps = ['core', 'users', 'appointments', 'treatments', 'telemedicine']
        
        try:
            if options['reset']:
                self.reset_migrations(apps)
            
            self.create_migrations(apps)
            
            if not options['no_migrate']:
                self.apply_migrations()
                
            self.stdout.write(self.style.SUCCESS('✅ Migration management completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during migration: {str(e)}'))
            raise

    def reset_migrations(self, apps):
        """Reset migrations for development (DANGEROUS)"""
        self.stdout.write(self.style.WARNING('⚠️  Resetting migrations (DEVELOPMENT ONLY)...'))
        
        confirm = input('This will delete all migration files. Are you sure? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('Operation cancelled.')
            return
            
        import os
        from django.conf import settings
        
        for app in apps:
            migrations_dir = os.path.join(settings.BASE_DIR, app, 'migrations')
            if os.path.exists(migrations_dir):
                for file in os.listdir(migrations_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        file_path = os.path.join(migrations_dir, file)
                        os.remove(file_path)
                        self.stdout.write(f'  Deleted: {app}/migrations/{file}')

    def create_migrations(self, apps):
        """Create migrations for all apps"""
        self.stdout.write('📝 Creating migrations...')
        
        for app in apps:
            try:
                self.stdout.write(f'  Creating migrations for {app}...')
                call_command('makemigrations', app, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Migrations created for {app}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Could not create migrations for {app}: {str(e)}'))

    def apply_migrations(self):
        """Apply all migrations"""
        self.stdout.write('🚀 Applying migrations...')
        
        try:
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('  ✅ All migrations applied successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error applying migrations: {str(e)}'))
            raise

    def check_migrations(self):
        """Check for unapplied migrations"""
        self.stdout.write('🔍 Checking for unapplied migrations...')
        
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'showmigrations', '--plan'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                unapplied = [line for line in result.stdout.split('\n') if '[ ]' in line]
                if unapplied:
                    self.stdout.write(f'  Found {len(unapplied)} unapplied migrations')
                    for migration in unapplied:
                        self.stdout.write(f'    {migration}')
                else:
                    self.stdout.write('  ✅ All migrations are applied')
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ Error checking migrations: {result.stderr}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error checking migrations: {str(e)}'))
