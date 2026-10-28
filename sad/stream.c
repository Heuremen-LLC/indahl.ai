// CPU memory bandwidth, STREAM triad a[i]=b[i]+s*c[i], pthreads. Usage: ./stream THREADS GIB_PER_ARRAY REPS
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <string.h>
typedef struct {double *a,*b,*c; size_t lo,hi;} W;
#include <stdatomic.h>
static atomic_int bcount, bsense;
static void barrier(int n){ static _Thread_local int local=0; local=!local; if(atomic_fetch_add(&bcount,1)==n-1){ atomic_store(&bcount,0); atomic_store(&bsense,local);} else { while(atomic_load(&bsense)!=local){} } }
static int nt,reps; static double *times;
static void* run(void* p){ W* w=(W*)p; double s=3.0;
  for(size_t i=w->lo;i<w->hi;i++){ w->a[i]=1.0; w->b[i]=2.0; w->c[i]=0.5; }
  for(int r=0;r<reps;r++){ barrier(nt); struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
    for(size_t i=w->lo;i<w->hi;i++) w->a[i]=w->b[i]+s*w->c[i];
    barrier(nt); clock_gettime(CLOCK_MONOTONIC,&t1);
    if(w->lo==0) times[r]=(t1.tv_sec-t0.tv_sec)+(t1.tv_nsec-t0.tv_nsec)*1e-9; }
  return 0; }
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
int main(int argc,char**argv){ nt=atoi(argv[1]); double gib=atof(argv[2]); reps=atoi(argv[3]);
  size_t n=(size_t)(gib*1073741824.0/8); n-=n%nt; double *a=malloc(n*8),*b=malloc(n*8),*c=malloc(n*8); times=calloc(reps,sizeof(double));
  pthread_t th[64]; W w[64];
  for(int t=0;t<nt;t++){ w[t]=(W){a,b,c,n/nt*t,n/nt*(t+1)}; pthread_create(&th[t],0,run,&w[t]); }
  for(int t=0;t<nt;t++) pthread_join(th[t],0);
  double bytes=24.0*n; double*s=malloc(reps*8); memcpy(s,times,reps*8); qsort(s,reps,8,cmp);
  printf("{\"kind\":\"cpu_triad\",\"threads\":%d,\"gib_per_array\":%.2f,\"reps\":%d,\"best_gbs\":%.1f,\"median_gbs\":%.1f,\"worst_gbs\":%.1f}\n",nt,gib,reps,bytes/s[0]/1e9,bytes/s[reps/2]/1e9,bytes/s[reps-1]/1e9);
  return a[n/2]==3.5?0:1; }
