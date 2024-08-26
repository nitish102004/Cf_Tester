import requests
import re
import os
import sys
import cloudscraper


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[33m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def raw(string: str, replace: bool = False) -> str:
    """Returns the raw representation of a string. If replace is true, replace a single backslash's repr \\ with \\."""
    r = repr(string)[1:-1]  # Strip the quotes from representation
    if replace:
        r = r.replace('\\\\', '\\')
    return r


def make_file(file_name, content):
    with open(file_name, 'w') as file:
        file.write(content)


def make_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def parse_problem(LINK, path="./"):
    try:
        name = LINK.split('/')[-1]
        scraper = cloudscraper.create_scraper()
        f = scraper.get(LINK)
        all_starts = [m.start() for m in re.finditer("<pre>", f.text)]
        all_ends = [m.start() for m in re.finditer("</pre>", f.text)]
        inputs = []
        outputs = []
        for i in range(len(all_starts)):
            if i % 2 == 0:
                inputs.append((all_starts[i], all_ends[i]))
            else:
                outputs.append((all_starts[i], all_ends[i]))
        current_input_num = 1
        current_output_num = 1
        for i in range(len(inputs)):
            item = inputs[i]
            raw_str = f.text[item[0]:item[1]]
            raw_str = raw_str.replace("<br />", "\n").replace("<pre>", "")
            raw_str = re.sub(r"<div class=.*?>", "", raw_str)
            raw_str = re.sub(r"</div>", "\n", raw_str).strip()
            print("Parsing input {0}{1}{2}".format(bcolors.BOLD, current_input_num, bcolors.ENDC))
            print("=================================")
            print("{0}{1}{2}".format(bcolors.OKBLUE, raw_str, bcolors.ENDC))
            print("=================================")
            make_file(f"{path}{current_input_num}.in", raw_str)
            current_input_num += 1

            item = outputs[i]
            raw_str = f.text[item[0]:item[1]]
            raw_str = raw_str.replace("<br />", "\n").replace("<pre>", "")
            raw_str = re.sub(r"<div class=.*?>", "", raw_str)
            raw_str = re.sub(r"</div>", "\n", raw_str).strip()
            print("Parsing output {0}{1}{2}".format(bcolors.BOLD, current_output_num, bcolors.ENDC))
            print("=================================")
            print("{0}{1}{2}".format(bcolors.OKBLUE, raw_str, bcolors.ENDC))
            print("=================================")
            make_file(f"{path}{current_output_num}.out", raw_str)
            current_output_num += 1
    except Exception as e:
        print(e)


def parse_contest(ID):
    LINK = f"https://codeforces.com/contest/{ID}"
    scraper = cloudscraper.create_scraper()
    f = scraper.get(LINK)
    search_link = f"/contest/{ID}/problem/"
    all_starts = [m.start() for m in re.finditer(search_link, f.text)]
    problems = []
    for item in all_starts:
        cur_prob = ""
        cur_add = 0
        while f.text[item+len(search_link)+cur_add] != '"':
            cur_prob += f.text[item+len(search_link)+cur_add]
            cur_add += 1
        if len(problems) == 0 or problems[-1] != cur_prob:
            problems.append(cur_prob)
    for problem in problems:
        make_directory(problem)
    for problem in problems:
        problem_link = f"https://codeforces.com/contest/{ID}/problem/{problem}"
        print("{0}Parsing problem {1}{2}{3}".format(bcolors.HEADER, bcolors.BOLD, problem, bcolors.ENDC))
        make_file(f'{problem}/{problem.lower()}.cpp', '')
        parse_problem(problem_link, f"{problem}/")
    print("{0}Finished parsing contest{1}".format(bcolors.OKGREEN, bcolors.ENDC))


if __name__ == "__main__":
    parse_type = sys.argv[1].lower()
    if parse_type in ['o', 'p', '1']:
        parse_problem(sys.argv[2])
    elif parse_type == 'c':
        parse_contest(sys.argv[2])
