import re
from datetime import datetime
from .models import Project, Media, Transcript, TranscriptSegment, Translation, TranslationSegment
from faster_whisper import WhisperModel
from transformers import pipeline
from typing import Union, List
import argostranslate.package
import argostranslate.translate


def transcribe(modeladmin, request, queryset):
	for media in queryset:
		t = Transcript.objects.create(media=media, language=media.language, title=media.title)
		if media.language == 'he':
			m = 'ivrit-ai/faster-whisper-v2-d4'  # 'ivrit-ai/faster-whisper-v2-d4'  # 'ivrit-ai/whisper-large-v3-ct2'
			model = WhisperModel(m, device="cuda", compute_type="int8")  # device="cuda", compute_type="float16" for AI Hat
		else:
			m = 'large-v3'  # 
			model = WhisperModel(m, device="cuda", compute_type="int8")  # device="cuda", compute_type="float16" for AI Hat
		t.ts_start = datetime.now()
		segments, info = model.transcribe(media.attachment.path, beam_size=5, language=media.language)
		output = []
		for segment in segments:
			ts = TranscriptSegment.objects.create(
				transcript=t,
				start=str(segment.start),
				end=str(segment.end),
				text=segment.text
			)
			output.append(segment.text)
		t.ts_end = datetime.now()
	t.full = '\n'.join(output)
	t.save()


def translate_he(modeladmin, request, queryset):
	for media in queryset:
		translate(media, 'he')


def translate_en(modeladmin, request, queryset):
	for media in queryset:
		translate(media, 'en')


def translate(media, lang):
	t = Translation.objects.create(media=media, language=lang, title=media.title)
	m = 'large-v3'
	model = WhisperModel(m, device="cuda", compute_type="int8")  # device="cuda", compute_type="float16" for AI Hat
	t.ts_start = datetime.now()
	segments, info = model.transcribe(media.attachment.path, beam_size=5, language=lang, task='translate')
	output = []
	for segment in segments:
		print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
		ts = TranslationSegment.objects.create(
			translation=t,
			start=segment.start,
			end=segment.end,
			text=segment.text
		)
		output.append(segment.text)
	t.ts_end = datetime.now()
	t.full = '\n'.join(output)
	t.save()

translate_he.short_description = 'Translate to Hebrew'
translate_en.short_description = 'Translate to English'


#    segments, info = model.transcribe("audio.mp3", beam_size=5, task="translate")


def summarize(modeladmin, request, queryset):
	for t in queryset:
		t.summary = summarize_text(t.full, language=t.media.language if t.media else t.language)
		t.save()
	return '\n'.join(output)


def summarize_text(
	text: str,
	max_length: int = 150,
	min_length: int = 30,
	language: str = "auto") -> str:
	"""
	Summarize text documents in Hebrew, Farsi, or English using a transformers pipeline.
	
	Args:
		text (str): Input text to summarize.
		model_name (str): Hugging Face model for summarization (default: facebook/bart-large-cnn).
		max_length (int): Maximum length of the summary.
		min_length (int): Minimum length of the summary.
		language (str): Language of the text ('hebrew', 'farsi', 'english', or 'auto').
	
	Returns:
		str: Summarized text.
	"""
	# Basic text preprocessing
	text = re.sub(r'\s+', ' ', text.strip())

	# Initialize the summarization pipeline
	# Note: For multilingual support, consider 'csebuetnlp/mT5_multilingual_XLSum' for better Hebrew/Farsi handling

	# For Hebrew and Farsi, recommend switching to a multilingual model if needed
	if language in ["he", "fa"]:
		model_name = "csebuetnlp/mT5_multilingual_XLSum"
		summarizer = pipeline(
			"summarization",
			model=model_name,
			tokenizer=model_name,
			framework="pt",
			device="cpu"
		)
	else:
		model_name = "facebook/bart-large-cnn"
		summarizer = pipeline(
			"summarization",
			model=model_name,
			tokenizer=model_name,
			framework="pt",
			device="cpu"
		)

	# Handle long texts by chunking if necessary
	max_input_length = summarizer.model.config.max_length
	words = text.split()
	if len(words) > max_input_length:
		chunks = []
		current_chunk = []
		current_length = 0

		for word in words:
			current_chunk.append(word)
			current_length += len(word) + 1
			if current_length > max_input_length:
				chunks.append(" ".join(current_chunk))
				current_chunk = []
				current_length = 0
		if current_chunk:
			chunks.append(" ".join(current_chunk))
	else:
		chunks = [text]

	# Summarize each chunk
	summaries = []
	for chunk in chunks:
		summary = summarizer(
			chunk,
			max_length=max_length,
			min_length=min_length,
			do_sample=False,
			truncation=True
		)[0]["summary_text"]
		summaries.append(summary)

	# Combine summaries
	final_summary = " ".join(summaries)

	# Ensure output is within max_length
	if len(final_summary.split()) > max_length:
		final_summary = summarizer(
			final_summary,
			max_length=max_length,
			min_length=min_length,
			do_sample=False,
			truncation=True
		)[0]["summary_text"]

	return final_summary

# # Example usage
# if __name__ == "__main__":
# 	# Sample texts
# 	english_text = """
# 	Artificial intelligence is transforming industries worldwide. From healthcare to finance, 
# 	AI systems are improving efficiency and decision-making. Recent advancements in natural 
# 	language processing have enabled machines to understand and generate human-like text.
# 	"""
	
# 	hebrew_text = """
# 	הבינה המלאכותית משנה את התעשיות ברחבי העולם. ממערכות בריאות ועד פיננסים, 
# 	מערכות AI משפרות את היעילות ואת קבלת ההחלטות. התקדמות אחרונה בעיבוד שפה טבעית 
# 	מאפשרת למכונות להבין ולייצר טקסט דמוי אנושי.
# 	"""
	
# 	farsi_text = """
# 	هوش مصنوعی در حال تغییر صنایع در سراسر جهان است. از مراقبت‌های بهداشتی گرفته تا 
# 	امور مالی، سیستم‌های هوش مصنوعی کارایی و تصمیم‌گیری را بهبود می‌بخشند. پیشرفت‌های 
# 	اخیر در پردازش زبان طبیعی به ماشین‌ها امکان داده است تا متنی شبیه به انسان را درک 
# 	کنند و تولید کنند.
# 	"""
	
# 	# Summarize texts
# 	print("English Summary:")
# 	print(summarize_text(english_text, language="english"))
# 	print("\nHebrew Summary:")
# 	print(summarize_text(hebrew_text, language="hebrew"))
# 	print("\nFarsi Summary:")
# 	print(summarize_text(farsi_text, language="farsi"))




# import argostranslate.package
# import argostranslate.translate

# # Update package index to find available packages
# argostranslate.package.update_package_index()

# # Define source and target languages
# from_code = "en"  # Example: English
# to_code = "he"    # Hebrew

# # Find and install the required language package
# available_packages = argostranslate.package.get_available_packages()
# package_to_install = next(
#     filter(
#         lambda x: x.from_code == from_code and x.to_code == to_code,
#         available_packages
#     )
# )
# argostranslate.package.install_from_path(package_to_install.download())