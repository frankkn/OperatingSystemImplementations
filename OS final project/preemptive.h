#ifndef __PREEMPTIVE_H__
#define __PREEMPTIVE_H__

__data __at (0x37) char cur_tid;
__data __at (0x38) unsigned char time;
__data __at (0x39) unsigned char time_unit;
__data __at (0x3A) unsigned char time_after_offset[4]; // for thread 0~3

#define delay(n)\
  time_after_offset[cur_tid] = time + n;\
  while(time_after_offset[cur_tid] != time){}\

#define MAXTHREADS 4

#define CNAME(s) _ ## s

#define SemaphoreCreate(s, n)\
            s = n\
            
#define SemaphoreWaitBody(s, label)\
    { __asm \
        label:\
        MOV A, CNAME(s)\
        JZ  label\
        JB ACC.7, label\
        dec  CNAME(s) \
      __endasm; }

#define SemaphoreSignal(s)\
        __asm \
          INC CNAME(s)\
        __endasm;\


typedef char ThreadID;
typedef void (*FunctionPtr)(void);

ThreadID ThreadCreate(FunctionPtr);
void ThreadYield(void);
void ThreadExit(void);
void myTimer0Handler();

#endif // __PREEMPTIVE_H__
