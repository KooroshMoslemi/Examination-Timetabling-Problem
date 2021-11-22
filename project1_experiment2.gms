option MIP=CPLEX;
option optcr=0;
option optca=0;
option reslim=25200;


set
    i
    j
    t;

alias(t, tp);

parameter
    a(j, i)
    p(i, t);

$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$onMulti
$load i j t a p
$gdxin

display i,j,t,a,p;

binary variable q(i, t);
integer variable v(j, t);
variable z;
equation obj, const1, const2;

obj..
    z =e= sum((j,t),v(j,t));

const1(i)..
    sum(t$(p(i, t)=1),  q(i,t)) =e= 1;

const2(j, t)..
    sum(i$(a(j, i)=1), q(i, t)) - v(j,t) =l= 1;

model PROJECT_1 /all/;
solve PROJECT_1 using MIP minimizing z;
display q.l,v.l, z.l,PROJECT_1.etSolve;