"""Offline, hand-written selection oracles, not actual provider or model evaluation."""
import json
import subprocess
import sys
import unittest

from src.cloud_architecture_selection import select, LIMITS, PROVIDERS


def profile(**overrides):
    return {
        'data_class':'public','visibility':'public','source_visibility':'public',
        'identity':'none','consistency':'none','commercial':False,'backend':False,
        'durable_data':False,'google_workspace_integration':False,
        'controlled_writers':True,'custom_domain':False,'no_inactivity_pause':False,
        'guaranteed_sla':False,'estimates':{},**overrides,
    }


def dynamic(**overrides):
    return profile(**{'backend':True,'durable_data':True,'identity':'custom',
                      'consistency':'single_writer',**overrides})


def candidate(result,p):
    return next(c for c in result['candidates'] if c['provider']==p)


def zero_estimates():
    return {p:{k:0 for k in metrics} for p,metrics in LIMITS.items()}


class CloudArchitectureSelectionTests(unittest.TestCase):
    def test_public_static(self):
        r=select(profile())
        self.assertEqual(r['preferred'],'pages')
        self.assertEqual(candidate(r,'pages')['status'],'CONDITIONAL')
        self.assertTrue(candidate(r,'pages')['missing_estimates'])
        self.assertEqual(candidate(r,'gas_sheets')['status'],'EXCLUDED')

    def test_private_source_and_commercial_exclude_pages(self):
        for field,v in (('source_visibility','private'),('commercial',True)):
            r=select(profile(**{field:v}))
            self.assertEqual(r['preferred'],'workers_d1')
            self.assertEqual(candidate(r,'pages')['status'],'EXCLUDED')
            self.assertNotIn(' + D1',candidate(r,'workers_d1')['architecture'])

    def test_workspace_controlled_admin(self):
        r=select(dynamic(google_workspace_integration=True,visibility='restricted',data_class='internal_non_sensitive'))
        self.assertEqual(r['preferred'],'gas_sheets')
        self.assertIn('verified_visitor_not_deployer',candidate(r,'gas_sheets')['required_checks'])

    def test_workspace_does_not_override_sql_or_writer_boundary(self):
        for values in ({'consistency':'sql'},{'controlled_writers':False},{'custom_domain':True}):
            r=select(dynamic(google_workspace_integration=True,**values))
            self.assertEqual(r['preferred'],'workers_d1')
            self.assertEqual(candidate(r,'gas_sheets')['status'],'EXCLUDED')

    def test_editorial_transactional_workflow(self):
        r=select(dynamic(consistency='sql'))
        self.assertEqual(r['preferred'],'workers_d1')
        self.assertIn('conditional_atomic_batch_no_zero_row_success',candidate(r,'workers_d1')['required_checks'])
        self.assertEqual(candidate(r,'pages')['status'],'EXCLUDED')
        self.assertEqual(candidate(r,'gas_sheets')['status'],'EXCLUDED')

    def test_managed_auth_or_postgres(self):
        for flags in ({'identity':'managed'},{'consistency':'postgres'}):
            r=select(dynamic(**flags))
            self.assertEqual(r['preferred'],'supabase')
            self.assertEqual(candidate(r,'workers_d1')['status'],'EXCLUDED')
            self.assertIn('separate_frontend_host_and_cost',candidate(r,'supabase')['required_checks'])

    def test_managed_auth_no_pause_no_free_fit(self):
        r=select(dynamic(identity='managed',no_inactivity_pause=True))
        self.assertIsNone(r['preferred'])
        self.assertEqual(r['status'],'NO_CONFIRMED_FREE_FIT')
        self.assertTrue(all(c['status']=='EXCLUDED' for c in r['candidates']))

    def test_governance_and_sla_cannot_be_ranked_away(self):
        for data in ('personal','sensitive'):
            r=select(dynamic(data_class=data,estimates=zero_estimates()))
            self.assertEqual(r['status'],'NEEDS_DATA_GOVERNANCE')
            self.assertNotIn('preferred',r)
        self.assertEqual(select(profile(guaranteed_sla=True))['status'],'NO_CONFIRMED_FREE_FIT')

    def test_missing_and_invalid_requirements(self):
        self.assertEqual(select(profile(identity=None))['status'],'NEEDS_REQUIREMENTS')
        mutations=[profile(backend='false'),profile(commercial=0),profile(identity='unknown'),
                   profile(visibility='restricted'),profile(consistency='sql'),
                   profile(durable_data=True),profile(**{'deployment_permitted':True})]
        missing=profile();missing.pop('data_class');mutations.append(missing)
        for x in mutations:
            self.assertEqual(select(x)['status'],'INVALID_PROFILE')

    def test_invalid_quota_units_and_types(self):
        for estimate in ({'pages':{'site_mb':True}}, {'pages':{'site_mb':-1}},
                         {'pages':{'site_mb':1.5}}, {'pages':{'wrong_unit':1}},
                         {'invented':{}}, {'pages':[]}, {'pages':{'site_mb':10**16}}):
            self.assertEqual(select(profile(estimates=estimate))['status'],'INVALID_PROFILE')

    def test_quota_boundary_each_provider(self):
        for stack, key, limit, p in [
            ('pages','site_mb',1000,profile()),
            ('gas_sheets','concurrent_per_user',30,dynamic(google_workspace_integration=True)),
            ('workers_d1','d1_rows_written_day_account',100000,dynamic(consistency='sql')),
            ('supabase','db_mb_project',500,dynamic(identity='managed')),
        ]:
            for n in (limit-1,limit,limit+1):
                r=select({**p,'estimates':{stack:{key:n}}})
                c=candidate(r,stack)
                self.assertEqual(c['status'],'EXCLUDED' if n>limit else 'CONDITIONAL')
                if n<=limit:self.assertIn(key,c['near_limit'])

    def test_no_estimate_means_unknown_not_zero(self):
        r=select(dynamic(consistency='sql',estimates={'workers_d1':{'d1_rows_read_day_account':None}}))
        self.assertIn('d1_rows_read_day_account',candidate(r,'workers_d1')['missing_estimates'])
        self.assertFalse(r['free_cost_guaranteed'])

    def test_rank_respects_estimates_without_bypassing_hard_exclusion(self):
        e=zero_estimates()
        e['workers_d1']['worker_cpu_ms_invocation']=11
        r=select(dynamic(consistency='sql',estimates=e))
        self.assertEqual(r['preferred'],'supabase')
        self.assertEqual(candidate(r,'gas_sheets')['status'],'EXCLUDED')
        self.assertEqual(candidate(r,'workers_d1')['status'],'EXCLUDED')

    def test_near_limit_and_incomplete_do_not_certify_actual_account(self):
        e=zero_estimates()
        e['pages']['site_mb']=800
        r=select(profile(estimates=e))
        self.assertEqual(r['preferred'],'workers_d1')
        self.assertIn('site_mb',candidate(r,'pages')['near_limit'])
        self.assertFalse(r['actual_provider_verified'])

    def test_all_results_are_advisory(self):
        for p in (profile(),dynamic(),profile(data_class='sensitive'),{},profile(identity=None),
                  profile(guaranteed_sla=True)):
            r=select(p)
            for key in ('deployment_permitted','external_write_permitted','paid_upgrade_permitted',
                        'actual_provider_verified','free_cost_guaranteed','formal_release_permitted'):
                self.assertIs(r[key],False)
            for c in r.get('candidates',[]):
                self.assertTrue(c['sources'])
                self.assertTrue(c['required_checks'])
        self.assertEqual(set(LIMITS),set(PROVIDERS))

    def test_cli_real_input_and_malformed(self):
        cmd=[sys.executable,'-m','src.cloud_architecture_selection']
        for payload,code in [(json.dumps(profile()).encode(),0),
                             (b'{"a":1,"a":2}',2),(b'x'*65537,2),(b'\xff',2)]:
            p=subprocess.run(cmd,input=payload,capture_output=True,timeout=10)
            self.assertEqual(p.returncode,code)
            self.assertFalse(json.loads(p.stdout)['deployment_permitted'])
