"""P2-2d controlled report workflow on the existing bound task/artifact pool.

Explicit confirmed root changes only. Synthetic local paths, trusted operators.
File publication and workbench database commit are NOT one transaction: a stale
worker may leave an old-generation file, but cannot accept it as current.
No model calls, external deployment or live-source publication CAS.
"""
import io
import json
import zipfile
from pathlib import Path
from . import p22_snapshot_report as report, team_workbench as wb, workbench_tasks as tasks, workbench_learning as learn

STAGES = {
    'intake': ('project-intake', []),
    'spec': ('requirements-spec', ['intake']),
    'arch': ('architecture-design', ['spec']),
    'plan': ('task-planning', ['arch']),
    'impl': ('implement-feature', ['plan']),
    'qa': ('test-and-acceptance', ['impl']),
    'security': ('security-review', ['arch', 'impl']),
    'deploy-plan': ('deployment', ['qa', 'security']),
}


def _inspect(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.namelist()!=['report.json','manifest.json'] or z.testzip() is not None:
            raise ValueError('invalid bundle')
        raw=z.read('report.json')
        manifest=json.loads(z.read('manifest.json'))
        if manifest['report_sha256']!=report.sha(raw):
            raise ValueError('report hash mismatch')
        return json.loads(raw),manifest


def _capture(source, revision, policy):
    data=report.bundle(source,revision,policy)
    _,m=_inspect(data)
    return {'source_revision':revision,'policy_revision':policy,
            'snapshot_sha256':m['snapshot_sha256']},data


def _root(work, expected_root):
    current=wb.context(work,'resume-project')['artifacts']
    root=current.get('requirements')
    if type(expected_root) is not int or not root or root['id']!=expected_root:
        raise ValueError('stale requirement artifact; review first')
    return json.loads(root['content']),current


def _path(work, root_id):
    # Only the actual bound requirements artifact ID controls the output name.
    return wb.private_root(work)/('report-root-%d.zip'%root_id)


def initialize(work, source, source_revision, policy_revision):
    """Create a NEW synthetic-only workspace; partial setup must be reviewed."""
    config,_=_capture(source,source_revision,policy_revision)
    work=wb.initialize(work,'Synthetic version-bound report workflow')
    tasks.setup(work)
    learn.setup(work,include_training_cases=True)
    tasks.question(work,'LIVE','External activation prohibited in this exercise')
    mapping={}
    for priority,(name,(skill,deps)) in enumerate(STAGES.items()):
        tasks.add(work,name,name,priority,deps,[],['check'])
        mapping[name]=wb.catalog()[skill]['produces']
    tasks.add(work,'audit','Independent workspace audit',20,[],[],['check'])
    tasks.add(work,'activate','External activation (not authorized)',21,['deploy-plan'],['LIVE'],['check'])
    mapping.update(audit=None,activate=None)
    root=wb.handoff(work,'project-intake',json.dumps(config,sort_keys=True),'Synthetic pinned source and policy')['artifact_id']
    tasks.bind_artifacts(work,mapping,{k:1 for k in mapping},root,'bind-report','Synthetic controlled workflow',True)
    return {'root_id':root,'authorization_granted':False}


def revise(work, source, source_revision, policy_revision, expected_root,
           expected_revision, session, evidence, confirmed=False):
    if confirmed is not True:
        raise ValueError('confirmed source or policy change required')
    prior,_=_root(work,expected_root)
    new,_=_capture(source,source_revision,policy_revision)
    if new==prior or source_revision<prior['source_revision']:
        raise ValueError('no new source or policy version')
    if source_revision==prior['source_revision'] and new['snapshot_sha256']!=prior['snapshot_sha256']:
        raise ValueError('changed source requires a new revision')
    return tasks.revise(work,'intake',expected_revision,session,evidence,True,
        requirement={'expected_artifact_id':expected_root,'content':json.dumps(new,sort_keys=True),
                     'source_ref':'Synthetic confirmed source/policy version change'})


def verify(work, source, expected_root):
    """Read-only check of exact pinned bytes, not workflow acceptance."""
    config,_=_root(work,expected_root)
    actual,data=_capture(source,config['source_revision'],config['policy_revision'])
    if actual!=config:
        raise ValueError('source snapshot differs from pinned requirement')
    output=_path(work,expected_root)
    if output.is_symlink():
        return 'CONFLICT'
    if not output.exists():
        return 'NOT_OBSERVED'
    if not output.is_file():
        return 'CONFLICT'
    with output.open('rb') as f:
        return 'COMMITTED' if f.read(len(data)+1)==data else 'CONFLICT'


def complete_stage(work,source,task,session,expected_revision,expected_root,
                   expected_report=None,reconcile_existing=False):
    """Complete a claimed bound task, generating and testing actual ZIP bytes.

    QA uses an explicit caller-provided oracle. Existing output is only reused
    by an explicit read-only reconciliation choice; no blind publication retry.
    """
    if task not in STAGES:
        raise ValueError('unknown report stage')
    rows={r['id']:r for r in tasks.review(work)['tasks']}
    row=rows[task]
    if row['state']!='RUNNING' or row['session']!=session or type(expected_revision) is not int or row['revision']!=expected_revision:
        raise ValueError('stale task session or revision')
    config,current=_root(work,expected_root)
    actual,data=_capture(source,config['source_revision'],config['policy_revision'])
    if actual!=config:
        raise ValueError('source snapshot differs from pinned requirement')
    skill=wb.catalog()[STAGES[task][0]]
    kind=skill['produces']
    inputs={k:current[k]['id'] for k in skill['requires'] if k in current and current[k]['current']}
    if set(inputs)!=set(skill['requires']):
        raise ValueError('stale prerequisite')
    artifact={'expected_artifact_id':current[kind]['id'] if kind in current else None,'inputs':inputs}
    content={'root_id':expected_root,**config,'stage':task}
    if task in ('impl','qa','security','deploy-plan'):
        path=_path(work,expected_root)
        if task=='impl' and reconcile_existing is not True:
            report._publish_bundle(data,path)
        # Compare against the bytes from THIS pinned snapshot, not a second read.
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing or invalid report output')
        with path.open('rb') as f:
            observed=f.read(len(data)+1)
        if observed!=data:
            raise ValueError('output conflict; keep evidence and review')
        actual_report,manifest=_inspect(observed)
        content.update(output=path.name,zip_sha256=report.sha(observed),
                       report_sha256=manifest['report_sha256'])
        if task=='qa':
            if not isinstance(expected_report,dict):
                raise ValueError('explicit QA oracle required')
            if actual_report!=expected_report:
                return tasks.finish(work,task,session,{'check':'FAIL'},
                    'Synthetic exact report oracle mismatch',expected_revision)
        if task=='security':
            keys={'policy_revision','completed_quantities'}
            if config['policy_revision']==2:
                keys.add('status_counts')
            if set(actual_report)!=keys or set(actual_report['completed_quantities'])!=set(report.GROUPS):
                raise ValueError('unexpected report fields')
        if task=='deploy-plan':
            for prereq in ('implementation','qa','security-review'):
                evidence=json.loads(current[prereq]['content'])
                if evidence.get('root_id')!=expected_root or evidence.get('zip_sha256')!=content['zip_sha256']:
                    raise ValueError('stale acceptance evidence')
            content['external_activation_authorized']=False
    if kind!='requirements':
        artifact.update(content=json.dumps(content,sort_keys=True),source_ref='Synthetic report workflow stage '+task)
    return tasks.finish(work,task,session,{'check':'PASS'},
        'Controlled local stage '+task,expected_revision,artifact=artifact)
