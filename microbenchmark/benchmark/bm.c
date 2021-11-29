#include <malloc.h>
#include <pthread.h>
#include <time.h>

/*
#define NUM_THREADS 8
#define NUM_VARS 1 //*/
#define ITERATIONS 1000000


int *vars[NUM_VARS];

struct Thread_arg {
    int * var;
    int id;
    long misses;
};

#define memcon __ATOMIC_SEQ_CST

void* fun(void * arg_passed){
    struct Thread_arg * arg=arg_passed;

    int id = arg->id;
    int * var = arg->var;
    int zero=0;
    long misses=0;

    //printf("pre loop\n");
    //try to write my id
    for (int i=0; i<ITERATIONS; i++){
        while(!__atomic_compare_exchange_4(var, &zero, id, 1, memcon, memcon)){
            misses++;
        };
        *var = 0;
        //printf("thread %d missed %ld times\n", id, misses);
    }
    //printf("post loop\n");

    arg->misses = misses;
}

struct Thread_arg args[NUM_THREADS];

int main(){
    int i;
    pthread_t thread_id[NUM_THREADS];

    //float start, taken;

    for (i=0; i<NUM_VARS; i++){
        vars[i]=(int*)calloc(0x1000, 1);
    }

    for (i=0; i<NUM_THREADS; i++){
        args[i].var = vars[i%NUM_VARS];
        args[i].id=i;
    }

    struct timespec start, end, diff;
    clock_gettime(CLOCK_REALTIME, &start);

    for (i=0; i<NUM_THREADS; i++){
        pthread_create(&thread_id[i], NULL, fun, &args[i]);
    }

    for (i=0; i<NUM_THREADS; i++){
        pthread_join(thread_id[i], NULL);
    }

    clock_gettime(CLOCK_REALTIME, &end);

    if ((end.tv_nsec-start.tv_nsec)<0) {
		diff.tv_sec = end.tv_sec-start.tv_sec-1;
		diff.tv_nsec = 1000000000+end.tv_nsec-start.tv_nsec;
	} else {
		diff.tv_sec = end.tv_sec-start.tv_sec;
		diff.tv_nsec = end.tv_nsec-start.tv_nsec;
	}

    printf("%d.%ld\n", diff.tv_sec, diff.tv_nsec);
}
