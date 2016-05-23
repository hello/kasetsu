#include <iostream>
#include <fstream>
#include <string.h>
#include <sstream>
#include <sndfile.hh>

#include "tinylstm_conv_layer.h"
#include "tinylstm_math.h"

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

void test_conv2d_really_basic() {
    Weight_t out[1];
    Weight_t w[4] = {TOFIX(0.9),TOFIX(0.8),TOFIX(0.7),TOFIX(0.6)};
    Weight_t image[4] = {TOFIX(-0.1),TOFIX(0.2),TOFIX(-0.3),TOFIX(0.4)};
    
    WeightLong_t temp = 0;
    for (int i = 0; i < 4; i++) {
        temp += w[i] * image[i];
    }
    
    temp += 1 << (QFIXEDPOINT - 1);
    temp>>= QFIXEDPOINT;
    
    tinylstm_convolve2d_direct(out, w, image, 2, 2, 2, 2);
    
    int diff = out[0] - temp;
    
    int foo = 3;
    foo++;
    
    
}

void test_conv2d_layer() {
    const static Weight_t weights[4] = {TOFIX(0.5),TOFIX(0.5),TOFIX(0.5),TOFIX(0.5)};
    const static ConstTensor_t weight_tensor = {&weights[0],{1,2,2}};
    const static ConvLayer2D_t layer_def = { &weight_tensor,{2,4,4},{2,3,3}};
    
    ConstLayer_t layer = tinylstm_create_conv_layer(&layer_def);

    const uint32_t dims[3] = {2,3,3};
    Tensor_t * t1 = tinylstm_create_new_tensor(dims);
    
    const uint32_t dims2[3] = {2,4,4};
    Tensor_t * t2 = tinylstm_create_new_tensor(dims2);
    
    for (uint32_t islice = 0; islice < 2; islice++) {
        Weight_t * p = get_slice(t2,islice);
        
        for (uint32_t j = 0; j < 4; j++) {
            for (uint32_t i = 0; i < 4; i++) {
                *(p + j*4 + i) = TOFIX(0.25);
            }
        }
    }

    layer.eval(layer.context,t2,t1);
    
    t1->delete_me(t1);
    t2->delete_me(t2);
    
}



int main(int argc, char * argv[]) {
    test_conv2d_really_basic();
    test_conv2d_layer();

    /*
    const std::string inFile = argv[1];
    
    memset(_buf,0,sizeof(_buf));
    memset(_outbuf,0,sizeof(_outbuf));

    
    read_file(inFile);
     */


    
    return 0;
}
