option MINLP=BARON;
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
integer variable c(j, t);
binary variable q(i, t);

variable z;
equation obj, const1, const2;

obj..
    z =e= sum((j, t, tp) $ (t.val >= tp.val), (c(j, t) * c(j, tp)) / power(2.71, t.val - tp.val));

const1(i)..
    sum(t$(p(i, t)=1),  q(i,t)) =e= 1;

const2(j, t)..
    c(j,t) =e= sum(i$(a(j, i)=1), q(i, t));

model PROJECT_1 /all/;
solve PROJECT_1 using MINLP minimizing z;
display q.l,c.l , z.l,PROJECT_1.etSolve;