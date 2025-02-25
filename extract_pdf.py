"""

"""

import csv
import os
import re
from typing import List, Union

import fitz  # type: ignore
from tqdm import tqdm

from datatypes import Course, Result
from logger_util import get_logger

DIR_ROOT = "."
DIR_OUTPUT = os.path.join(DIR_ROOT, "out")
DIR_INGEST = os.path.join(DIR_ROOT, "docs")

PATH_TARGET_COURSE_NAMES = os.path.join(DIR_ROOT, "target_course_names.csv")
PATH_OUTPUT_DATA = os.path.join(DIR_OUTPUT, "output.csv")
PATH_FILTERED_DATA = os.path.join(DIR_OUTPUT, "filtered.csv")
PATH_DEBUG_EXTRACTED_TEXT = os.path.join(DIR_OUTPUT, "debug_extracted_text.txt")
PATH_REPORT = os.path.join(DIR_OUTPUT, "report.csv")

logger = get_logger(__name__)


def __init():
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
        with open(PATH_TARGET_COURSE_NAMES, "w"):
            pass
        should_rerun = True

    if should_rerun:
        # TODO: Make the error messages specific for the reason it failed
        logger.warning(
            "Please place the PDF files in the ingest directory and re-run the script."
        )
        exit()


def __get_target_courses(filepath: Union[os.PathLike[str], str, None] = None):
    """
    Returns the target course names from a file.

    @return {list[str]} - List of target course names.
    """

    # TODO: Return a set instead

    if filepath is None:
        filepath = PATH_TARGET_COURSE_NAMES

    try:

        with open(filepath, "r") as f:
            reader = csv.reader(f)
            contents = list(reader)[1:]

            courses: List[Course] = []
            for i in range(len(contents)):
                course_code = contents[i][0]
                course_name = contents[i][1]

                courses.append(Course(course_code, course_name))

            courses.sort(key=lambda x: x.name)

            return courses

    except Exception as e:
        logger.error(f"Error reading target course names: {e}")
        return list[Course]()


def __get_all_text(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file.

    @param {str} pdf_path - Path to the PDF file.
    @return {str} - All text from the PDF file as a raw string.
    """

    doc = fitz.open(pdf_path)
    all_text: str = ""

    for i in range(len(doc)):
        page = doc.load_page(i)
        all_text += page.get_text()

    return __sanitise_text(all_text)


def __sanitise_text(text: str):
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
        # TODO: Fix the case where only one instance of the name is found which is not the correct one.
        # Consider using the filename (meh option) or use a better regex to extract more options to consider.
        # Temporary fix
        for i in range(len(data) - 1, -1, -1):
            if "Transcript" in data[i]:
                del data[i]

        most_common = max(set(data), key=data.count)
        return most_common.title()
    else:
        # TODO: Instead of None, return the filename
        return None


def __get_all_courses(text: str, student_name: str):
    """
    Extracts all courses from the text.

    @param {str} text - Raw text extracted from a PDF file.
    @return {list[list[str]]} - List of courses.
    """

    expression = r"(.*)(\n.*){0,1}\n(.*)\n\((.*)\) - \(.*\)(?:\n\d{2}\/\d{2}\/\d{4}-\d{2}\/\d{2}\/\d{4})"
    data = re.findall(expression, text)

    output: List[Result] = []
    for row in data:
        course_name = row[0] + row[1]
        course_name = re.sub(r"\n", " ", course_name)
        course_name = re.sub(r"---", "", course_name)
        course_name = course_name.strip()

        mark = row[2]
        course_code = row[3]

        output.append(Result(student_name, mark, Course(course_code, course_name)))

    return output


def __find_all_pdfs() -> list[str]:
    """
    Finds all PDF files in the ingest directory.

    @return {list[str]} - List of paths to all PDF files.
    """

    pdfs: List[str] = []
    for root, _, files in os.walk(DIR_INGEST):
        for file in files:
            if file.endswith(".pdf"):
                pdfs.append(os.path.join(root, file))

    return pdfs


def __filter_data(data: List[Result]):
    """
    Filters the data to only include the target courses.

    @param {list[list[str]]} data - List of data.
    @return {list[list[str]]} - Filtered data.
    """

    course_data = __get_target_courses()

    course_codes = [course.code for course in course_data]
    course_names = [course.name for course in course_data]

    filtered_data: List[Result] = []

    for result in data:
        if result.course.code in course_codes and result.course.name in course_names:
            filtered_data.append(result)

    return filtered_data


def __write_to_csv(data: List[Result], path: str):
    """
    Writes the data to a CSV file.

    @param {list[list[str]]} data - List of data.
    @param {str} path - Path to the CSV file.
    """

    try:
        with open(path, "w") as f:
            # TODO: Replace with Pandas
            writer = csv.writer(f)
            writer.writerow(["Name", "Pass", "Course Code", "Course Name"])
            writer.writerows([result.to_list() for result in data])

        logger.info(f"Successfully wrote to CSV file: {path}")

    except Exception as e:
        logger.error(f"Error writing to CSV file: {e}")


def process_pdf(pdf_path: str, write_debug: bool = False) -> List[Result]:
    """
    Processes a PDF file.
    @param {str} pdf_path - Path to the PDF file.
    @return {list[list[str]]} - List of data.
    """

    extracted_text = __get_all_text(pdf_path)
    if write_debug:
        with open(PATH_DEBUG_EXTRACTED_TEXT, "w") as f:
            f.write(extracted_text)

    name = __get_name_from_text(extracted_text)
    course_data = __get_all_courses(extracted_text, name)

    return course_data


def process_all_pdfs():
    """
    Processes all PDF files in the ingest directory.
    """

    pdf_paths = __find_all_pdfs()

    if len(pdf_paths) == 0:
        logger.warning("No PDF files found in the ingest directory.")
        exit()

    output_data: List[Result] = []
    filtered_data: List[Result] = []

    logger.info(f"Processing {len(pdf_paths)} PDF files...")

    for pdf_path in tqdm(pdf_paths, leave=False):
        output_data += process_pdf(pdf_path)

    output_data.sort(key=lambda x: (x.student_name, x.course.name))

    logger.info("Finished!")

    filtered_data = __filter_data(output_data)

    __write_to_csv(output_data, PATH_OUTPUT_DATA)
    __write_to_csv(filtered_data, PATH_FILTERED_DATA)


def test_solo():
    """
    Tests a single PDF file.
    """

    pdf_path = "./docs/Matt Croft 100682228 USI Transcript1.pdf"
    output_data = process_pdf(pdf_path, write_debug=True)

    print(output_data)


def main():
    """
    Main function.
    """

    __init()

    process_all_pdfs()


if __name__ == "__main__":
    main()
    # test_solo()
