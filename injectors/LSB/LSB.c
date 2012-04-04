#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int *LSBsteps;
int LSBstepsize = 0;

/**********************************************************
* Set positions where to steganograph message into medium *
**********************************************************/

void initializeSteps(int *steps, int stepsize) {
  
  LSBsteps = (int *) malloc(stepsize*sizeof(int));
  memcpy (LSBsteps,steps,stepsize*sizeof(int));
  
  LSBstepsize = stepsize;
  
}



/**********************************************************
*   Recover message hidden in medium Less Significant Bits   *
**********************************************************/
  
void RecoverBits(unsigned char *message, unsigned char *medium, int messagesize, int mediumsize, int bitperbyte) {
  
    
    
  // Check size, position array, bitperbyte quantity.
  if( messagesize > mediumsize/(8/bitperbyte) || LSBstepsize < messagesize*(8/bitperbyte) || (bitperbyte != 1 && bitperbyte != 2 && bitperbyte != 4 && bitperbyte != 8 ) ) {
      printf("[ERR] RecoverBits error: messagesize: %d, mediumsize: %d, bitperbyte: %d, lsbstepsize: %d\n", messagesize, mediumsize, bitperbyte, LSBstepsize);
  } 
  
  
  else {
      
        long int messageindex = 0;
        long int mediumindex = 0;
        
        
        // Iterate byte length of Message to recover from Stego-Medium
        for (messageindex = 0; messageindex < messagesize; messageindex++) {
            
                unsigned char mask = 0;
                int bitcount = 0;
                int stepindex = 0;
                
                // Recover 'bitperbyte' bit quantity in every position in Stego-Medium specified in LSBsteps
                for(; bitcount < 8 && mediumindex < mediumsize && stepindex < LSBstepsize; bitcount+=bitperbyte, mediumindex+=LSBsteps[stepindex], stepindex++, mask+=bitperbyte) {
//                        
                    // Recover 'bitperbyte' bits quantity in medium[medium]
                    unsigned char newbit = ~( ( ~0 ) << bitperbyte ) & medium[mediumindex];
                    
                    // Put newbits in masked byte position
                    message[messageindex] = (message[messageindex] & ~(1 << mask)) | (newbit << mask); 


                }	  
        }

  }
  
}

/**********************************************************
*    Steganograph message in medium Less Significant Bits    *
**********************************************************/

void ModifyBits(unsigned char *message, unsigned char *medium, unsigned int messagesize, unsigned int mediumsize, int bitperbyte) {
	  
	
        // Check size, position array, bitperbyte quantity.
        if( messagesize > mediumsize/(8/bitperbyte) || LSBstepsize < messagesize*(8/bitperbyte) || (bitperbyte != 1 && bitperbyte != 2 && bitperbyte != 4 && bitperbyte != 8 ) ) {
            printf("[ERR] ModifyBits error: messagesize: %d, mediumsize: %d, bitperbyte: %d, lsbstepsize: %d\n", messagesize, mediumsize, bitperbyte, LSBstepsize);
        } 
	else {
		int messageindex = 0, mediumindex = 0;
		unsigned char d;
		int stepindex=0;

                // Iterate byte of Message to steganograph
		for (; messageindex < messagesize; messageindex++) {
		      
		      d = message[messageindex];
		      
		      int bitcount = 0;
                      
                      // Insert 'bitperbyte' bit quantity in every Stego-Medium position specified in LSBsteps
		      for (; bitcount<8 && mediumindex < mediumsize && stepindex < LSBstepsize; bitcount+=bitperbyte, mediumindex+=LSBsteps[stepindex], stepindex++, d>>=bitperbyte) {
                          
                                // Insert 'bitperbyte' bits of byte d, in medium[medium]
                                medium[mediumindex] = ( d | medium[mediumindex] & ( ~0 << bitperbyte) );
 				
				
		      }
		
		}
	}
}


