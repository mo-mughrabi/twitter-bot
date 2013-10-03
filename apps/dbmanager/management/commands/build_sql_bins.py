# -*- coding: utf-8 -*-
import glob
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, connection
import os
from django.db.models import get_apps


class Command(BaseCommand):
    args = '<No arguments>'
    help = ''

    def handle(self, *args, **options):
        try:

            cursor = connection.cursor()

            self.stdout.write('Building SQL bins into database..\n')
            for apps in get_apps():
                sql_bin = os.path.join(os.path.dirname(apps.__file__), 'sql/bin')
                if os.path.isdir(sql_bin):
                    self.stdout.write('SQL/BIN found in %s ...\n' % apps.__name__)
                    for file in glob.glob("%s/*.sql" % sql_bin):
                        self.stdout.write('Executing (%s) in %s\n' % (file, apps.__name__))
                        f = open(file, mode='r')
                        sql = f.read()
                        f.close()
                        cursor.execute(sql)
                        cursor.execute('commit')

            self.stdout.write('\n')
            self.stdout.write('Execution completed, exiting.\n')




        except Exception as e:
            raise CommandError('Exception: %s' % str(e))