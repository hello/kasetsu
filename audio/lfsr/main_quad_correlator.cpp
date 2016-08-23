
#include "pn.h"
#include <string.h>

#include <fstream>
#include <iterator>
#include <vector>
#include <iostream>
#include <stdint.h>

int main(int argc, char * argv[]) {
    
    if (argc < 2) {
        std::cout << "NEED TO SPECIFY AN INPUT FILE" << std::endl;
        return 0;
    }
    
    
    std::ifstream input(argv[1], std::ios::binary );
    // copies all data into buffer
    std::vector<char> buffer((std::istreambuf_iterator<char>(input)),(std::istreambuf_iterator<char>()));
    
    for (int j =0; j < 512; j++) {
        int count = 0;

        pn_init_with_mask_12();
        
        uint8_t the_byte = 0x00;
        
        int32_t sums[8][4];
        memset(&sums[0][0],0,sizeof(sums));
        
        for (std::vector<char>::iterator it = buffer.begin() + j*4; it != buffer.end();) {
            uint32_t x;
            char * c =(char * ) &x;
            
            c[0] = *it++;
            c[1] = *it++;
            c[2] = *it++;
            c[3] = *it++;
            
            pn_correlate_4x(x,sums,&the_byte);
            
            count++;
            
            if (count >= 4096) {
                break;
            }
        }
        
        //std::cout << sums[0] << "," << sums[1] << "," << sums[2] << "," << sums[3] << std::endl;
        for (int i = 0; i < 8; i++) {
            if (i != 0) std::cout << ",";
            std::cout << sums[i][0];
        }
        std::cout << std::endl;

    }
    
    
    return 0;
}
