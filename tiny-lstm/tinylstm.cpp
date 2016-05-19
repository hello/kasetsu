#include <iostream>
#include <fstream>
#include <string.h>
#include <sstream>
#include <sndfile.hh>

using namespace std;

#define BUF_SIZE (1 << 24)

static uint8_t _buf[BUF_SIZE];
static uint8_t _outbuf[4*BUF_SIZE];


static void read_file (const std::string & fname) {
   

    SndfileHandle file ;
    
    file = SndfileHandle (fname) ;
    
    printf ("Opened file '%s'\n", fname.c_str()) ;
    printf ("    Sample rate : %d\n", file.samplerate ()) ;
    printf ("    Channels    : %d\n", file.channels ()) ;
    
    
/*    
    int16_t buf[AUDIO_FFT_SIZE * file.channels()];
    int16_t monobuf[AUDIO_FFT_SIZE];
    while (true) {
    int count = file.read(buf, AUDIO_FFT_SIZE * file.channels());
        if (count <= 0) {
            break;
        }
        
        memset(monobuf,0,sizeof(monobuf));
        
        for (int i = 0; i < AUDIO_FFT_SIZE; i ++) {
            monobuf[i] = buf[file.channels() * i];
        }
        
        AudioFeatures_SetAudioData(monobuf, AUDIO_FFT_SIZE);
    }
*/
}





int main(int argc, char * argv[]) {
    const std::string inFile = argv[1];
    
    memset(_buf,0,sizeof(_buf));
    memset(_outbuf,0,sizeof(_outbuf));

    
    read_file(inFile);


    
    return 0;
}
