from django.contrib import admin
from Pisos_tracker_app.models import Report, House, Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject','date',)
    search_fields = ('name', 'email',)
    date_hierarchy = 'date'

# Register your models here.
admin.site.register(Report)
admin.site.register(House)
admin.site.register(Feedback, FeedbackAdmin)