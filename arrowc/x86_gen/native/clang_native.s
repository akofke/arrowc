	.section	__TEXT,__text,regular,pure_instructions
	.globl	_print_int32
	.align	4, 0x90
_print_int32:                           ## @print_int32
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L0$pb
L0$pb:
	popl	%eax
	movl	8(%ebp), %ecx
	leal	L_.str-L0$pb(%eax), %eax
	movl	%ecx, -4(%ebp)
	movl	-4(%ebp), %ecx
	movl	%eax, (%esp)
	movl	%ecx, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.globl	_print_uint32
	.align	4, 0x90
_print_uint32:                          ## @print_uint32
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L1$pb
L1$pb:
	popl	%eax
	movl	8(%ebp), %ecx
	leal	L_.str1-L1$pb(%eax), %eax
	movl	%ecx, -4(%ebp)
	movl	-4(%ebp), %ecx
	movl	%eax, (%esp)
	movl	%ecx, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.globl	_print_int8
	.align	4, 0x90
_print_int8:                            ## @print_int8
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L2$pb
L2$pb:
	popl	%eax
	movb	8(%ebp), %cl
	leal	L_.str2-L2$pb(%eax), %eax
	movb	%cl, -1(%ebp)
	movsbl	-1(%ebp), %edx
	movl	%eax, (%esp)
	movl	%edx, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.globl	_print_uint8
	.align	4, 0x90
_print_uint8:                           ## @print_uint8
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L3$pb
L3$pb:
	popl	%eax
	movb	8(%ebp), %cl
	leal	L_.str3-L3$pb(%eax), %eax
	movb	%cl, -1(%ebp)
	movzbl	-1(%ebp), %edx
	movl	%eax, (%esp)
	movl	%edx, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.globl	_print_float32
	.align	4, 0x90
_print_float32:                         ## @print_float32
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L4$pb
L4$pb:
	popl	%eax
	movss	8(%ebp), %xmm0
	leal	L_.str4-L4$pb(%eax), %eax
	movss	%xmm0, -4(%ebp)
	cvtss2sd	-4(%ebp), %xmm0
	movl	%eax, (%esp)
	movsd	%xmm0, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.globl	_print
	.align	4, 0x90
_print:                                 ## @print
## BB#0:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	calll	L5$pb
L5$pb:
	popl	%eax
	movl	8(%ebp), %ecx
	leal	L_.str5-L5$pb(%eax), %eax
	movl	%ecx, -4(%ebp)
	movl	-4(%ebp), %ecx
	movl	%eax, (%esp)
	movl	%ecx, 4(%esp)
	calll	_printf
	movl	%eax, -8(%ebp)          ## 4-byte Spill
	addl	$24, %esp
	popl	%ebp
	ret

	.section	__TEXT,__cstring,cstring_literals
L_.str:                                 ## @.str
	.asciz	"%d\n"

L_.str1:                                ## @.str1
	.asciz	"%u\n"

L_.str2:                                ## @.str2
	.asciz	"%hhd\n"

L_.str3:                                ## @.str3
	.asciz	"%hhu\n"

L_.str4:                                ## @.str4
	.asciz	"%g\n"

L_.str5:                                ## @.str5
	.asciz	"%s"


.subsections_via_symbols
