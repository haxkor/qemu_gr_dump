from subprocess import check_output, run, PIPE

T_start, T_end, T_step = 2, 200, 10
V_start, V_end, V_step = 1, 10, 1
samplesize = 20

#thread_count_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] # ,16,32,64]
thread_count_list = [1,2,4,8,16]
var_count_list = [1,2,4]



codefile = "bm.c"
with open(codefile, "r") as f:
    code = f.read()

results_csv = "results.csv"
with open(results_csv, "w") as f:
    f.write("mode,threads,vars,time")


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

def avg_cut_outliers(samples,trim=4):
    return avg(sorted(samples)[trim:-trim])

def dump_csv(mode, t, v, samples):
    with open(results_csv, "a") as f:
        for sample in samples:
            tup = (mode, t, v, sample)
            f.write("%s;%d;%d;%f\n" % tup)

def make_var_list(t):
    result = list()
    while t>0:
        result.append(t)
        t//=2

    return result
    

for thread_count in thread_count_list:
    for var_count in make_var_list(thread_count):
        print()
        for mode in ["native", "cas", "helper_cas"]:
            exe = gen_exec(thread_count, var_count, mode)
            samples = [measure_time(exe,mode) for _ in range(samplesize)]

            dump_csv(mode, thread_count, var_count, samples)
            #results_dict[(mode, thread_count, var_count)] = result

            print("threads= %d, vars= %d, mode=%s === %f" % (thread_count, var_count, mode, avg_cut_outliers(samples)))
            

