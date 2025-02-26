import os

DIR_ROOT = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUT = os.path.join(DIR_ROOT, "out")
DIR_INGEST = os.path.join(DIR_ROOT, "docs")

PATH_LOG = os.path.join(DIR_OUTPUT, "logs.log")
PATH_TARGET_COURSE_NAMES = os.path.join(DIR_ROOT, "target_course_names.csv")
PATH_OUTPUT_DATA = os.path.join(DIR_OUTPUT, "output.csv")
PATH_FILTERED_DATA = os.path.join(DIR_OUTPUT, "filtered.csv")
PATH_DEBUG_EXTRACTED_TEXT = os.path.join(DIR_OUTPUT, "debug_extracted_text.txt")
PATH_REPORT = os.path.join(DIR_OUTPUT, "report.csv")
