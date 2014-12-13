

	.section	.rodata

	.section	.data
display_0: 
	.long 0
display_1: 
	.long 0

	.file	"native.c"
	.section	.rodata
.LC0:
	.string	"%d\n"
	.text
	.globl	print_int32
	.type	print_int32, @function
print_int32:
.LFB0:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	8(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC0, (%esp)
	call	printf
	movl	8(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE0:
	.size	print_int32, .-print_int32
	.section	.rodata
.LC1:
	.string	"%u\n"
	.text
	.globl	print_uint32
	.type	print_uint32, @function
print_uint32:
.LFB1:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	8(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC1, (%esp)
	call	printf
	movl	8(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE1:
	.size	print_uint32, .-print_uint32
	.section	.rodata
.LC2:
	.string	"%hhd\n"
	.text
	.globl	print_int8
	.type	print_int8, @function
print_int8:
.LFB2:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	8(%ebp), %eax
	movb	%al, -12(%ebp)
	movsbl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC2, (%esp)
	call	printf
	movzbl	-12(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE2:
	.size	print_int8, .-print_int8
	.section	.rodata
.LC3:
	.string	"%hhu\n"
	.text
	.globl	print_uint8
	.type	print_uint8, @function
print_uint8:
.LFB3:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	8(%ebp), %eax
	movb	%al, -12(%ebp)
	movzbl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC3, (%esp)
	call	printf
	movzbl	-12(%ebp), %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE3:
	.size	print_uint8, .-print_uint8
	.section	.rodata
.LC4:
	.string	"%g\n"
	.text
	.globl	print_float32
	.type	print_float32, @function
print_float32:
.LFB4:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	flds	8(%ebp)
	fstpl	4(%esp)
	movl	$.LC4, (%esp)
	call	printf
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE4:
	.size	print_float32, .-print_float32
	.section	.rodata
.LC6:
	.string	"%s"
	.text
	.globl	print
	.type	print, @function
print:
.LFB5:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	movl	8(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC6, (%esp)
	call	printf
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE5:
	.size	print, .-print
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits


	.section	.text

	.global	fn_0_f
	.type	fn_0_f	@function
fn_0_f:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
	movl	display_1, %ebx
	movl	%ebx, -4(%ebp)
	movl	%ebp, display_1
	movl	$0, -8(%ebp)	# R{0,1}:int32
	movl	$0, -12(%ebp)	# R{1,1}:int32


fn_0_f_b_0:

	# PRM  0:int32                         R{0,1}:int32
	#						-8(%ebp)
	movl	8(%ebp), %edi

	# MV   R{0,1}:int32                    R{1,1}:int32
	#	-8(%ebp)				-12(%ebp)
	movl	%edi, -12(%ebp)

	# RTRN R{1,1}:int32
	#	-12(%ebp)					
	movl	%edi, -8(%ebp)
	movl	-12(%ebp), %eax
	leave
	ret

	.global	main
	.type	main	@function
main:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$44, %esp
	movl	display_0, %ebx
	movl	%ebx, -4(%ebp)
	movl	%ebp, display_0
	movl	$0, -8(%ebp)	# R{0,0}:fn(int32)->unit
	movl	$0, -12(%ebp)	# R{1,0}:fn(uint32)->unit
	movl	$0, -16(%ebp)	# R{2,0}:fn(int8)->unit
	movl	$0, -20(%ebp)	# R{3,0}:fn(uint8)->unit
	movl	$0, -24(%ebp)	# R{4,0}:fn(float32)->unit
	movl	$0, -28(%ebp)	# R{5,0}:fn(string)->unit
	movl	$0, -32(%ebp)	# R{6,0}:fn(int32)->int32
	movl	$0, -36(%ebp)	# R{7,0}:int32
	movl	$0, -40(%ebp)	# R{8,0}:int32


main_b_0:

	# IMM  print_int32:label               R{0,0}:fn(int32)->unit
	#						-8(%ebp)
	leal	print_int32, %edi

	# IMM  print_uint32:label              R{1,0}:fn(uint32)->unit
	#						-12(%ebp)
	leal	print_uint32, %eax

	# IMM  print_int8:label                R{2,0}:fn(int8)->unit
	#						-16(%ebp)
	leal	print_int8, %ebx

	# IMM  print_uint8:label               R{3,0}:fn(uint8)->unit
	#						-20(%ebp)
	leal	print_uint8, %ecx

	# IMM  print_float32:label             R{4,0}:fn(float32)->unit
	#						-24(%ebp)
	leal	print_float32, %edx

	# IMM  print:label                     R{5,0}:fn(string)->unit
	#						-28(%ebp)
	leal	print, %esi

	# IMM  fn-0-f:label                    R{6,0}:fn(int32)->int32
	#						-32(%ebp)
	movl	%ecx, -20(%ebp)
	leal	fn_0_f, %ecx

	# IMM  1:int32                         R{8,0}:int32
	#						-40(%ebp)
	movl	%edi, -8(%ebp)
	movl	$1, %edi

	# CALL R{6,0}:fn(int32)->int32 (R{8,0}):(int32) R{7,0}:int32
	#	-32(%ebp)				-36(%ebp)
	movl	%eax, -12(%ebp)
	movl	%ebx, -16(%ebp)
	movl	%ecx, -32(%ebp)
	movl	%edx, -24(%ebp)
	movl	%esi, -28(%ebp)
	movl	%edi, -40(%ebp)
	pushl	-40(%ebp)
	call	*-32(%ebp)
	addl	$4, %esp

	# EXIT
	#							
	pushw	$0
	call	exit

