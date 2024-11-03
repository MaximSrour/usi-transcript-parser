"""

"""

import fitz
import re
import os
import csv
from tqdm import tqdm

from logger_util import get_logger

DIR_ROOT = "."
DIR_OUTPUT = os.path.join(DIR_ROOT, "out")
DIR_INGEST = os.path.join(DIR_ROOT, "docs")

PATH_TARGET_COURSE_NAMES = os.path.join(DIR_ROOT, "target_course_names.txt")
PATH_OUTPUT_DATA = os.path.join(DIR_OUTPUT, "output.csv")
PATH_FILTERED_DATA = os.path.join(DIR_OUTPUT, "filtered.csv")
PATH_DEBUG_EXTRACTED_TEXT = os.path.join(DIR_OUTPUT, "debug_extracted_text.txt")

DEBUG = False

logger = get_logger(__name__)


def __get_target_course_names(filepath = None) -> list[str]:
	"""
	Returns the target course names from a file.

	@return {list[str]} - List of target course names.
	"""

	#TODO: Return a set instead

	if filepath is None:
		filepath = PATH_TARGET_COURSE_NAMES

	try:
		with open(filepath, "r") as file:
			contents = [line.strip().upper() for line in file.readlines()]

			# Remove duplicates and empty lines
			contents = list(filter(None, set(contents)))
			contents.sort()

			return contents

	except Exception as e:
		logger.error(f"Error reading target course names: {e}")
		return []


def __get_all_text(pdf_path: str) -> str:
	"""
	Extracts all text from a PDF file.

	@param {str} pdf_path - Path to the PDF file.
	@return {str} - All text from the PDF file as a raw string.
	"""

	doc = fitz.open(pdf_path)
	all_text = ""

	for i in range(len(doc)):
		page = doc.load_page(i)
		all_text += page.get_text()
	
	return __sanitise_text(all_text)


def __sanitise_text(text: str) -> str:
	"""
	Sanitises the text extracted from a PDF file.

	@param {str} text - Raw text extracted from a PDF file.
	@return {str} - Sanitised text.
	"""

	sanitised_text = re.sub(r"\(IdenƟĮer\) - \(FIⁱⁱ\)\n", "---\n", text)
	return sanitised_text


def __get_name_from_text(text: str) -> str:
	"""
	Extracts the name of the person from the text.

	@param {str} text - Raw text extracted from a PDF file.
	@return {str} - Name of the person.
	"""


	expression = r"(.*)(?:\nPage  \d+ of \d+)"
	data = re.findall(expression, text)

	if data:
		# This is necessary since the structure of the PDF is not consistent and
		# the name on the first page is not extracted correctly.
		#TODO: Fix the case where only one instance of the name is found which is not the correct one.
			# Consider using the filename (meh option) or use a better regex to extract more options to consider.
		most_common = max(set(data), key=data.count)
		return most_common.title()
	else:
		return None


def __get_all_courses(text: str) -> list[list[str]]:
	"""
	Extracts all courses from the text.

	@param {str} text - Raw text extracted from a PDF file.
	@return {list[list[str]]} - List of courses.
	"""

	expression = r"(.*)(\n.*){0,1}\n(.*)\n\((.*)\) - \(.*\)(?:\n\d{2}\/\d{2}\/\d{4}-\d{2}\/\d{2}\/\d{4})"
	data = re.findall(expression, text)
	
	output = []
	for row in data:
		text = row[0] + row[1]
		text = re.sub(r"\n", " ", text)
		text = re.sub(r"---", "", text)
		text = text.strip()
		output += [[row[3], text, row[2]]]

	return output


def __find_all_pdfs() -> list[str]:
	"""
	Finds all PDF files in the ingest directory.

	@return {list[str]} - List of paths to all PDF files.
	"""

	pdfs = []
	for root, dirs, files in os.walk(DIR_INGEST):
		for file in files:
			if file.endswith(".pdf"):
				pdfs.append(os.path.join(root, file))
	return pdfs


def __filter_data(data: list[list[str]]) -> list[list[str]]:
	"""
	Filters the data to only include the target courses.
	
	@param {list[list[str]]} data - List of data.
	@return {list[list[str]]} - Filtered data.
	"""

	filtered_data = []
	for row in data:
		if row[3] in __get_target_course_names():
			filtered_data.append(row)
	return filtered_data


def __write_to_csv(data: list[list[str]], path: str) -> None:
	"""
	Writes the data to a CSV file.

	@param {list[list[str]]} data - List of data.
	@param {str} path - Path to the CSV file.
	"""

	try:
		with open(path, "w") as f:
			writer = csv.writer(f)
			writer.writerow(["Name", "Pass", "Course Code", "Course Name"])
			writer.writerows(data)

		logger.info(f"Successfully wrote to CSV file: {path}")

	except Exception as e:
		logger.error(f"Error writing to CSV file: {e}")


def process_pdf(pdf_path: str) -> list[list[str]]:
	"""
	Processes a PDF file.

	@param {str} pdf_path - Path to the PDF file.
	@return {list[list[str]]} - List of data.
	"""

	extracted_text = __get_all_text(pdf_path)
	name = __get_name_from_text(extracted_text)
	
	if DEBUG:
		with open(PATH_DEBUG_EXTRACTED_TEXT, "w") as f:
			f.write(extracted_text)
		
	course_data = __get_all_courses(extracted_text)

	output = []
	for row in course_data:
		row = [name, row[2], row[0], row[1]]
		output.append(row)

	return output


def process_all_pdfs() -> None:
	"""
	Processes all PDF files in the ingest directory.
	"""

	pdf_paths = __find_all_pdfs()

	if len(pdf_paths) == 0:
		logger.warning("No PDF files found in the ingest directory.")
		exit()

	output_data = []
	filtered_data = []

	logger.info(f"Processing {len(pdf_paths)} PDF files...")

	for pdf_path in tqdm(pdf_paths, leave=False):
		output_data += process_pdf(pdf_path)

	output_data.sort(key=lambda x: (x[0], x[3]))

	logger.info("Finished!")

	filtered_data = __filter_data(output_data)

	__write_to_csv(output_data, PATH_OUTPUT_DATA)
	__write_to_csv(filtered_data, PATH_FILTERED_DATA)


def init() -> None:
	"""
	Initialises the program.
	"""

	should_rerun = False

	if not os.path.exists(DIR_OUTPUT):
		os.makedirs(DIR_OUTPUT)

	if not os.path.exists(DIR_INGEST):
		os.makedirs(DIR_INGEST)
		should_rerun = True

	if not os.path.exists(PATH_TARGET_COURSE_NAMES):
		with open(PATH_TARGET_COURSE_NAMES, "w") as f:
			pass
		should_rerun = True

	if should_rerun:
		logger.warning("Please place the PDF files in the ingest directory and re-run the script.")
		exit()


def main() -> None:
	"""
	Main function.
	"""

	init()

	process_all_pdfs()


if __name__ == "__main__":
	main()