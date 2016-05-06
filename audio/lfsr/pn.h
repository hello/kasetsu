
#ifndef _LFSR_H_
#define _LFSR_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int32_t pn_correlate_with_xor(const uint16_t * v1, const uint16_t * v2, uint32_t len);
uint8_t pn_get_next_bit();
void pn_init_with_state(uint16_t init_state);
void pn_init(void);

#ifdef __cplusplus
}
#endif
    
#endif