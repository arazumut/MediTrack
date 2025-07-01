from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Migrate legacy notifications to new format'

    def handle(self, *args, **options):
        # Check if core_notification table exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_notification'")
            if not cursor.fetchone():
                self.stdout.write(self.style.SUCCESS('No core_notification table found, nothing to migrate'))
                return

            # Check if old user_id column exists and new recipient_id doesn't
            cursor.execute("PRAGMA table_info(core_notification)")
            columns = cursor.fetchall()
            columns_dict = {col[1]: col for col in columns}
            
            if 'user_id' in columns_dict and 'recipient_id' not in columns_dict:
                self.stdout.write(self.style.WARNING('Migrating notifications from user_id to recipient_id...'))
                
                # Create migration SQL
                cursor.execute("""
                UPDATE core_notification
                SET recipient_id = user_id
                WHERE recipient_id IS NULL AND user_id IS NOT NULL
                """)
                
                self.stdout.write(self.style.SUCCESS('Successfully migrated notification data!'))
            else:
                self.stdout.write(self.style.SUCCESS('No migration needed for notifications'))
