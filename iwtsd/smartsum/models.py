import jiwer

from django.db import models

# Create your models here.

LANGS = (
	('en', 'English'),
	('he', 'Hebrew'),
	('fa', 'Farsi'),
)


class BaseModel(models.Model):
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	# created_by = models.ForeignKey(User)
	# modified_by = models.ForeignKey(User)
	class Meta:
		abstract = True


class TimedModel(BaseModel):
	ts_start = models.DateTimeField(null=True, blank=True)
	ts_end = models.DateTimeField(null=True, blank=True)

	class Meta:
		abstract = True


class Project(BaseModel):
	name = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.name


class Media(BaseModel):
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	title = models.CharField(max_length=255, null=True, blank=True)
	attachment = models.FileField(upload_to='media/attachments', null=True, blank=True, help_text='Supported formats: mp4, mp3, m4a, wav, flac')
	language = models.CharField(null=True, choices=LANGS)
	url = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
		verbose_name_plural = 'media'

	def __str__(self):
		return self.title or self.date_created


class Transcript(TimedModel):
	title = models.CharField(max_length=255, null=True)
	media = models.ForeignKey('Media', null=True, blank=True, on_delete=models.CASCADE)
	language = models.CharField(null=True, choices=LANGS)
	full = models.TextField(null=True, blank=True)
	summary = models.TextField(null=True, blank=True)
	reference = models.TextField(null=True, blank=True, help_text='Provide a reference transcription to calculate WER.')
	wer = models.FloatField(null=True, blank=True)

	def __str__(self):
		return f'{self.media.title or self.media.date_created} ({self.language})' if self.media else self.title

	def save(self, **kwargs):
		if self.reference and not self.wer:
			self.wer = calculate_wer(self.full, self.reference)
		super().save(**kwargs)

	def snippet(self):
		if self.full:
			return self.full[0:500]
		else:
			return ''

	def summary_snip(self):
		if self.summary:
			return self.summary[0:500]
		else:
			return ''

	def time_elapsed(self):
		return self.ts_end - self.ts_start if self.ts_end and self.ts_start else '0'


class TranscriptSegment(BaseModel):
	transcript = models.ForeignKey('Transcript', null=True, on_delete=models.CASCADE)
	start = models.DecimalField(max_digits=12, decimal_places=3, null=True)
	end = models.DecimalField(max_digits=12, decimal_places=3, null=True)
	text = models.TextField(null=True, blank=True)

	def __str__(self):
		return "[%.2fs -> %.2fs] %s" % (self.start, self.end, self.text)


class Translation(TimedModel):
	transcript = models.ForeignKey('Transcript', null=True, blank=True, on_delete=models.CASCADE)
	media = models.ForeignKey('Media', null=True, blank=True, on_delete=models.CASCADE)
	title = models.CharField(max_length=255, null=True)
	language = models.CharField(null=True, choices=LANGS)
	full = models.TextField(null=True, blank=True)
	summary = models.TextField(null=True, blank=True)
	reference = models.TextField(null=True, blank=True, help_text='Provide a reference transcription to calculate WER.')
	wer = models.FloatField(null=True, blank=True)

	def __str__(self):
		if self.transcript:
			return f'{self.transcript.media.title or self.transcript.media.date_created} ({self.language})'
		else:
			return f'{self.media.title or self.title} (self.language)'

	def save(self, **kwargs):
		if self.reference and not self.wer:
			self.wer = calculate_wer(self.full, self.reference)
		super().save(**kwargs)

	def snippet(self):
		if self.full:
			return self.full[0:500]
		else:
			return ''

	def summary_snip(self):
		if self.summary:
			return self.summary[0:500]
		else:
			return ''

	def time_elapsed(self):
		return self.ts_end - self.ts_start if self.ts_end and self.ts_start else '0'


class TranslationSegment(BaseModel):
	translation = models.ForeignKey('Translation', null=True, on_delete=models.CASCADE)
	start = models.DecimalField(max_digits=12, decimal_places=3, null=True)
	end = models.DecimalField(max_digits=12, decimal_places=3, null=True)
	text = models.TextField(null=True, blank=True)

	def __str__(self):
		return "[%.2fs -> %.2fs] %s" % (self.start, self.end, self.text)


def calculate_wer(reference, hypothesis):
	# Example reference and hypothesis transcriptions
	# reference = ["the quick brown fox jumps over the lazy dog", "i am learning about wer"]
	# hypothesis = ["the quick brown fox jump over the lazy dog", "i am learning about where"]

	# Apply optional text normalization (e.g., lowercase, remove punctuation)
	# to ensure fair comparison.
	transforms = jiwer.Compose([
		#jiwer.ExpandCommonEnglishContractions(),
		jiwer.RemoveEmptyStrings(),
		jiwer.ToLowerCase(),
		jiwer.RemoveMultipleSpaces(),
		jiwer.Strip(),
		jiwer.RemovePunctuation(),
		jiwer.ReduceToListOfListOfWords(),
	])

	wer = jiwer.wer(
		reference,
		hypothesis,
		reference_transform=transforms, 
		hypothesis_transform=transforms
	)

	print(f"Word Error Rate (WER): {wer}")
	return round(wer*100, 2)

# from jiwer import wer

# reference_transcript = "the quick brown fox jumps over the lazy dog"
# hypothesis_transcript = "the quick brown fox jump over the lazy dog" # Substitution (jumps -> jump)

# # Calculate WER
# error_rate = wer(reference_transcript, hypothesis_transcript)

# # Convert to percentage and print
# wer_percentage = round(error_rate * 100, 2)
# print(f"WER: {wer_percentage}%")