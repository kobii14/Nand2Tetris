// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
	@R6
	M=0
	@R8
	M=0
	@R14
	A=M
	D=M
	@R5
	M=D
	@R7
	M=D
	@i
	M=0
(LOOP)
	@R15
	D=M
	@i
	D=D-M
	@END
	D;JEQ
//if smaller than minimum
	@R14
	D=M
	@i
	A=D+M
	D=M
	@R5
	D=M-D
	@MINI
	D;JGT
(RETMINI)
//if bigger than maximum
	@R14
	D=M
	@i
	A=D+M
	D=M
	@R7
	D=M-D
	@MAXI
	D;JLT
(RETMAXI)

//continue
	@i
	M=M+1
	@LOOP
	0;JMP

(MINI)
	@i
	D=M
	@R6
	M=D
	@R14
	D=M
	@i
	A=D+M
	D=M
	@R5
	M=D
	@RETMINI
	0;JMP

(MAXI)
	@i
	D=M
	@R8
	M=D
	@R14
	D=M
	@i
	A=D+M
	D=M
	@R7
	M=D
	@RETMAXI
	0;JMP
(END)

	@R14
	D=M
	@R6
	A=D+M
	D=A
	@new
	M=D
	@R7
	D=M
	@new
	A=M
	M=D

	
	

	
	@R14
	D=M
	@R8
	A=D+M
	D=A
	@neww
	M=D
	@R5
	D=M
	@neww
	A=M
	M=D
(ENDD)
	@ENDD
	0;JMP
	
	














