
#include "pn.h"
#include <string.h>

#include <fstream>
#include <iterator>
#include <vector>
#include <iostream>
#include <stdint.h>
#include <sstream>

int main(int argc, char * argv[]) {
    
    if (argc < 2) {
        std::cout << "NEED TO SPECIFY AN INPUT FILE" << std::endl;
        return 0;
    }
    
    
    std::ifstream input(argv[1], std::ios::binary );
    // copies all data into buffer
    std::vector<char> buffer((std::istreambuf_iterator<char>(input)),(std::istreambuf_iterator<char>()));
    std::vector<int16_t> vec2;
    vec2.reserve(1<<20);
    
    
    for (int j =0; j < 512; j++) {
        int count = 0;

        pn_init_with_mask_12();
        
        uint8_t the_byte = 0x00;
        
        int16_t sums[4][8];
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
       
        /*
        for (int i = 0; i < 8; i++) {
            if (i != 0) std::cout << ",";
            vec2.push_back(sums[0][i]);
            std::cout << sums[0][i];
        }
        
        std::cout << std::endl;
        */
        for (int i = 7; i >= 0; i--) {
            vec2.push_back(sums[3][i]);
        }
         
        

    }
    
    std::ostringstream oss;
    
    if (!vec2.empty())
    {
        // Convert all but the last element to avoid a trailing ","
        std::copy(vec2.begin(), vec2.end()-1,
                  std::ostream_iterator<int>(oss, "\n"));
        
        // Now add the last element with no delimiter
        oss << vec2.back();
    

    }
    
    std::cout << oss.str() << std::endl;

    return 0;
}
