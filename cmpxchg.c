#include <pthread.h>
int a=1;
//int expected = 1;
//int desired = 3;
//int * where = &a;


void * fun(void * arg){
    int r=__atomic_compare_exchange_4(&a, &a, 1, 1, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
}

    


int main(){

    pthread_t thread_id[2];

    pthread_create(&thread_id[0], NULL, fun, NULL);
    pthread_create(&thread_id[1], NULL, fun, NULL);

    void* status;
    pthread_join(thread_id[0], &status);
    pthread_join(thread_id[1], &status);
    
}
