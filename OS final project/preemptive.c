#include <8051.h>
#include "preemptive.h"

 __data __at (0x30) char savedSP[4];
 __data __at (0x34) char bitmap;
 __data __at (0x35) char new_tid; //thread 0/1/2/3
 __data __at (0x36) char tmp_sp;
//__data __at (0x37) char cur_tid; //thread 0/1/2/3
//__data __at (0x38) char next_tid; (cur=3 next=8)

#define SAVESTATE \
        {\
        __asm \
            push ACC\
            push B\
            push DPL\
            push DPH\
            push PSW\
        __endasm; \
        savedSP[cur_tid] = SP;\
        }\

#define RESTORESTATE \
        {\
        SP = savedSP[cur_tid];\
        __asm \
            POP PSW\
            POP DPH\
            POP DPL\
            POP B\
            POP ACC\
        __endasm; \
        }\

extern void main(void);

void Bootstrap(void) {
  bitmap = 0;
  TMOD = 0;
  IE = 0x82;
  TR0 = 1;
  cur_tid = ThreadCreate(main);
  RESTORESTATE;
}

ThreadID ThreadCreate(FunctionPtr fp) {
  EA = 0;
  if(bitmap == 15)  return -1;

  if(bitmap == 0) {
    bitmap = 1;
    new_tid = 0;
  }
  else if(bitmap == 1) {
    bitmap = 3;
    new_tid = 1;
  }
  else if(bitmap == 3) {
    bitmap = 7;
    new_tid = 2;
  }
  else if(bitmap == 7) {
    bitmap == 15;
    new_tid = 3;
  }

  tmp_sp = SP;
  SP = (0x3F) + (0x10) * new_tid;

  __asm
    PUSH DPL
    PUSH DPH
  __endasm;

  __asm
    MOV A, #0
    PUSH ACC
    PUSH ACC
    PUSH ACC
    PUSH ACC
  __endasm;

  PSW = new_tid << 3;
  __asm
    PUSH PSW
  __endasm;

  savedSP[new_tid] = SP;

  SP = tmp_sp;

  EA = 1;
  return new_tid;
}

void ThreadYield(void) {
  EA = 0;
  SAVESTATE;
  do {
    if(cur_tid < 3){
      cur_tid++;
    }else{
      cur_tid = 0;
    }
    if(bitmap & (1 << cur_tid)){
        break;
    }
  }while(1);
  RESTORESTATE;
  EA = 1;
}

void ThreadExit(void) {
  EA = 0;
  if(cur_tid == 0) bitmap = bitmap - 1;
  else if(cur_tid == 1)  bitmap = bitmap - 2;
  else if(cur_tid == 2)  bitmap = bitmap - 4;
  else if(cur_tid == 3)  bitmap = bitmap - 8;

  if(bitmap & 1){ //if there's another thread available
      cur_tid = 0;//set its id
  }
  else if(bitmap & 2){
      cur_tid = 1;
  }
  else if(bitmap & 4){
      cur_tid = 2;
  }
  else if(bitmap & 8){
      cur_tid = 3;
  }
  else{
      while(1){}
  }
  RESTORESTATE;
  EA = 1;
}

void myTimer0Handler(){
  EA = 0;
  SAVESTATE;
  __asm
      MOV A, R0
      PUSH ACC
      MOV A, R1
      PUSH ACC
      MOV A, R2
      PUSH ACC
      MOV A, R3
      PUSH ACC
      MOV A, R4
      PUSH ACC
      MOV A, R5
      PUSH ACC
      MOV A, R6
      PUSH ACC
      MOV A, R7
      PUSH ACC
  __endasm;

  time_unit = time_unit + 1;
  if(time_unit == 8){
    time_unit = 0;
    time = time + 1;
  }

  do{ //find a currently available thread 
    if(cur_tid < 3 ){
        cur_tid++;
    }else{
        cur_tid = 0;
    }

    if( cur_tid == 0 && (bitmap & 1))break;
    else if( cur_tid == 1 && (bitmap & 2))break;
    else if( cur_tid == 2 && (bitmap & 4))break;
    else if( cur_tid == 3 && (bitmap & 8))break;

  } while (1);

  __asm
      POP ACC
      MOV R7, A
      POP ACC
      MOV R6, A
      POP ACC
      MOV R5, A
      POP ACC
      MOV R4, A
      POP ACC
      MOV R3, A
      POP ACC
      MOV R2, A
      POP ACC
      MOV R1, A
      POP ACC
      MOV R0, A
  __endasm;
  RESTORESTATE;
  EA = 1;
  __asm
      RETI
  __endasm;
}

unsigned char now(void){
    return time;
}