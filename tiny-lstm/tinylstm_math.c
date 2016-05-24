#include "tinylstm_math.h"

const static int8_t tanh_table[356] = {0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,36,37,38,39,40,41,42,43,44,44,45,46,47,48,49,50,51,51,52,53,54,55,55,56,57,58,59,59,60,61,62,63,63,64,65,65,66,67,68,68,69,70,70,71,72,73,73,74,75,75,76,76,77,78,78,79,80,80,81,81,82,83,83,84,84,85,85,86,86,87,88,88,89,89,90,90,91,91,92,92,93,93,93,94,94,95,95,96,96,97,97,97,98,98,99,99,99,100,100,101,101,101,102,102,102,103,103,103,104,104,104,105,105,105,106,106,106,107,107,107,108,108,108,108,109,109,109,109,110,110,110,110,111,111,111,111,112,112,112,112,113,113,113,113,113,114,114,114,114,114,115,115,115,115,115,116,116,116,116,116,116,117,117,117,117,117,117,118,118,118,118,118,118,118,119,119,119,119,119,119,119,119,120,120,120,120,120,120,120,120,120,121,121,121,121,121,121,121,121,121,121,122,122,122,122,122,122,122,122,122,122,122,122,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,124,124,124,124,124,124,124,124,124,124,124,124,124,124,124,124,124,124,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,125,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,126,127};


Weight_t tinymath_abs(Weight_t x) {
    if (((uint8_t)x) == 0x80) {
        //deal with case if x = -128
        x++;
    }

    return x >= 0 ? x : -x;
}

Weight_t tinylstm_tanh(WeightLong_t x) {
    const static uint32_t k_max_len = sizeof(tanh_table) / sizeof(tanh_table[0]);

    const uint8_t sign = x < 0;
    Weight_t y = 0x7F;
    x = tinymath_abs(x);
    
    if (x < k_max_len) {
        y = tanh_table[x];
    }


    if (sign) {
        return -y;
    }

    return y;
}

void tinylstm_vec_tanh(Weight_t * out, const WeightLong_t * in, const uint32_t num_elements) {
    uint32_t i;
    
    for (i = 0; i < num_elements; i++) {
        out[i] = tinylstm_tanh(in[i]);
    }
}

void tinylstm_matmulvec_long_output(WeightLong_t * out,const Weight_t * mat, const Weight_t * vec, const uint32_t num_rows, const uint32_t num_cols) {
    
    WeightLong_t * pOut = out;
    const Weight_t * pRow = mat;
    WeightLong_t temp;
    uint32_t j,i;
    
    for (j = 0; j < num_rows; j++) {
        temp = 0;
        for (i = 0; i < num_cols; i++) {
            temp += vec[i] * pRow[i];
        }
        *pOut = temp;
        
        pRow += num_cols;
        pOut++;
    }
    
}


//takes two 3 dimensional tensors (a bunch of images, and a bunch of convolutional filters),
//applies them accross each of the innermost tensor dimension (i.e. A1 x B1 x C1, A2 x B2 x C2, we're talking about A1 and A2, and A1 == A2)
void tinylstm_convolve3d_direct(Weight_t * out, const Weight_t * weights,const Weight_t * image, const Weight_t bias,const uint32_t num_weights_rows,const uint32_t num_weights_cols, const uint32_t num_image_rows, const uint32_t num_image_cols, const uint32_t num_images) {
    
    
    const uint32_t num_rows_out = num_image_rows - num_weights_rows + 1;
    const uint32_t num_cols_out = num_image_cols - num_weights_cols + 1;
    const uint32_t weight_size = num_weights_rows * num_weights_cols;
    const uint32_t image_size = num_image_rows * num_image_cols;
    
    uint32_t ioutrow,ioutcol;
    uint32_t iimage;
    uint32_t j,i;
    
    Weight_t * out_row = out;
    
    for (ioutrow = 0; ioutrow < num_rows_out; ioutrow++) {
        for (ioutcol = 0; ioutcol < num_cols_out; ioutcol++) {
            
            WeightLong_t accumulator = 0;
            const Weight_t * weight_start = weights;
            const Weight_t * image_start = image +  (ioutrow * num_image_cols) + ioutcol;
            
            for (iimage = 0; iimage < num_images; iimage++) {
                
                //element by element multiply of one matrix against another (NOT THIS IS NOT A MATRIX MULTIPLY)
                //summing as you go.
                
                const Weight_t * image_row = image_start;
                const Weight_t * weight_row = weight_start;

                for (j = 0; j < num_weights_rows; j++) {
                    
                    // ***** TODO optimize this right here *****
                    for (i = 0; i < num_weights_cols; i++) {
                        accumulator += image_row[i] * weight_row[i];
                    }
                    
                    weight_row += num_weights_cols;
                    image_row += num_image_cols;
                }
                
                //traverse to next slice for weights and image
                weight_start += weight_size;
                image_start += image_size;
            }
            
            //round
            accumulator += (1 << (QFIXEDPOINT - 1));
            accumulator >>= QFIXEDPOINT;
            
            //add bias
            accumulator += bias;
            
            //saturate
            if (accumulator > MAX_WEIGHT) {
                accumulator = MAX_WEIGHT;
            }
            
            if (accumulator < -MAX_WEIGHT) {
                accumulator = -MAX_WEIGHT;
            }
            
            out_row[ioutcol] = (Weight_t) accumulator;
            
        }
        
        out_row += num_cols_out;
    }
}


