# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.core import management
import os
from django.conf import settings


class Command(BaseCommand):
    args = '<No arguments>'
    help = 'This command will reset the database and load all fixtures.'
    requires_model_validation = False

    def handle(self, *args, **options):
        try:

            databases = getattr(settings, 'DATABASES')

            for i in connections.databases:
                if i in ('dwh_slave', 'default_slave'):
                    continue

                # connecting to remove all tables from database
                cursor = connections[i].cursor()
                cursor.execute(
                    """SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type != 'VIEW' AND table_name NOT LIKE 'pg_ts_%%'""")
                rows = cursor.fetchall()
                for row in rows:
                    try:
                        cursor.execute('drop table %s cascade ' % row[0])
                        self.stdout.write("dropping %s\n" % row[0])
                    except:
                        self.stdout.write("couldn't drop %s\n" % row[0])

                self.stdout.write("Starting database sync process\n")
                management.call_command('syncdb', interactive=False, database=i)
                management.call_command('migrate')

            if os.path.isfile('apps/account/fixtures/groups.json'):
                management.call_command('loaddata', 'apps/account/fixtures/groups.json', database='default')

            if os.path.isfile('apps/account/fixtures/users.json'):
                management.call_command('loaddata', 'apps/account/fixtures/users.json', database='default')

            self.stdout.write('------------------------------------\n')
            management.call_command('build_sql_bins', )
            self.stdout.write('------------------------------------\n')

        except KeyError:
            raise