from django.contrib import admin
from .models import Project, Media, Transcript, TranscriptSegment, Translation
from .actions import transcribe, translate_he, translate_en, summarize


class MediaInline(admin.TabularInline):
	model = Media
	extra = 1


class ProjectAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_created')
	# list_filter = ()
	inlines = [MediaInline,]


class MediaAdmin(admin.ModelAdmin):
	list_display = ('project', 'attachment', 'url',)
	list_filter = ('project',)
	actions = [transcribe, translate_he, translate_en]


class TranscriptAdmin(admin.ModelAdmin):
	list_display = ('media', 'language', 'snippet', 'wer', 'time_elapsed')
	list_filter = ('language',)
	exclude = ('ts_start', 'ts_end')
	actions = [summarize]  # ,translate


class TranslationAdmin(admin.ModelAdmin):
	list_display = ('media', 'language', 'snippet', 'wer', 'time_elapsed')
	list_filter = ('language',)
	exclude = ('ts_start', 'ts_end')
	actions = [summarize]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Translation, TranslationAdmin)