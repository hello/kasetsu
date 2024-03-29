
#include "pn.h"
#include "upconvert.h"
#include <sndfile.hh>
#include <string.h>
#include <iostream>

#define NUM_PN_PERIODS   (500/16)
#define SAMPLE_RATE (16000)
static void create_file (const char * fname,const int16_t * buffer, const uint32_t buflen) {
    
    SndfileHandle file ;
    const static int channels = 1 ;
    const static int srate = SAMPLE_RATE ;
    
    printf ("Creating file named '%s'\n", fname) ;
    
    file = SndfileHandle (fname, SFM_WRITE, SF_FORMAT_WAV | SF_FORMAT_PCM_16, channels, srate) ;
    
    file.write (buffer, buflen) ;
    
    /*
     **	The SndfileHandle object will automatically close the file and
     **	release all allocated memory when the object goes out of scope.
     **	This is the Resource Acquisition Is Initailization idom.
     **	See : http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization
     */
}

int main(int argc, char * argv[]) {
    
    uint32_t i;
    
    pn_init_with_mask_14();

    const uint32_t len = pn_get_length();
    std::cout << "len is " << len << " which will be about " << (len / (float)SAMPLE_RATE) << " seconds" << std::endl;
    
    //malloc
    uint8_t bits[NUM_PN_PERIODS * len];
    int16_t samplebuf[NUM_PN_PERIODS * len];
    
    
    for (i = 0; i < NUM_PN_PERIODS * len; i++) {
        bits[i] = pn_get_next_bit();
    
        if (bits[i] > 0) {
            samplebuf[i] = 1024;
        }
        else {
            samplebuf[i] = -1024;
        }
    
    }
    
    
    create_file("reference.wav",samplebuf,len);
    create_file("white.wav",samplebuf,NUM_PN_PERIODS * len);
    
    
    return 0;
}
