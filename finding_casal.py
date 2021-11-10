from sys import argv

filename = argv[1]

outname = "filtered_cmpxchgs"
next_lines_ctr = 0 

correct = []
incorrect = []

current = ""

def write(s):
    global current
    current += s

def is_correct(s):
    line0 = s.splitlines()[1]
    line1 = s.splitlines()[2]

    assert "casal" in line0 
    # assert "mov" in line1, line1

    line0 = line0[36:]
    line1 = line1[36:]

    cmpv = line0[1:3]

    return cmpv in line1[4:]

    


with open(outname, "w") as out:
    with open(filename, "r") as f:

        for line in f.readlines():
            if next_lines_ctr:
                write(line)
                next_lines_ctr -= 1

                if next_lines_ctr == 0:
                    write("\n\n")

                    if is_correct(current):
                        correct.append(current)
                    else:
                        incorrect.append(current)

                    current = ""

            if "lock cmpxch" in line:
                cmpxch = line

            if "casal" in line:
                write( cmpxch + line)
                next_lines_ctr = 3

    out.write("correct:\n")
    out.write("\n".join(l for l in correct))

    out.write("incorrect:\n")
    out.write("\n".join(l for l in incorrect))


