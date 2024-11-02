import extract_pdf

def test_target_courses_no_file_exists():
	"""
	Tests if the target courses file exists.
	"""

	test_filepath =	"test/data/test_target_courses_no_file_exists.txt"

	results = extract_pdf.__get_target_course_names(test_filepath)

	assert results == []


def test_target_courses_empty_file():
	"""
	Tests if the target courses file is empty.
	"""

	test_filepath =	"test/data/test_target_courses_empty_file.txt"

	results = extract_pdf.__get_target_course_names(test_filepath)

	assert results == []


def test_target_courses_one_target():
	"""
	Tests that it can extract the target course name correctly.
	"""

	test_filepath =	"test/data/test_target_courses_one_target.txt"

	results = extract_pdf.__get_target_course_names(test_filepath)

	assert results == ["ABC"]


def test_target_courses_ten_targets():
	"""
	Tests that all courses are extracted correctly.
	"""

	test_filepath =	"test/data/test_target_courses_ten_targets.txt"

	results = extract_pdf.__get_target_course_names(test_filepath)

	assert len(results) == 10
	assert results == ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWX", "YZA", "ZZZ"]


def test_target_courses_correctly_cleaned():
	"""
	Tests that the target courses are cleaned correctly.
	"""

	test_filepath =	"test/data/test_target_courses_correctly_cleaned.txt"

	results = extract_pdf.__get_target_course_names(test_filepath)

	assert len(results) == 4
	assert extract_pdf.__get_target_course_names(test_filepath) == ["ABC", "DEF", "GHI", "Z Z Z"]