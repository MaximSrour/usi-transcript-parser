import copy
import csv

from extract_pdf import PATH_FILTERED_DATA, PATH_REPORT


def determine_value(
    row: list, target_courses: list[tuple[str, str]]
) -> tuple[str, str]:
    """
    Determines the value of the row.

    Check which course it match based on the names
    """

    name, grade, course_id, course_name = row

    if name == "Anthony Dennis Wills" and course_name == "WORK SAFELY AT HEIGHTS":
        pass

    for val in target_courses:
        target_course_id, target_course_name = val
        if target_course_name.upper() == course_name.upper():
            break
    else:
        target_course_id, target_course_name = None, None

    if grade == "CA":
        if course_id == target_course_id:
            return ("Y", None)
        else:
            return ("POSSIBLE", course_id)

    if grade in ["RPL", "CT"]:
        return ("POSSIBLE", course_id)

    return ("N", None)


def main() -> None:
    """
    Main function.
    """

    # if not PATH_OUTPUT_DATA.exists():
    #     print(f"Error: {PATH_OUTPUT_DATA} does not exist.")
    #     exit()

    # if not PATH_FILTERED_DATA.exists():
    #     print(f"Error: {PATH_FILTERED_DATA} does not exist.")
    #     exit()

    target_courses = list(csv.reader(open("target_courses.csv", "r")))

    filtered_data = csv.reader(open(PATH_FILTERED_DATA, "r"))

    """
    Each row is of the format:
        Name, Grade, Course ID, Course Name
    There are approx 20 target courses in the target_courses.csv file
    For each student, we need to find the target courses and their grades
    For each one, run a number of checks:
        If grade is CA and the ID matches what is in the target_courses, then it should return (Y, None)
        If grade is CA and the ID does not match what is in the target_courses, then it should return (POSSIBLE, the ID)
        If grade is RPL or CT, then it should return (POSSIBLE, the ID)
        Otherwise, it should return (N, None)
    """

    output = []

    for row in filtered_data:
        value = determine_value(row, target_courses)

        out = copy.deepcopy(row)
        out.extend(value)
        output.append(out)

    with open(PATH_REPORT, "w") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Name", "Grade", "Course ID", "Course Name", "Value", "Possible ID"]
        )
        writer.writerows(output[1:])


if __name__ == "__main__":
    main()
