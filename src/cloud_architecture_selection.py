"""TP-006: offline advisory selection for four free-tier website stacks.

Not a provider client, cost guarantee, identity check, or deployment gate.
All facts about accounts, estimates and requirements are supplied by the caller.
"""
import json
import sys

POLICY_VERSION = 'TP-006/1'
SOURCE_DATE = '2026-11-15'
FIELDS = {
    'data_class': ('public', 'internal_non_sensitive', 'personal', 'sensitive'),
    'visibility': ('public', 'restricted'),
    'source_visibility': ('public', 'private'),
    'identity': ('none', 'custom', 'managed'),
    'consistency': ('none', 'single_writer', 'sql', 'postgres'),
}
FLAGS = (
    'commercial', 'backend', 'durable_data', 'google_workspace_integration',
    'controlled_writers', 'custom_domain', 'no_inactivity_pause', 'guaranteed_sla',
)
PROVIDERS = ('pages', 'gas_sheets', 'workers_d1', 'supabase')
# Integer planning units, MB and GB as named. Public ceilings, not actual
# remaining account capacity or quotas for every feature. Free/consumer only.
LIMITS = {
    'pages': {
        'site_mb': 1000, 'bandwidth_gb_month': 100,
        'deploy_seconds': 600,
    },
    'gas_sheets': {
        'execution_seconds': 360, 'concurrent_per_user': 30,
        'concurrent_per_script': 1000, 'versions_total': 200,
        'mail_recipients_day': 100, 'trigger_seconds_day': 5400,
        'url_fetch_day': 20000, 'sheets_reads_min_project': 300,
        'sheets_writes_min_project': 300, 'sheets_reads_min_user_project': 60,
        'sheets_writes_min_user_project': 60,
    },
    'workers_d1': {
        'worker_requests_day_account': 100000, 'worker_cpu_ms_invocation': 10,
        'd1_rows_read_day_account': 5000000, 'd1_rows_written_day_account': 100000,
        'd1_largest_db_mb': 500, 'd1_total_mb_account': 5000,
        'd1_databases_account': 10, 'd1_queries_invocation': 50,
    },
    'supabase': {
        'db_mb_project': 500, 'active_projects_account': 2,
        'auth_mau': 50000, 'file_storage_mb': 1000,
        'egress_gb_month': 5, 'cached_egress_gb_month': 5,
    },
}
SOURCES = {
    'pages': [
        'https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages',
        'https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits',
        'https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https',
    ],
    'gas_sheets': [
        'https://developers.google.com/apps-script/guides/services/quotas',
        'https://developers.google.com/apps-script/guides/web',
        'https://developers.google.com/apps-script/reference/base/session',
        'https://developers.google.com/apps-script/reference/lock/lock-service',
        'https://developers.google.com/workspace/sheets/api/limits',
        'https://developers.google.com/apps-script/concepts/deployments',
        'https://developers.google.com/apps-script/api/reference/rest',
    ],
    'workers_d1': [
        'https://developers.cloudflare.com/workers/platform/limits/',
        'https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/',
        'https://developers.cloudflare.com/d1/platform/limits/',
        'https://developers.cloudflare.com/d1/platform/pricing/',
        'https://developers.cloudflare.com/d1/worker-api/d1-database/',
        'https://developers.cloudflare.com/d1/reference/faq/',
    ],
    'supabase': [
        'https://supabase.com/pricing',
        'https://supabase.com/docs/guides/database/postgres/row-level-security',
        'https://supabase.com/docs/guides/platform/backups',
        'https://supabase.com/docs/guides/deployment/going-into-prod',
    ],
}
CHECKS = {
    'pages': ['public_only_artifact_and_source', 'pages_use_terms',
              'project_base_path_and_https', 'artifact_sha_and_deployed_url',
              'rebuild_previous_artifact', 'github_actions_and_domain_cost'],
    'gas_sheets': ['verified_visitor_not_deployer', 'private_sheet_no_direct_client_access',
                   'single_script_writer_and_revision_guard', 'atomic_same_sheet_batch_and_receipt',
                   'formula_injection_and_lock_timeout', 'restore_to_new_workbook',
                   'script_id_content_version_deployment_id_exec_url', 'oauth_scope_and_account_quota'],
    'workers_d1': ['server_auth_acl_csrf_secure_cookie', 'isolated_binding_and_secrets',
                   'conditional_atomic_batch_no_zero_row_success', 'read_only_receipt_on_unknown',
                   'cpu_rows_quota_abuse_controls', 'export_restore_new_database',
                   'remote_worker_version_and_schema_compatible_rollback'],
    'supabase': ['separate_frontend_host_and_cost', 'rls_and_grants_all_exposed_tables',
                 'auth_jwt_role_owner_and_no_service_role_in_client',
                 'transaction_rpc_and_storage_policy', 'free_pause_and_quota_handling',
                 'logical_dump_and_separate_object_backup_restore',
                 'migration_sha_and_frontend_database_compatible_rollback'],
}


def _result(status, **kwargs):
    return {'policy': POLICY_VERSION, 'source_date': SOURCE_DATE,
            'status': status, 'deployment_permitted': False,
            'external_write_permitted': False, 'paid_upgrade_permitted': False,
            'actual_provider_verified': False, 'free_cost_guaranteed': False,
            'formal_release_permitted': False, **kwargs}


def select(profile):
    """Strict structured profile, with unknowns explicit as null.

    Estimates are peak totals in named units including existing usage where
    applicable, not counts of users or predicted bills. No network, writes,
    provider credentials, or authorization fields are accepted.
    """
    if type(profile) is not dict or set(profile) != set(FIELDS) | set(FLAGS) | {'estimates'}:
        return _result('INVALID_PROFILE', errors=['exact_profile_fields_required'])
    unknown = []
    for field, values in FIELDS.items():
        v = profile[field]
        if v is None:
            unknown.append(field)
        elif not isinstance(v, str) or v not in values:
            return _result('INVALID_PROFILE', errors=[field])
    for field in FLAGS:
        v = profile[field]
        if v is None:
            unknown.append(field)
        elif type(v) is not bool:
            return _result('INVALID_PROFILE', errors=[field])
    estimates = profile['estimates']
    if type(estimates) is not dict or set(estimates) - set(PROVIDERS):
        return _result('INVALID_PROFILE', errors=['estimates'])
    for provider, vals in estimates.items():
        if type(vals) is not dict or set(vals) - set(LIMITS[provider]):
            return _result('INVALID_PROFILE', errors=['estimate_fields:'+provider])
        for key,value in vals.items():
            if value is not None and (type(value) is not int or not 0 <= value <= 10**15):
                return _result('INVALID_PROFILE', errors=['estimate_value:'+provider+':'+key])
    if unknown:
        return _result('NEEDS_REQUIREMENTS', missing=sorted(unknown))
    p=profile
    if (p['visibility']=='restricted' and p['identity']=='none'
        or not p['durable_data'] and p['consistency']!='none'
        or p['durable_data'] and p['consistency']=='none'):
        return _result('INVALID_PROFILE', errors=['inconsistent_requirements'])
    if p['data_class'] in ('personal','sensitive'):
        return _result('NEEDS_DATA_GOVERNANCE', missing=[
            'approved_data_classification_and_lawful_basis',
            'institution_region_retention_and_provider_review',
            'approved_security_and_access_boundary'])
    if p['guaranteed_sla']:
        return _result('NO_CONFIRMED_FREE_FIT', reasons=['required_sla_not_established_on_free_tiers'])
    dynamic = (p['backend'] or p['durable_data'] or p['identity']!='none'
               or p['visibility']=='restricted' or p['data_class']!='public'
               or p['google_workspace_integration'])
    rejected = {
        'pages': [],
        'gas_sheets': [],
        'workers_d1': [],
        'supabase': [],
    }
    if dynamic: rejected['pages'].append('static_host_only')
    if p['commercial']: rejected['pages'].append('pages_commercial_scope_not_established')
    if p['source_visibility']=='private': rejected['pages'].append('free_public_source_required')
    if p['custom_domain']: rejected['gas_sheets'].append('native_exec_url_not_custom_domain')
    if p['consistency'] in ('sql','postgres'): rejected['gas_sheets'].append('sql_guarantees_required')
    if p['durable_data'] and not p['controlled_writers']:
        rejected['gas_sheets'].append('all_writers_not_controlled_by_same_script')
    if p['identity']=='managed':
        rejected['gas_sheets'].append('managed_application_identity_requires_other_service')
        rejected['workers_d1'].append('managed_application_identity_requires_other_service')
    if p['consistency']=='postgres': rejected['workers_d1'].append('postgres_specific_requirement')
    if p['no_inactivity_pause']: rejected['supabase'].append('free_project_may_pause')
    if not dynamic:
        rejected['gas_sheets'].append('unnecessary_backend_for_static_requirement')
        rejected['supabase'].append('unnecessary_database_service_for_static_requirement')
    # For static commercial/private source, Workers assets can be used without D1.
    # GAS is prioritized only when the workload benefits from Workspace services.
    order = (['pages','workers_d1','gas_sheets','supabase'] if not dynamic else
             ['supabase','workers_d1','gas_sheets','pages'] if p['identity']=='managed' or p['consistency']=='postgres' else
             ['gas_sheets','workers_d1','supabase','pages'] if p['google_workspace_integration'] else
             ['workers_d1','gas_sheets','supabase','pages'])
    candidates = []
    for provider in order:
        required = dict(LIMITS[provider])
        if provider=='workers_d1' and not p['durable_data']:
            required={k:v for k,v in required.items() if not k.startswith('d1_')}
        found=estimates.get(provider,{})
        missing=[k for k in required if found.get(k) is None]
        over=[k for k,v in required.items() if found.get(k) is not None and found[k]>v]
        # At/near public ceilings: flag loss of headroom, never certify free cost.
        near=[k for k,v in required.items() if found.get(k) is not None and v*8<=found[k]*10<=v*10]
        reasons=rejected[provider]+['projected_quota_exceeded:'+k for k in over]
        extra=list(CHECKS[provider])
        if p['google_workspace_integration'] and provider!='gas_sheets':
            extra.append('google_oauth_integration_and_independent_quotas')
        if p['custom_domain']:
            extra.append('domain_ownership_dns_tls_and_cost')
        if provider=='workers_d1' and not p['durable_data']:
            extra=[c for c in extra if c not in (
                'conditional_atomic_batch_no_zero_row_success','read_only_receipt_on_unknown',
                'export_restore_new_database')]
        candidates.append({'provider':provider,
                           'architecture': {'pages':'GitHub Pages + Actions',
                                            'gas_sheets':'GitHub + GAS Web App + private Sheets',
                                            'workers_d1':'GitHub + Workers Static Assets/API'+(' + D1' if p['durable_data'] else ''),
                                            'supabase':'GitHub + separately selected frontend + Supabase'}[provider],
                           'status':'EXCLUDED' if reasons else 'CONDITIONAL',
                           'reasons':reasons,'missing_estimates':missing,
                           'near_limit':near,'public_limits':required,
                           'required_checks':extra,'sources':SOURCES[provider]})
    # Prefer complete, reserve-bearing estimates over incomplete/near-limit
    # alternatives only after hard suitability constraints; no auto-authorize.
    viable=[c for c in candidates if c['status']=='CONDITIONAL']
    viable.sort(key=lambda c:(bool(c['near_limit']),bool(c['missing_estimates'])))
    preferred=viable[0]['provider'] if viable else None
    return _result('CONDITIONAL_OPTIONS' if viable else 'NO_CONFIRMED_FREE_FIT',
                   preferred=preferred, candidates=candidates,
                   shared_gates=['confirmed_requirements_and_exact_source',
                                 'provider_plan_account_remaining_quota_and_terms',
                                 'scoped_tool_and_separate_external_deployment_authorization',
                                 'security_review_backup_restore_and_rollback',
                                 'actual_https_remote_version_and_functional_acceptance',
                                 'separate_human_uat_and_formal_launch'])


def _unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key]=value
    return result


def main():
    try:
        raw=sys.stdin.buffer.read(65537)
        if len(raw)>65536:
            raise ValueError('profile too large')
        profile=json.loads(raw.decode('utf-8'),object_pairs_hook=_unique)
        result=select(profile)
    except (UnicodeError,ValueError,RecursionError):
        result=_result('INVALID_PROFILE',errors=['invalid_json_or_size'])
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 2 if result['status']=='INVALID_PROFILE' else 0


if __name__=='__main__':
    raise SystemExit(main())
