option MINLP=BARON;
option optcr=0;
option optca=0;
option reslim=21600;


set
    w
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
$load w i j t a p
$gdxin

display w,i,j,t,a,p;
integer variable c(j, t);
integer variable cp(j, w);
integer variable u(j);
binary variable q(i, t);

variable z;
equation obj, const1, const2,const3,const4,const5,const6;

obj..
    z =e= 50*sum(j,u(j)) + sum((j, t, tp) $ (tp.val > t.val and mod(tp.val,7)<=3 and mod(t.val,7)<=3 and (tp.val-t.val)<=10) , -(tp.val-t.val)*(tp.val-t.val)*c(j,t)*c(j,tp));

const1(i)..
    sum(t$(p(i, t)=1),  q(i,t)) =e= 1;

const2(j, t)..
    c(j,t) =e= sum(i$(a(j, i)=1), q(i, t));

const3(j, t)..
    c(j,t) =l= 1;

const4(i)..
    sum(t$(p(i, t)=0),  q(i,t)) =e= 0;

const5(j,w)..
    cp(j,w) =e= sum(t$( t.val >= 7*(w.val-1) and t.val <= (7*w.val)-4), c(j,t));

const6(j,w)..
    u(j) =g= cp(j,w);

model PROJECT_1 /all/;
solve PROJECT_1 using MINLP minimizing z;
display q.l,c.l , z.l,PROJECT_1.etSolve;