from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import csv
import os
import json
import tempfile
import subprocess
from flask import Flask, request, jsonify
app = Flask(__name__)
CORS(app)

frontend_url = 'http://192.168.1.7:8501'

def check_credentials(username, password):
    base_dir = os.path.dirname(__file__)
    csv_file_path = os.path.join(base_dir, 'passwords.csv')

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['username'] == username and row['password'] == password:
                return True
    return False

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    credentials_check = check_credentials(username, password)
    
    if credentials_check: 
        redirect_url = f"{frontend_url}?username={username}&embed=true"
        return jsonify({"message": "Login successful", "url": redirect_url}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route('/questions', methods=['POST'])
def get_problem():
    data = request.get_json()
    username = data.get('username', '')

    base_dir = os.path.dirname(__file__)
    user_info_filepath = os.path.join(base_dir, "user_info.csv")

    if not os.path.isfile(user_info_filepath):
        return jsonify({"error": "File not found"}), 404

    name = None
    test_id = None
    with open(user_info_filepath, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username:
                name = row['name']
                test_id = row['test_id']
                break

    test_id_filepath = os.path.join(base_dir, f"{test_id}.csv")

    if not os.path.isfile(test_id_filepath):
        return jsonify({"error": "Test ID file not found"}), 404

    response = send_file(test_id_filepath, mimetype='text/csv', as_attachment=True, download_name=f"{test_id}.csv")
    response.headers['X-User-Name'] = name
    response.headers['X-Test-ID'] = test_id

    return response

def load_test_cases():
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "test_cases.json")
    with open(filepath, 'r') as f:
        return json.load(f)

# Route to handle code submission
@app.route('/submit', methods=['POST'])
def submit_code():
    data = request.json
    code = data['code']
    language = data['language']
    problem_title = data['problem_title']

    # Load the test cases for the given problem
    test_cases = next((p['test_cases'] for p in load_test_cases() if p['title'] == problem_title), None)
    if not test_cases:
        return jsonify({'error': 'Problem not found'}), 404

    # Define file extensions for each language
    file_extensions = {
        'python': '.py',
        'c': '.c',
        'cpp': '.cpp',
        'java': '.java',
        'javascript': '.js'
    }

    # Define run commands for each language
    run_commands = {
        'python': 'python "{code_file}"',
        'c': 'gcc "{code_file}" -o "{exe_file}" && "{exe_file}"',
        'cpp': 'g++ "{code_file}" -o "{exe_file}" && "{exe_file}"',
        'java': 'javac "{code_file}" && java -cp "{folder}" Code',
        'javascript': 'node "{code_file}"'
    }

    # Check if the language is supported
    if language not in file_extensions:
        return jsonify({'error': 'Unsupported language'}), 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the code file
            code_file_extension = file_extensions[language]
            code_file_name = f'code{code_file_extension}'
            code_file_path = os.path.join(temp_dir, code_file_name)

            with open(code_file_path, 'w') as code_file:
                code_file.write(code)

            # Prepare results list
            results = []

            for test_case in test_cases:
                input_data = test_case['input']
                expected_output = test_case['output']

                # Write input to a file (input.txt)
                input_file_path = os.path.join(temp_dir, 'input.txt')
                with open(input_file_path, 'w') as input_file:
                    json.dump(input_data, input_file)

                # Print to verify the input is being written correctly
                print(f"Input data for test case: {input_data}")

                # Modify the code for Python to handle input directly
                if language == 'python':
                    code_with_input_handling = f"""
import json
with open('input.txt', 'r') as f:
    input_data = json.load(f)

nums = input_data['nums']
target = input_data['target']

result = two_sum(nums, target)
print(result)
"""
                    with open(code_file_path, 'w') as code_file:
                        code_file.write(code + "\n" + code_with_input_handling)

                # Execute the code based on the language
                command = run_commands[language].format(
                    code_file=code_file_path,
                    exe_file=os.path.join(temp_dir, 'a.exe'),
                    folder=temp_dir
                )

                try:
                    process_result = subprocess.run(
                        command, shell=True, capture_output=True, text=True, cwd=temp_dir
                    )
                    output = process_result.stdout.strip()
                    stderr_output = process_result.stderr.strip()
                    exit_code = process_result.returncode

                    # Debug: Log the output and errors for inspection
                    print(f"Command output: {output}")
                    print(f"Command stderr: {stderr_output}")
                    print(f"Exit code: {exit_code}")

                    # If there's an error, capture the stderr output
                    if exit_code != 0:
                        result_output = f"Error: {stderr_output}"
                    else:
                        result_output = output

                    # Compare the output with the expected result
                    if result_output:
                        try:
                            parsed_output = json.loads(result_output)
                            print(parsed_output)
                        except json.JSONDecodeError:
                            parsed_output = result_output
                    else:
                        parsed_output = None

                    results.append({
                        'input': input_data,
                        'expected': expected_output,
                        'output': parsed_output,
                        'pass': parsed_output == expected_output,
                        'error': stderr_output if exit_code != 0 else ''
                    })

                except Exception as e:
                    return jsonify({'error': f'Unexpected error while executing: {str(e)}'}), 500

            return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
