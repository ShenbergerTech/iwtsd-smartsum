from django.core.management.base import BaseCommand, CommandError
import argostranslate.package
import argostranslate.translate


class Command(BaseCommand):
	help = "Downloads Argos Translate language packs."

	# def add_arguments(self, parser):
	#     parser.add_argument("poll_ids", nargs="+", type=int)

	def handle(self, *args, **options):
		# Update package index to find available packages
		argostranslate.package.update_package_index()
		available_packages = argostranslate.package.get_available_packages()

		# Define source and target languages
		from_code = "he"  # Hebrew
		to_code = "en"    # English

		# Find and install the required language package
		print(f'Downloading {from_code} to {to_code}...')
		package_to_install = next(
			filter(
				lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
			)
		)
		argostranslate.package.install_from_path(package_to_install.download())

		from_code = "fa"  # Farsi
		to_code = "en"    # English

		# Find and install the required language package
		print(f'Downloading {from_code} to {to_code}...')
		package_to_install = next(
			filter(
				lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
			)
		)
		argostranslate.package.install_from_path(package_to_install.download())

		from_code = "en"  # English
		to_code = "fa"    # Farsi

		# Find and install the required language package
		print(f'Downloading {from_code} to {to_code}...')
		package_to_install = next(
			filter(
				lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
			)
		)
		argostranslate.package.install_from_path(package_to_install.download())

		# from_code = "fa"  # Farsi
		# to_code = "he"    # Hebrew

		# # Find and install the required language package
		# print(f'Downloading {from_code} to {to_code}...')
		# package_to_install = next(
		# 	filter(
		# 		lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
		# 	)
		# )
		# argostranslate.package.install_from_path(package_to_install.download())

