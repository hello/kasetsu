
#include "pn.h"
#include "upconvert.h"
#include <sndfile.hh>
#include <string.h>

#define NUM_PN_PERIODS   (100)

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
    
    uint32_t i;
    uint32_t num_samples_written;

    pn_init_with_mask_9();
    const uint32_t len = pn_get_length();
    
    //malloc
    uint32_t sample_buf_size = len * 24;
    uint8_t bits[len];
    int16_t samplebuf[sample_buf_size];

    
    for (i = 0; i < len; i++) {
        bits[i] = pn_get_next_bit();
    }
    
    num_samples_written = upconvert_bits_bpsk(samplebuf, bits, len * NUM_PN_PERIODS, sample_buf_size);
    
    
    create_file("test.wav",samplebuf,num_samples_written);
    
    
    return 0;
}
