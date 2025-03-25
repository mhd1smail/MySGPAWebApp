from flask import Flask, render_template, request

app = Flask(__name__)

# Define the grading system
grades = {
    "O": (91, 100, 10),
    "A+": (81, 90, 9),
    "A": (71, 80, 8),
    "B+": (61, 70, 7),
    "B": (56, 60, 6),
    "C": (50, 55, 5),
    "F": (0, 49, 0)  # Fail
}

# Function to convert end-sem marks (out of 75) to out of 40
def convert_to_40(marks_out_of_75):
    return (marks_out_of_75 / 75) * 40

# Function to convert required end-sem marks (out of 40) back to out of 75
def convert_to_75(marks_out_of_40):
    return (marks_out_of_40 / 40) * 75

# Calculate minimum required end-sem marks for each grade
def calculate_minimum_endsem(internal_marks):
    results = {}
    for grade, (min_percent, max_percent, grade_points) in grades.items():
        min_total_marks = (min_percent / 100) * 100
        required_endsem_40 = max(0, min_total_marks - internal_marks)
        required_endsem_75 = convert_to_75(required_endsem_40)
        results[grade] = required_endsem_75
    return results

# Function to get grade points
def get_grade_points(achieved_grade):
    return grades.get(achieved_grade, 0)[2]

@app.route('/', methods=['GET', 'POST'])
def index():
    result_text = ""
    if request.method == 'POST':
        subjects = []
        total_weighted_points = 0
        total_credits = 0

        for i in range(1, 100):  # Assuming a maximum of 99 subjects
            subject_name = request.form.get(f'subject_name_{i}')
            credits = request.form.get(f'credits_{i}')
            internal_marks = request.form.get(f'internal_marks_{i}')

            if not subject_name:
                break

            try:
                credits = int(credits)
                internal_marks = float(internal_marks)
                if 0 <= internal_marks <= 60:
                    subjects.append({
                        "name": subject_name,
                        "credits": credits,
                        "internal_marks": internal_marks
                    })
                else:
                    result_text += f"Invalid internal marks for {subject_name}. Please enter a value between 0 and 60.\n"
            except ValueError:
                result_text += f"Invalid input for {subject_name}. Please enter numeric values for credits and internal marks.\n"

        if not subjects:
            return render_template('index.html', result_text="No subjects were entered. Please add at least one subject.")

        for subject in subjects:
            subject_name = subject["name"]
            internal_marks = subject["internal_marks"]
            min_endsem_marks = calculate_minimum_endsem(internal_marks)
            result_text += f"\nSubject: {subject_name}\nMinimum End-Sem Marks (out of 75) to Achieve Each Grade:\n"
            for grade, marks in min_endsem_marks.items():
                result_text += f"{grade}: {marks:.2f}\n"

        # Pass subjects to the next page for grade entry
        return render_template('enter_grades.html', subjects=subjects, result_text=result_text)

    return render_template('index.html')

@app.route('/enter_grades', methods=['POST'])
def enter_grades():
    subjects = []
    total_weighted_points = 0
    total_credits = 0
    result_text = ""

    for i in range(1, 100):  # Assuming a maximum of 99 subjects
        subject_name = request.form.get(f'subject_name_{i}')
        credits = request.form.get(f'credits_{i}')
        internal_marks = request.form.get(f'internal_marks_{i}')

        if not subject_name:
            break

        try:
            credits = int(credits)
            internal_marks = float(internal_marks)
            if 0 <= internal_marks <= 60:
                subjects.append({
                    "name": subject_name,
                    "credits": credits,
                    "internal_marks": internal_marks
                })
            else:
                result_text += f"Invalid internal marks for {subject_name}. Please enter a value between 0 and 60.\n"
        except ValueError:
            result_text += f"Invalid input for {subject_name}. Please enter numeric values for credits and internal marks.\n"

    if not subjects:
        return render_template('index.html', result_text="No subjects were entered. Please add at least one subject.")

    for subject in subjects:
        subject_name = subject["name"]
        internal_marks = subject["internal_marks"]
        min_endsem_marks = calculate_minimum_endsem(internal_marks)
        result_text += f"\nSubject: {subject_name}\nMinimum End-Sem Marks (out of 75) to Achieve Each Grade:\n"
        for grade, marks in min_endsem_marks.items():
            result_text += f"{grade}: {marks:.2f}\n"

    # Pass subjects to the next page for grade entry
    return render_template('submit_grades.html', subjects=subjects, result_text=result_text)

@app.route('/submit_grades', methods=['POST'])
def submit_grades():
    subjects = []
    total_weighted_points = 0
    total_credits = 0
    result_text = ""

    for i in range(1, 100):  # Assuming a maximum of 99 subjects
        subject_name = request.form.get(f'subject_name_{i}')
        credits = request.form.get(f'credits_{i}')
        internal_marks = request.form.get(f'internal_marks_{i}')
        achieved_grade = request.form.get(f'achieved_grade_{i}', 'F')  # Default to 'F' if grade is missing

        if not subject_name:
            break

        try:
            credits = int(credits)
            internal_marks = float(internal_marks)
            if 0 <= internal_marks <= 60:
                subjects.append({
                    "name": subject_name,
                    "credits": credits,
                    "internal_marks": internal_marks,
                    "achieved_grade": achieved_grade
                })
            else:
                result_text += f"Invalid internal marks for {subject_name}. Please enter a value between 0 and 60.\n"
        except ValueError:
            result_text += f"Invalid input for {subject_name}. Please enter numeric values for credits and internal marks.\n"

    if not subjects:
        return render_template('submit_grades.html', subjects=[], result_text="No subjects were entered to calculate SGPA.")

    for subject in subjects:
        subject_name = subject["name"]
        internal_marks = subject["internal_marks"]
        min_endsem_marks = calculate_minimum_endsem(internal_marks)
        result_text += f"\nSubject: {subject_name}\nMinimum End-Sem Marks (out of 75) to Achieve Each Grade:\n"
        for grade, marks in min_endsem_marks.items():
            result_text += f"{grade}: {marks:.2f}\n"

        achieved_grade = subject["achieved_grade"].strip().upper()
        grade_points = get_grade_points(achieved_grade)
        if grade_points == 0:
            result_text += f"Invalid grade entered for {subject_name}. Assuming 'F' with 0 grade points.\n"
        weighted_points = grade_points * subject["credits"]
        total_weighted_points += weighted_points
        total_credits += subject["credits"]

    if total_credits > 0:
        sgpa = total_weighted_points / total_credits
        return render_template('results.html', sgpa=f"{sgpa:.2f}")
    else:
        return render_template('submit_grades.html', subjects=subjects, result_text="No subjects were entered to calculate SGPA.")

if __name__ == '__main__':
    app.run(debug=True)