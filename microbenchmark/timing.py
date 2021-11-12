from subprocess import check_output, run, PIPE


codefile = "bm.c"
with open(codefile, "r") as f:
    code = f.read()


results_dict = dict()

def gen_exec(t, v, mode):
    if mode == "native":
        cc = "gcc"
    else:
        cc = "x86_64-linux-gnu-gcc-10"


    prefix = "#define NUM_THREADS %d\n#define NUM_VARS %d\n" % (t,v)
    name = "temp-bm-%d-%d-%s" % (t, v, cc[:3])
    namec = name + ".c"

    with open(namec, "w") as f:
        f.write(prefix + code)

    run("%s -pthread -static -o %s %s" % (cc, name, namec), shell=True, check=True)
    return name



def measure_time(exe, mode):
    if mode == "cas":
        pref = "qemu-x86_64_cas"
    elif mode == "helper_cas":
        pref = "qemu-x86_64_helper_cas"
    else: # native
        pref = ""

    cmd = "%s ./%s" % (pref, exe)
    out = check_output(cmd, shell=True)

    result = float(out)
    return result


def avg(samples):
    return sum(samples)/len(samples)

T_start, T_end, T_step = 2, 200, 10
V_start, V_end, V_step = 1, 10, 1
samplesize = 1

thread_count_list = [1,4,8,16,32,64]
var_count_list = [1,2,3,4,5]


for thread_count in thread_count_list:
    for var_count in var_count_list:
        for mode in ["native", "cas", "helper_cas"]:
            print("threads= %d, vars= %d, mode=%s" % (thread_count, var_count, mode))

            exe = gen_exec(thread_count, var_count, mode)
            samples = [measure_time(exe,mode) for _ in range(samplesize)]

            results_dict[(mode, thread_count, var_count)] = avg(samples)

            

