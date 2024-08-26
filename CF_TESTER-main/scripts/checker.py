import os
import subprocess
import sys
import html

class bcolors:
    HEADER = '#C5CAE9'
    OKBLUE = '#64B5F6'
    OKCYAN = '#4DD0E1'
    OKGREEN = '#81C784'
    WARNING = '#FFD54F'
    FAIL = '#EF5350'
    ENDC = '#000000'
    BOLD = 'font-weight: bold;'
    UNDERLINE = 'text-decoration: underline;'
    WARNING2 = '#FF4081'

def get_tests():
    """
    Gets all the test cases for the current directory
    Test cases must have the .in extension
    """
    input_files = []
    output_files = []
    for file in os.listdir('.'):
        if file.endswith('.in'):
            input_files.append(file)
        elif file.endswith('.out'):
            output_files.append(file)
    return input_files, output_files

def escape_html(text):
    """Escape HTML special characters"""
    return html.escape(text)

def format_html_header(text, color):
    """Format header with color"""
    return f'<h2 style="color: {color};">{text}</h2>'

def format_html_pre(content, color):
    """Format preformatted content with color"""
    return f'<pre style="background: {color}; padding: 10px; border-radius: 4px; overflow: auto; max-height: 400px; color: #000000;">{content}</pre>'

def format_html_input(input_lines):
    """Format the input file content as HTML"""
    if input_lines:
        # Strip any trailing newlines from each line and join them with <br>
        input_html = "<br>".join(escape_html(line).strip() for line in input_lines if line.strip())
        return format_html_header("Input:", bcolors.OKBLUE) + format_html_pre(input_html, bcolors.OKBLUE)
    return ""


def format_results_html(results_lines, expected_lines):
    """Format the results as HTML"""
    html_content = format_html_header("Results:", bcolors.OKBLUE)
    results_html = "<br>".join(escape_html(line) for line in results_lines)
    html_content += format_html_pre(results_html, bcolors.OKBLUE)

    if expected_lines:
        expected_html = "<br>".join(escape_html(line) for line in expected_lines)
        html_content += format_html_header("Expected:", bcolors.OKBLUE)
        html_content += format_html_pre(expected_html, bcolors.OKBLUE)

    return html_content

def format_debug_html(debug_lines):
    """Format debug information as HTML"""
    if debug_lines:
        debug_html = "<br>".join(escape_html(line) for line in debug_lines)
        return format_html_header("Debug:", bcolors.WARNING) + format_html_pre(debug_html, bcolors.WARNING)
    return ""

def format_status_html(successful):
    """Format the status as HTML"""
    if successful:
        return format_html_header("ALL SAMPLES PASSED", bcolors.OKGREEN)
    else:
        return format_html_header("FAILED SAMPLES", bcolors.FAIL)

def run_test(input_file: str, output_files: list[str], executable: str):
    """
    Run the executable with the given input file
    Capture the output and debug print statements
    """
    p = subprocess.Popen([executable], stdin=open(input_file, 'r'),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results_lines = []
    debug_lines = []
    expected_lines = []
    for line in p.stdout.readlines():
        line = line.decode("utf-8").strip()
        if len(line):
            results_lines.append(line)
    for line in p.stderr.readlines():
        line = line.decode("utf-8").strip()
        if len(line):
            debug_lines.append(line)
    
    expected_output_file = input_file.replace(".in", ".out")
    if expected_output_file in output_files:
        with open(expected_output_file) as f:
            for line in f.readlines():
                line = line.strip()
                if len(line):
                    expected_lines.append(line)
    return results_lines, debug_lines, expected_lines

def determine_status(results_lines, expected_lines):
    """
    Return true if test didn't fail
    Return false if test failed
    """
    if len(expected_lines) == 0:
        return True
    if len(results_lines) != len(expected_lines):
        return False
    else:
        for i in range(len(results_lines)):
            if results_lines[i].lower() != expected_lines[i].lower():
                return False
    return True

def test_code(executable: str):
    """
    Given all test files, run code on it and see if output is correct
    """
    input_files, output_files = get_tests()
    successful = True
    html_output = ""

    for test in input_files:
        with open(test) as f:
            input_lines = f.readlines()

        results_lines, debug_lines, expected_lines = run_test(test, output_files, executable)
        html_output += f'<h1>Running on test {escape_html(test)}</h1>'
        successful &= determine_status(results_lines, expected_lines)
        html_output += format_html_input(input_lines)
        html_output += format_results_html(results_lines, expected_lines)
        html_output += format_debug_html(debug_lines)
    
    html_output += format_status_html(successful)
    
    # Output results as JavaScript code for the HTML page
    print(html_output)

if __name__ == "__main__":
    executable = sys.argv[1]
    test_code(executable)
