
#include <8051.h>
#include "preemptive.h"

__data __at (0x3E) char empty;
__data __at (0x3F) char mutex;
__data __at (0x20) char car_name[4];//each car's name for each car thread  
__data __at (0x2A) char spot1;//parking spot 1
__data __at (0x2B) char spot2;//parking spot 2
__data __at (0x2C) char car_id;// car1 ~ car5
__data __at (0x2D) char car_tid;// 0/1/2 ,3 for main thread 
__data __at (0x2E) char next_car;
__data __at (0x2F) char i;

#define L(x) LABEL(x)
#define LABEL(x) x##$

#define print(car_no, movement)\
    TMOD |= 0x20;\
    TH1 = -6;\
    SCON = 0x50;\
    TR1 = 1;\
    for(i = 0; i < 4; i++){\
        if(i == 0)  SBUF = car_no;\
        else if(i == 1) SBUF = movement;\
        else if(i == 2) SBUF = (time & 7) +'0';\
        else if(i == 3) SBUF = '\n';\
        while(!TI){}\
        TI = 0;\
    }\

void Producer(void) {
    SemaphoreWaitBody(empty, L(__COUNTER__) );
    SemaphoreWaitBody(mutex, L(__COUNTER__) );
    EA = 0;
    if( spot1 == '0' ){
        spot1 = car_name[cur_tid];
        print(car_name[cur_tid],'i');
    }else if( spot2 == '0' ){
        spot2 = car_name[cur_tid];
        print(car_name[cur_tid],'i');
    }
    EA = 1;
    SemaphoreSignal(mutex);
    delay(1);
    
    EA = 0;
    if( spot1 == car_name[cur_tid] ){
        spot1 = '0';
        print(car_name[cur_tid], 'o');
    }else if( spot2 == car_name[cur_tid] ){
        spot2 = '0';
        print(car_name[cur_tid], 'o');
    }
    EA = 1;
    SemaphoreSignal(empty);
    SemaphoreSignal(next_car);
    ThreadExit();
}

void main(void) {
    SemaphoreCreate(mutex, 1);
    SemaphoreCreate(empty,2);
    SemaphoreCreate(next_car, 0);

    EA = 1;

    spot1 = '0';
    spot2 = '0';
    car_id = '1';
    
    car_tid = ThreadCreate(Producer);
    car_name[car_tid] = car_id;
    car_id = car_id + 1;

    car_tid = ThreadCreate(Producer);
    car_name[car_tid] = car_id;
    car_id = car_id + 1;

    car_tid = ThreadCreate(Producer);
    car_name[car_tid] = car_id;
    car_id = car_id + 1;
    while(time < 0xff){
        SemaphoreWaitBody(next_car, L(__COUNTER__) );
        car_tid = ThreadCreate(Producer);
        car_name[car_tid] = car_id;
        car_id = (car_id == '5') ? '1' : car_id + 1;
    }
    ThreadExit();

}

void _sdcc_gsinit_startup(void) {
        __asm
            ljmp  _Bootstrap
        __endasm;
}

void _mcs51_genRAMCLEAR(void) {}
void _mcs51_genXINIT(void) {}
void _mcs51_genXRAMCLEAR(void) {}
void timer0_ISR(void) __interrupt(1) {
        __asm
            ljmp _myTimer0Handler
        __endasm;
}
