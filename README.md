# macropy

macro.py is offered in the hope it might be useful.

It is invoked as follows :

python3 macro.py input_file
which presumes that both the macro.py program and the input file are in the working directory.
output goes to stdout.

macro.py is inspired by the standard Linux C macro preprocessor.
There are only two directives:
#include "path/to/included/file"
and
#define
as below.
#define example_macro(p1,p2,p3) print(p3,p1,p2)
Invoke example_macro:
example_macro(A,B,C)
which gives
 print(C,A,B)
Please note the leading space. This is in the definition of example_macro.
The definition is composed of:
      the #define keyword, followed by a space
      the macro name example_macro
      the comma-separated macro argument placeholders enclosed in brackets
      the immediately following macro body which is composed of text and 
              references to the macro argument placeholders.
      When the macro is invoked with parameters a corresponding text substitution is made.

I have used macro.py on C source files to expand complex macros in a readable fashion.
It may be necessary to strip comments from the source
before invoking macro.py. This can be achieved on Linux as follows:

gcc -fpreprocessed -dD -E $1 > temp.cpp
python3 ./macro.py temp.cpp > $1.ot

This is because macro.py does not at present recognise comments and processes the whole
file as one block of text, expanding macro calls as it finds them.

There follows a list of example inputs and outputs from the program.
Macro.py is not limited to C source files and is useful for general text manipulation.

The following definitions work as expected.
Input as follows:

#define n1024 1024
n1024
#define n32k 1024 * 32
n32k
#define n1024 nan
n1024
#define n16k 1024 * 16
n16k
#define n1024 nan
n1024
#define n32k n1024 * 32
n32k

NOTE: this is how to delete a macro, simply quote its name only in a definition.
#define n1024

n1024
#define n16k n1024 * 16
n16k
Gives output:

1024
1024 * 32
nan
1024 * 16
nan
nan * 32
n1024
n1024 * 16

****************************************

You can do this:

#define macro #define
#define m1 macro m2(p1,p2)
m1
which gives this:

#define m2(p1,p2)
****************************************

Macro parameters can be nested as in

#define myfunc(p1,p2,p3) generate p1 p2 p3
#define H XX
myfunc(A,B[2 ],C(D(e),F(H,I,J)))

which gives this:
 generate A B[2 ] C(D(e),F(XX,I,J))
****************************************

input from demo
****************************************
#define B(x) x * x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1 p2 p3
#define P(x,y) B(x) + D(y)
myfunc(D(3),B(2),P(3,2))

****************************************
output from demo
****************************************
 generate  log(3)  2 * 2   3 * 3 +  log(2)

****************************************

input from demo2
****************************************
#define B(x) x * x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B(2),D(Z,))

****************************************
output from demo2
****************************************
 generate A  2 * 2  log(Z)
****************************************

input from t1
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C)
****************************************
output from t1
****************************************
 generate A B C
****************************************

input from t2
****************************************
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D))
****************************************
output from t2
****************************************
 generate A B  print D
****************************************

input from t3
****************************************
#define myfunc(p1,p2,p3(p4,p5)) generate p1 p2 p3
myfunc(A,B,C)
****************************************
output from t3
where macro.py could not match a parameter
because parameters are matched by name in the macro body
****************************************
 generate A B p3
****************************************

input from t4
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D,E,F))
****************************************
output from t4
****************************************
 generate A B C(D,E,F)
****************************************

input from t5
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D,E))
****************************************
output from t5
****************************************
 generate A B C(D,E)
****************************************

input from t6
****************************************
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D))
C(me)
****************************************
output from t6
****************************************
 generate A B  print D
 print me
****************************************

input from t7
****************************************
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(me))
****************************************
output from t7
****************************************
 generate A B  print me
****************************************

input from t8
****************************************
#define D "me me me"
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D))

****************************************
output from t8
****************************************
 generate A B  print "me me me"
****************************************

input from t9
****************************************
#define E(x) sin(x)
#define D "hello" E(F)
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D))
****************************************
output from t9
****************************************
 generate A B  print "hello"  sin(F)
****************************************

input from t10
****************************************
#define E(x) sin(x)
#define D 'me me me' E(F)
#define C(D) print D
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B,C(D))
****************************************
output from t10
****************************************
 generate A B  print 'me me me'  sin(F)
****************************************

input from t11
****************************************
#define C(x) print x
C('Me me me')
****************************************
output from t11
****************************************
 print 'Me me me'
****************************************

input from t12
****************************************
#define C(x) print x
C('hello')
****************************************
output from t12
****************************************
 print 'hello'
****************************************

input from t15
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C)
****************************************
output from t15
****************************************
 generate A B[2 ] C
****************************************

input from t16
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C(D(e)))
****************************************
output from t16
****************************************
 generate A B[2 ] C(D(e))
****************************************

input from t17
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C(D(e),F(H)))
****************************************
output from t17
****************************************
 generate A B[2 ] C(D(e),F(H))
****************************************

input from t18
****************************************
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
****************************************
output from t18
****************************************
 generate A B[2 ] C(D(e),F(H,I,J))
****************************************

input from t22
****************************************
#define B(x) x*x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
#########################
#define P(L, M) L ## M
P(R, S)
P(Z ## X, M)
P(99##101, M)
****************************************
output from t22
****************************************

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A B[2 ] C(D(e),F(H,I,J))

 generate A B[2 ] C( log(e),F(H,I,J))
#########################
 R ##  S
 Z ## X ##  M
 99##101 ##  M
****************************************

input from t23
****************************************
#define B(x) x * x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1 p2 p3
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
######################
#define P(L, M) L ## M
P(R, S)
######################
myfunc(D(3),B(2),P(Z,W))
****************************************
output from t23
****************************************

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A B[2 ] C(D(e),F(H,I,J))

 generate A B[2 ] C( log(e),F(H,I,J))
######################
 R ##  S
######################
 generate  log(3)  2 * 2  Z ## W
****************************************

input from t24
****************************************
#define B(x) x * x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1, p2, p3

myfunc(A,B[2 ],C(D(e),F(H,I,J)))
########################
myfunc(D(3),B(2),P(Z,W))

****************************************
output from t24
****************************************

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A, B[2 ], C(D(e),F(H,I,J))

 generate A, B[2 ], C( log(e),F(H,I,J))
########################
 generate  log(3),  2 * 2, P(Z,W)
****************************************

input from t24b
****************************************
#define B(x) x * x
#define D(x) log(x)
#define myfunc(p1,p2,p3) generate p1, p2, p3
#########################
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
#########################

myfunc(D(3),B(2),P(,W))
myfunc(D(3),B(2),C(,B(6)))
****************************************
output from t24b

****************************************
#########################

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A, B[2 ], C(D(e),F(H,I,J))

 generate A, B[2 ], C( log(e),F(H,I,J))
#########################

 generate  log(3),  2 * 2, P(,W)
 generate  log(3),  2 * 2, C(, 6 * 6)
****************************************

input from t24c
****************************************
#define B(x)x*x
#define D(x)log(x)
#define myfunc(p1,p2,p3) generate p1, p2, p3
#########################
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
#########################

myfunc(D(3),B(2),P(,W))
myfunc(D(3),B(2),C(,B(6)))
myfunc((D(3)),(B(2)),C(,,B(6)))
****************************************
output from t24c

****************************************
#########################

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A, B[2 ], C(D(e),F(H,I,J))

 generate A, B[2 ], C(log(e),F(H,I,J))
#########################

 generate log(3), 2*2, P(,W)
 generate log(3), 2*2, C(,6*6)
 generate (log(3)), (2*2), C(,,6*6)
****************************************

input from t24d
****************************************
#define B(x)x*x
#define D(x)log(x)
#define myfunc(p1,p2,p3) generate p1, p2, p3
#########################
myfunc(A,B[2 ],C(D(e),F(H,I,J)))
#########################

myfunc(D(3),B(2),P(,W))
myfunc(D(3),B(2),C(,B(6)))
myfunc((D(3)),(B(2)),C(,,B(6)))
#define D
myfunc(D(3),B(2),P(,W))
myfunc(D(3),B(2),C(,B(6)))
myfunc((D(3)),(B(2)),C(,,B(6)))
#define D()
myfunc(D(3),B(2),P(,W))
myfunc(D(3),B(2),C(,B(6)))
myfunc((D(3)),(B(2)),C(,,B(6)))
****************************************
output from t24d

****************************************
#########################

macro.py *debug*  macro  B  missing arguments

macro.py *debug*  at   generate A, B[2 ], C(D(e),F(H,I,J))

 generate A, B[2 ], C(log(e),F(H,I,J))
#########################

 generate log(3), 2*2, P(,W)
 generate log(3), 2*2, C(,6*6)
 generate (log(3)), (2*2), C(,,6*6)
 generate D(3), 2*2, P(,W)
 generate D(3), 2*2, C(,6*6)
 generate (D(3)), (2*2), C(,,6*6)
 generate ()(3), 2*2, P(,W)
 generate ()(3), 2*2, C(,6*6)
 generate (()(3)), (2*2), C(,,6*6)
****************************************
input from t25
****************************************
#define test(A,B) AB
l1test(C,D)
l2test()
l3test(c)
l4test(,d)
l5test(A,)
l6test(,B)
****************************************
output from t25

****************************************
l1 CD
l2 
l3 c
l4 d
l5 A
l6 B
****************************************
input from t26
****************************************
#  define m20(A,B, C, D)ABCD
textm20()
textm20(,B)
textm20(,Bee)
textm20(A,,C,D)
****************************************
output from t26

****************************************
text
textB
textBee
textACD
****************************************
input from t27
****************************************
#  define m20(A,B, C, D)ABCDm20(blockme)
textm20()
textm20(,B)
textm20(,Bee)
textm20(A,,C,D)
****************************************
output from t27

****************************************
recursive macro call not allowed from within body of macro

macro.py *debug*  recursive macro call

macro.py *debug*  textm20()
 

['m20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20']
textblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmem20(blockme)

macro.py *debug*  recursive macro call

macro.py *debug*  textm20(,B)
 

['m20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20']
textBblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmem20(blockme)

macro.py *debug*  recursive macro call

macro.py *debug*  textm20(,Bee)
 

['m20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20']
textBeeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmem20(blockme)

macro.py *debug*  recursive macro call

macro.py *debug*  textm20(A,,C,D) 

['m20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20', 'm20']
textACDblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmeblockmem20(blockme)
****************************************

input from t28
****************************************
#  define m20(A,B, C, D)ABCD
textm20(,B)
****************************************
output from t28
****************************************
textB
****************************************

input from t29
****************************************
#  define m20(A,B, C, D)ABCD
textm20(,B,m20(,,C))
textm20(,X,m20(,,Y))

****************************************
output from t29
****************************************
textBC
textXY

recursive macro call is allowed within positional macro parameters.

