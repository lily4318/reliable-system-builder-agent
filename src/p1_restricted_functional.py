"""Bounded B003 public development functional tool, not a Python sandbox.

Interpret a deliberately small Python syntax subset over trusted immutable
integer intervals. Never compile, eval, exec, import or call candidate code.
Public fixed oracle is authored separately from candidate, not a hidden holdout
or independent human reviewer. Invalid inputs are blocked by the host.
"""
import ast
import hashlib
import json

CONTRACT={
    'task':'B003','function':'has_overlap(existing, proposed)',
    'input':'existing tuple of up to 32 pairs; proposed pair; exact integers -10080..10080, start < end',
    'output':'strict boolean: any existing interval overlaps proposed; endpoints touching do not overlap',
    'invalid_input_policy':'host rejects invalid intervals; candidate only evaluated for valid inputs',
    'syntax':'one plain def, two named positional arguments, if/else, for item in existing, return, boolean operations, comparisons, integer/boolean literals, index by 0 or 1, local assignment; no imports, calls, attributes, other Python syntax or code fences',
}
# Fixed expected values, not derived from the implementation or a model reply.
CASES=(
 ('empty',(),(10,20),False),
 ('touch-left',((0,10),),(10,20),False),
 ('touch-right',((20,30),),(10,20),False),
 ('overlap-left',((0,11),),(10,20),True),
 ('overlap-right',((19,30),),(10,20),True),
 ('contained',((12,18),),(10,20),True),
 ('contains',((0,30),),(10,20),True),
 ('equal',((10,20),),(10,20),True),
 ('disjoint-many',((0,5),(20,30),(30,31)),(10,20),False),
 ('last-overlap',((0,5),(20,30),(12,13)),(10,20),True),
 ('negative-time',((-8,-3),),(-3,2),False),
 ('negative-overlap',((-8,-3),),(-4,2),True),
)
ALLOWED=(ast.Module,ast.FunctionDef,ast.arguments,ast.arg,ast.If,ast.For,
         ast.Return,ast.Assign,ast.Name,ast.Load,ast.Store,ast.Constant,
         ast.Subscript,ast.BoolOp,ast.And,ast.Or,ast.UnaryOp,ast.Not,
         ast.Compare,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,
         ast.USub)


class Blocked(ValueError):
    pass


def _pair(x):
    return type(x) is tuple and len(x)==2 and all(type(n) is int and -10080<=n<=10080 for n in x) and x[0]<x[1]


def _inputs(existing,proposed):
    if type(existing) is not tuple or len(existing)>32 or not all(_pair(x) for x in existing) or not _pair(proposed):
        raise Blocked('INVALID_INPUT_HOST_REJECTED')


def _parse(source):
    if not isinstance(source,str) or not 1<=len(source)<=6000:
        raise Blocked('SOURCE_SIZE')
    try:
        tree=ast.parse(source,mode='exec')
    except (SyntaxError,RecursionError) as exc:
        raise Blocked('SOURCE_SYNTAX') from exc
    nodes=list(ast.walk(tree))
    if len(nodes)>240 or any(type(n) not in ALLOWED for n in nodes):
        raise Blocked('UNSUPPORTED_SYNTAX')
    if len(tree.body)!=1 or type(tree.body[0]) is not ast.FunctionDef:
        raise Blocked('ONE_FUNCTION_REQUIRED')
    fn=tree.body[0]
    a=fn.args
    if (fn.name!='has_overlap' or fn.decorator_list or fn.returns is not None or
        getattr(fn,'type_params',[]) or a.posonlyargs or a.kwonlyargs or
        a.defaults or a.kw_defaults or a.vararg or a.kwarg or
        [x.arg for x in a.args]!=['existing','proposed'] or
        any(x.annotation is not None for x in a.args) or
        sum(type(n) is ast.FunctionDef for n in nodes)!=1):
        raise Blocked('FUNCTION_CONTRACT')
    for n in nodes:
        if type(n) is ast.Name and (not n.id.isascii() or n.id.startswith('_') or len(n.id)>40):
            raise Blocked('NAME_NOT_PERMITTED')
        if type(n) is ast.Constant and not (type(n.value) is bool or type(n.value) is int and abs(n.value)<=10080):
            raise Blocked('LITERAL_NOT_PERMITTED')
        if type(n) is ast.Assign and (len(n.targets)!=1 or type(n.targets[0]) is not ast.Name or n.targets[0].id in ('existing','proposed')):
            raise Blocked('ASSIGNMENT_NOT_PERMITTED')
        if type(n) is ast.For and (type(n.target) is not ast.Name or n.target.id in ('existing','proposed') or
            type(n.iter) is not ast.Name or n.iter.id!='existing' or n.orelse):
            raise Blocked('LOOP_NOT_PERMITTED')
        if type(n) is ast.Subscript and (type(n.slice) is not ast.Constant or type(n.slice.value) is not int or n.slice.value not in (0,1)):
            raise Blocked('INDEX_NOT_PERMITTED')
    return fn


def _interpret(fn,existing,proposed):
    _inputs(existing,proposed)
    env={'existing':existing,'proposed':proposed}
    steps=0
    def tick():
        nonlocal steps
        steps+=1
        if steps>3000:
            raise Blocked('STEP_BUDGET')
    def boolean(x):
        if type(x) is not bool:
            raise Blocked('BOOLEAN_REQUIRED')
        return x
    def expr(n):
        tick()
        if type(n) is ast.Constant:
            return n.value
        if type(n) is ast.Name:
            if n.id not in env:
                raise Blocked('UNDEFINED_NAME')
            return env[n.id]
        if type(n) is ast.Subscript:
            x=expr(n.value)
            if not _pair(x):
                raise Blocked('INTERVAL_INDEX_REQUIRED')
            return x[n.slice.value]
        if type(n) is ast.UnaryOp:
            x=expr(n.operand)
            if type(n.op) is ast.Not:
                return not boolean(x)
            if type(n.op) is ast.USub and type(x) is int:
                return -x
            raise Blocked('INVALID_UNARY')
        if type(n) is ast.BoolOp:
            if type(n.op) is ast.And:
                return all(boolean(expr(v)) for v in n.values)
            if type(n.op) is ast.Or:
                return any(boolean(expr(v)) for v in n.values)
        if type(n) is ast.Compare:
            left=expr(n.left)
            for op,right in zip(n.ops,n.comparators):
                r=expr(right)
                if type(left) is not int or type(r) is not int:
                    raise Blocked('INTEGER_COMPARISON_REQUIRED')
                if not {ast.Eq:lambda:left==r,ast.NotEq:lambda:left!=r,
                        ast.Lt:lambda:left<r,ast.LtE:lambda:left<=r,
                        ast.Gt:lambda:left>r,ast.GtE:lambda:left>=r}[type(op)]():
                    return False
                left=r
            return True
        raise Blocked('EXPRESSION_NOT_PERMITTED')
    def statements(body):
        for n in body:
            tick()
            if type(n) is ast.Return:
                return True,boolean(expr(n.value))
            if type(n) is ast.Assign:
                env[n.targets[0].id]=expr(n.value)
            elif type(n) is ast.If:
                done,val=statements(n.body if boolean(expr(n.test)) else n.orelse)
                if done:
                    return done,val
            elif type(n) is ast.For:
                for item in existing:
                    tick()
                    env[n.target.id]=item
                    done,val=statements(n.body)
                    if done:
                        return done,val
            else:
                raise Blocked('STATEMENT_NOT_PERMITTED')
        return False,None
    done,value=statements(fn.body)
    if not done:
        raise Blocked('RETURN_REQUIRED')
    return value


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def oracle_digest():
    return _hash(json.dumps({'contract':CONTRACT,'cases':CASES},
                           sort_keys=True,separators=(',',':')).encode('utf-8'))


def evaluate(source):
    """Return only bounded tool facts; never execute arbitrary source."""
    report={'tool':'restricted-b003-intervals-v1','oracle_sha256':oracle_digest(),
            'source_sha256':_hash(source.encode('utf-8')) if isinstance(source,str) else None,
            'cases':[],'findings':[],'candidate_native_code_executed':False,
            'public_development_only':True,'independent_human_review':False,
            'release_authorized':False}
    try:
        fn=_parse(source)
    except Blocked as exc:
        report.update(status='BLOCKED_SYNTAX',findings=[str(exc)])
        return report
    for name,existing,proposed,expected in CASES:
        try:
            value=_interpret(fn,existing,proposed)
            passed=value is expected
            row={'id':name,'expected':expected,'actual':value,'pass':passed}
        except (Blocked,RecursionError) as exc:
            row={'id':name,'expected':expected,'error':str(exc),'pass':False}
        report['cases'].append(row)
        if not row['pass']:
            report['findings'].append(name+': expected '+str(expected)+'; '+str(row.get('error',row.get('actual'))))
    report['status']='PUBLIC_SLICE_PASS' if not report['findings'] else 'PUBLIC_SLICE_FAIL'
    return report
