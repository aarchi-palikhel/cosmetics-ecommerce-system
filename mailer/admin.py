import csv
import io
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.shortcuts import render
from .models import MailContact


@admin.register(MailContact)
class MailContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'location', 'gender', 'created_at')
    search_fields = ('name', 'email', 'location')
    list_filter = ('gender',)
    change_list_template = 'admin/mailer/mailcontact/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        extra = [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='mailer_import_csv')]
        return extra + urls

    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                self.message_user(request, 'No file selected.', messages.ERROR)
                return HttpResponseRedirect(reverse('admin:mailer_mailcontact_changelist'))

            decoded = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))
            created, skipped = 0, 0
            for row in reader:
                _, was_created = MailContact.objects.get_or_create(
                    email=row.get('EmailID', '').strip(),
                    defaults={
                        'name': row.get('Name', '').strip(),
                        'location': row.get('Location', '').strip(),
                        'gender': row.get('Gender', '').strip().lower(),
                    }
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

            self.message_user(request, f'Imported {created} contacts, skipped {skipped} duplicates.')
            return HttpResponseRedirect(reverse('admin:mailer_mailcontact_changelist'))

        return render(request, 'admin/mailer/mailcontact/import_csv.html')
