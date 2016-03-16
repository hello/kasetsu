
#include "pn.h"
#include "upconvert.h"
#include <sndfile.hh>
#include <string.h>

#define NUM_PN_PERIODS   (10)
#define PN_LEN           ((1<<9) - 1)
#define LEN ((NUM_PN_PERIODS) * (PN_LEN))
#define SAMPLE_BUF_SIZE (LEN * 11)

static void create_file (const char * fname,const int16_t * buffer, const uint32_t buflen) {
    
    SndfileHandle file ;
    const static int channels = 1 ;
    const static int srate = 48000 ;
    
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
    
    uint8_t bits[LEN];
    uint32_t i;
    uint32_t num_samples_written;
    int16_t samplebuf[SAMPLE_BUF_SIZE];

    pn_init();

    for (i = 0; i < LEN; i++) {
        bits[i] = pn_get_next_bit();
    }
    
    num_samples_written = upconvert_bits_bpsk(samplebuf, bits, LEN, SAMPLE_BUF_SIZE);
    
    
    create_file("test.wav",samplebuf,num_samples_written);
    
    
    return 0;
}