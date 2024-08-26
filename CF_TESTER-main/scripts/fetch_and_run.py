import requests
import re
import subprocess
import sys
import cloudscraper

class bcolors:
    HEADER = ''
    OKBLUE = ''
    OKCYAN = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''

def raw(string: str, replace: bool = False) -> str:
    r = repr(string)[1:-1]
    if replace:
        r = r.replace('\\\\', '\\')
    return r

def make_file(file_name, content):
    with open(file_name, 'w') as file:
        file.write(content)

def parse_problem(LINK, path="./"):
    try:
        scraper = cloudscraper.create_scraper()
        f = scraper.get(LINK)
        all_starts = [m.start() for m in re.finditer("<pre>", f.text)]
        all_ends = [m.start() for m in re.finditer("</pre>", f.text)]
        inputs = []
        outputs = []
        for i in range(len(all_starts)):
            if(i & 1):
                outputs.append((all_starts[i], all_ends[i]))
            else:
                inputs.append((all_starts[i], all_ends[i]))

        current_input_num = 1
        current_output_num = 1
        for i in range(len(inputs)):
            item = inputs[i]
            raw_str = f.text[item[0]:item[1]].replace("<br />", "\n").replace("<pre>", "")
            raw_str = re.sub(r"<div class=.*?>", "", raw_str)
            raw_str = re.sub(r"</div>", "\n", raw_str)
            s = raw_str.strip()
            make_file(f"{path}{current_input_num}.in", s)
            current_input_num += 1

            item = outputs[i]
            raw_str = f.text[item[0]:item[1]].replace("<br />", "\n").replace("<pre>", "")
            raw_str = re.sub(r"<div class=.*?>", "", raw_str)
            raw_str = re.sub(r"</div>", "\n", raw_str)
            s = raw_str.strip()
            make_file(f"{path}{current_output_num}.out", s)
            current_output_num += 1

    except Exception as e:
        print(f"Error: {str(e)}")

def run_test(executable: str, input_file: str) -> str:
    p = subprocess.Popen(f'./{executable} < {input_file}', shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    return output.decode('utf-8')

def main():
    LINK = sys.argv[1]
    parse_problem(LINK)
    executable = "a.out"  # Replace with your compiled C++ binary
    input_files, _ = get_tests()
    for input_file in input_files:
        result = run_test(executable, input_file)
        print(result)

if __name__ == "__main__":
    main()
