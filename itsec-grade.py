#!/usr/bin/env python3

import threading
import subprocess
import re
import os
import time
import logging
from sys import argv


if len(argv) != 5:
    print("usage:\nitsec-grade %task %max_score %corrector %default_comment")
    os._exit(0)     # clean exit without raising SystemExit
else:
    task = int(argv[1])
    max_score = float(argv[2])
    corrector = argv[3]
    default_comment = argv[4]

# configure this if you like
path_pref = "submissions/%d/" % task
num_threads = 4

# any submission i couldnt deal with is noted here
unhandled_path = "unhandled_submissions.txt"

# dont change stuff below here
logging.basicConfig()
log = logging.getLogger()
log.setLevel("WARNING")

max_team = 150
flag_len = 42  # funny number

white = '\033[0m'
red = '\033[31m'
green = '\033[32m'
orange = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'

COLOR_NORMAL = white
COLOR_KEYWORD = orange
COLOR_COMMENT = blue


def make_alreadygraded(task):
    with open("grading.csv", "r") as f:
        for line in f.readlines()[1:]:
            splitted = line.split(";")
            cur_task, cur_team = int(splitted[0]), int(splitted[1])

            if cur_task != task:
                continue

            already_graded.append(cur_team)


already_graded = list()
make_alreadygraded(task)

working_dict = dict()


class ExploitChecker(threading.Thread):
    def __init__(self, exploits, working_dict):
        threading.Thread.__init__(self)
        self.exploits = exploits
        self.dict = working_dict

    def run(self):
        # print(self.exploits)
        for exp in self.exploits:
            self.dict[exp] = isWorking(exp)


def schedule_checkers(exploits):
    exp_lists = dict([(i, list()) for i in range(num_threads)])

    # partition exploits
    for i, exp in enumerate(exploits):
        exp_lists[i % num_threads].append(exp)

    # start threads
    for l in exp_lists.values():
        t = ExploitChecker(l, working_dict)
        t.start()

    log.debug("started all threads")


def getWorking(exp):
    printed_waiting = False
    while working_dict.setdefault(exp) is None:
        if not printed_waiting:
            printed_waiting = True
            print("still checking exploit...")
        time.sleep(2)

    working, errpath = working_dict[exp]

    if not working:
        print("%s returned non-zero exit code. STDERR:" % exp)
        with open(errpath, "r") as f:
            print(red + f.read() + COLOR_NORMAL)
    elif working == 1:
        print("exploit does not crash, but flag does not seem valid")
    elif working == 2:
        print(green + "valid flag!" + COLOR_NORMAL)

    return working


def extract_team(exp):
    # yep this is trash design, but
    _, _, exp = exp.partition("team-")
    return int(exp.split("/")[0])


def pretty_print(exp):
    total = ""
    with open(exp, "r") as f:
        for line in f.readlines():
            code, hashtag, comment = line.partition("#")

            code = multiple_replace(keywords_dict, code)
            if hashtag:
                code += COLOR_COMMENT + hashtag + comment + COLOR_NORMAL

            total += code

    print(total)


def multiple_replace(keywords_dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, keywords_dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: keywords_dict[mo.string[mo.start():mo.end()]], text)


keywords = ["in", "def", "for", "while", "return",
            "import", "with", "as", "if", "else"]
keywords = ["%s " % k for k in keywords]  # add spaces
keywords += ["else:", "return"]
keywords_dict = dict((k, COLOR_KEYWORD + k + COLOR_NORMAL) for k in keywords)


def isWorking(exp):
    arg = "python3 " + exp
    try:
        # gotta make sure the errfile is listed before the submissions
        errpath = exp.replace("task", "err")
        with open(errpath, "w") as errf:
            out = subprocess.check_output(arg, shell=True, stderr=errf)
    except subprocess.CalledProcessError:
        with open(errpath, "r") as errf:
            # if we do Ctrl-C while grading, a KeyboardInterrupt might be send to one of the checking threads
            # not a very sexy way to do it
            if "KeyboardInterrupt" in errf.read():
                return isWorking(exp)

        return (0, errpath)

    i = out.find(b"flag{")
    flag = out[i: i+flag_len]

    if isValid(flag):
        return (2, 0)  # 2 if valid flag, 1 if runs but no valid flag
    else:
        return (1, 0)


def isValid(flag):
    return True     # TODO


def grade(task, team):
    while True:
        score = False
        comment = False
        try:
            score = input("score: ")
            try:
                score = float(score)
                if not 0 <= score <= max_score:
                    raise ValueError
            except ValueError:
                print("not a valid float withing score range 0 - %f" % max_score)
                continue

            comment = input("comment: ")
            if not comment:
                comment = default_comment

            internal_comment = input("internal comment: ")
            break

        except KeyboardInterrupt:
            if score is False:
                print("skipping")
                time.sleep(0.4)
                return
            else:
                print("restarting")
                continue

    with open("grading.csv", "a") as f:
        tup = (task, team, score, comment, internal_comment, corrector)
        f.write("%d;%d;%f;%s;%s;%s\n" % tup)


def getNewestSubmission(subdir):
    # TODO check if it was submitted after deadline?
    arg = "ls " + subdir
    out = subprocess.check_output(arg, shell=True)
    return subdir + out.splitlines()[-1].decode()


def handle_other_filetype(submission):
    """return path of recovered .py file if possible, else None"""
    if submission.endswith(".zip"):
        # TODO
        # check for zip bomb
        # unpack
        # return task.py path
        pass

    with open(unhandled_path, "a") as f:
        f.write(submission + "\n")


def getExploits():
    result = list()
    with open(unhandled_path, "w") as f:
        pass

    for cur_team in range(max_team):
        if cur_team in already_graded:
            log.debug("Team %d is already graded" % cur_team)
            continue

        subdir = path_pref + "team-%d/" % cur_team
        if not os.path.exists(subdir):
            log.debug("Team %d did not submit" % cur_team)
            continue

        exp = getNewestSubmission(subdir)
        if not exp.endswith(".py"):
            log.debug("newest submission of Team %d is not a .py file" % cur_team)
            recovered_exp = handle_other_filetype(exp)  # TODO
            if not recovered_exp:
                continue

        log.debug("found .py submission for Team %d" % cur_team)
        result.append(exp)

    return result


def main():
    exploits = getExploits()
    schedule_checkers(exploits)

    for exp in exploits:
        team = extract_team(exp)
        print("\n\n++++ Team %d ++++" % team)
        pretty_print(exp)
        working = getWorking(exp)

        grade(task, team)


if __name__ == "__main__":
    main()
