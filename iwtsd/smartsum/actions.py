import re
from datetime import datetime
from .models import Project, Media, Transcript, TranscriptSegment, Translation, TranslationSegment
from django.http import HttpResponseRedirect
from faster_whisper import WhisperModel
from transformers import pipeline
from typing import Union, List
import argostranslate.package
import argostranslate.translate
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document


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


def translate_ts(modeladmin, request, queryset):
	for ts in queryset:
		from_code = ts.language
		to_code = 'en'
		translatedText = argostranslate.translate.translate(ts.full, from_code, to_code)
		t = Translation.objects.create(
			transcript = ts,
			media = ts.media,
			title = ts.media.title,
			language = to_code,
			full = translatedText
		)
	return HttpResponseRedirect(f'/admin/smartsum/translation/{ts.id}/')

translate_ts.short_description = 'Translate - EN'


def summarize(modeladmin, request, queryset):
	for t in queryset:
		if t.full:
			# Split the text into chunks for processing and create Document object
			chunks = CharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_text(t.full)
			docs = [Document(page_content=chunk) for chunk in chunks]
			# Initialize the LLM with llama3.2 model and load the summarization chain
			chain = load_summarize_chain(OllamaLLM(model="llama3.2"), chain_type="map_reduce")
			t.summary = chain.invoke(docs)['output_text']
			t.save()
