#include <iostream>
#include <vector>
#include "pn.h"

#define MAG (1)

typedef std::vector<int16_t> Vec16_t;
typedef std::vector<int32_t> Vec32_t;
typedef std::vector<int64_t> Vec64_t;

static inline int64_t accumulate(const uint32_t n, const int16_t * in1, const int16_t * in2) {
    int64_t accumulator = 0;
    int16_t nloop = n;
    nloop = n;
    {
        int n = (nloop + 15) / 16;
        
        switch (nloop & 0x0F) {
            case 0: do { accumulator += *in1++ * *in2++;
            case 15:     accumulator += *in1++ * *in2++;
            case 14:     accumulator += *in1++ * *in2++;
            case 13:     accumulator += *in1++ * *in2++;
            case 12:     accumulator += *in1++ * *in2++;
            case 11:     accumulator += *in1++ * *in2++;
            case 10:     accumulator += *in1++ * *in2++;
            case 9:      accumulator += *in1++ * *in2++;
            case 8:      accumulator += *in1++ * *in2++;
            case 7:      accumulator += *in1++ * *in2++;
            case 6:      accumulator += *in1++ * *in2++;
            case 5:      accumulator += *in1++ * *in2++;
            case 4:      accumulator += *in1++ * *in2++;
            case 3:      accumulator += *in1++ * *in2++;
            case 2:      accumulator += *in1++ * *in2++;
            case 1:      accumulator += *in1++ * *in2++;
                
            } while (--n > 0);
        }
    }
    return accumulator;
    
}

void test() {
    uint32_t len = pn_get_length();
    Vec16_t vec;
    vec.reserve(2*len);
    
    Vec16_t pn;
    pn.reserve(len);
    
    
    for (int i = 0; i < 2*len; i++) {
        uint8_t pnbit = pn_get_next_bit();
        if (i < len) {
            pn.push_back(pnbit ? MAG : -MAG);
        }
        
        vec.push_back(pnbit ? MAG : -MAG);
    }
    
    Vec64_t res;
    res.reserve(len);
    for (int i = 0; i < len; i++) {
        int64_t y = accumulate(len, pn.data(), vec.data() + i);
        res.push_back(y);
    }
    
    int foo = 3;
    foo++;

}

int main(void) {
    
    pn_init_with_mask_9();
    
    test();
    
    return 0;
}