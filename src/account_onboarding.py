"""TD-003 beginner-first onboarding: offline next-step advice, never account operations."""
import json
import sys
from src.human_walkthrough import walkthrough

PROVIDERS = {
    "github": ("GitHub", "https://github.com/signup", "https://github.com/settings/profile"),
    "google": ("Google Drive（GAS＋Sheets）", "https://accounts.google.com/signup", "https://myaccount.google.com/"),
    "cloudflare": ("Cloudflare", "https://dash.cloudflare.com/sign-up", "https://dash.cloudflare.com/"),
    "supabase": ("Supabase", "https://supabase.com/dashboard", "https://supabase.com/dashboard"),
}
ENUMS = {
    "account": ("unknown","missing","security_pending","ready"),
    "connection": ("unknown","missing","connected","wrong_account","denied","unavailable"),
    "readback": ("unknown","verified","failed","wrong_target"),
    "capability": ("unknown","supported","unsupported"),
    "cost": ("unknown","free_confirmed","not_free_or_uncertain"),
}
SOURCES = [
    "https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt",
    "https://help.openai.com/en/articles/20001495-managing-app-permissions-in-chatgpt",
    "https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt",
]
PROVIDER_SOURCES = {
    "github": ["https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account",
               "https://docs.github.com/en/apps/using-github-apps/installing-a-github-app-from-a-third-party"],
    "google": ["https://support.google.com/accounts/answer/27441",
               "https://developers.google.com/apps-script/api/how-tos/enable",
               "https://developers.google.com/apps-script/guides/services/quotas"],
    "cloudflare": ["https://developers.cloudflare.com/fundamentals/account/create-account/",
                   "https://developers.cloudflare.com/workers/platform/pricing/"],
    "supabase": ["https://supabase.com/docs/guides/platform",
                 "https://supabase.com/docs/guides/platform/billing-on-supabase"],
}
# Each step is a human-facing action, expected result and stop condition.
# These are documented routes, not live verified screenshots.
def step(action, check, stop):
    return {"action":action,"verification":check,"if_blocked":stop}

def signup(provider):
    name,url,home=PROVIDERS[provider]
    if provider=="github":
        return [step(x["action"],x["verification"],
                     "頁面不同、驗證失敗或要求付費時先停下，回報已遮蔽畫面及錯誤文字。")
                for x in walkthrough("github_signup")["steps"]]
    first={
        "google": "選建立帳戶（Create account）→ 個人用途；已持有合適個人 Google 帳號則改登入，不另開帳戶。",
        "cloudflare": "在 Sign up 輸入自己的電子郵件及自訂密碼，選 Create Account。",
        "supabase": "在 Dashboard 選註冊（Sign up）或畫面提供的可信登入方式；這是管理平台帳號，不是網站會員註冊。",
    }[provider]
    end={
        "google": "確認 Google Account 首頁已登入。既有個人帳戶即可使用 Sheets/Apps Script；先不訂 Workspace、不建立 Cloud project。",
        "cloudflare": "在帳戶管理頁核對登入帳戶及免費方案；先不要開 Workers & Pages，首次進入可能建立子網域，也不用購買網域。",
        "supabase": "登入 Dashboard 後查看組織清單；若首次流程要求建立組織，先確認費用與範圍，尚未授權不按建立專案。",
    }[provider]
    return [
        step("在瀏覽器開啟官方入口 "+url,"應看到 "+name+" 的註冊或登入頁。",
             "網址非官方、連結失效或頁面不一致時停下。"),
        step(first,"進入帳戶填寫或可信身分供應者登入流程。",
             "若已有帳號直接登入，不重複註冊；機構帳戶受政策限制先向管理者確認。"),
        step("依官方畫面完成必要欄位、電子郵件/手機驗證、條款與人機驗證；密碼及驗證碼由你在官方頁輸入。",
             "看到驗證完成提示或進入管理首頁。","若要求付款、信用卡或不明授權，停止並回報非敏感畫面；不自行升級。"),
        step("在 "+home+" 核對目前登入的帳戶，依官方安全頁啟用可用的雙重驗證，復原碼自己離線保管。",
             "帳戶頁識別正確，必要安全檢查完成。","登入或復原遇阻只在官方頁處理，不傳任何憑證。"),
        step(end,"確認登入與安全狀態；只回覆「完成」或非敏感錯誤文字。",
             "若需建立新資源或變更計費方案，先回到聊天確認範圍。"),
    ]

def connect(provider):
    name=PROVIDERS[provider][0]
    detail={
        "github":"若 GitHub 安裝畫面提供 Only select repositories，限定核准的儲存庫；尚無目標 repo 就先確認建立範圍，不選全部私有 repo。",
        "google":"只選必要 Google 服務；若 Google 要求核准所選服務的全部必要權限，先縮小服務選擇而不是假裝部分授權有效。Drive/Sheets 不等於 Apps Script 部署。",
        "cloudflare":"核對正確 Cloudflare 帳戶與要求的 Workers/D1 存取權限；不另建廣泛 API Token，也不在此開 Workers & Pages。",
        "supabase":"核對正確組織及要求的管理權限；連接不建立 project，不分享 API key、service role 或資料庫密碼。",
    }[provider]
    return [
        step("回到 ChatGPT，確認目前登入正確 ChatGPT 帳號與工作空間；開個人選單 → Settings（設定）→ Plugins（外掛），部分介面顯示 Apps。",
             "看到外掛/應用程式管理或目錄。","看不到時先查計畫、地區、裝置及工作空間管理政策，不要求升級。"),
        step("搜尋 "+name.split("（")[0]+"；使用已查得的官方連接選項。如有 Install plugin，先看介紹再由你確認安裝。",
             "顯示正確服務，或已有連接設定。","找不到或被管理者停用時，不裝來路不明的替代外掛；回報狀態。"),
        step("若顯示 Connect／連接，點入官方登入流程；選你有權操作且符合本專案的帳號。",
             "看到供應商官方登入或權限審閱畫面。","若自動選錯帳號，先返回，不允許錯帳號；可用支援的 Connect another account。"),
        step(detail,"權限、目標帳戶、資源範圍可理解且符合本次需求。",
             "若必須接受超出需求的權限、付費或機構審批，停止；改評估更窄的路徑。"),
        step("由你閱讀並確認必要授權，返回 ChatGPT 的 Plugins/Apps 連接頁。",
             "看到已連接的正確帳戶；這只是使用者操作結果，不等於 Agent 已驗證。",
             "若拒絕或授權失敗，不重複按同一按鈕；提供遮蔽後的錯誤文字。"),
        step("回到對話，只回報「已連接」；Agent 接著用實際唯讀工具查身份、目標 metadata、授權能力與方案。",
             "取得真正唯讀結果並核對目標後，才可進入後續 C1；部署仍另授權。",
             "若唯讀失敗，定位帳號、scope、工具限制或服務狀態，不叫你重註冊。"),
    ]

def _out(status, **kwargs):
    return {"status":status, "advisory_only":True,
            "account_verified_by_router":False,
            "connection_verified_by_router":False,
            "c1_pass":False, "external_write_permitted":False,
            "deployment_permitted":False, "payment_permitted":False,
            "never_request_secrets":True, "newbie_default":True,
            "show_one_relevant_step_at_a_time":True,
            "resume_from_confirmed_step":True, **kwargs}

def route(profile):
    """Only selected providers; caller reports state, not authenticated evidence.

    Exact enum fields only, no account identifiers/secrets/free text.
    Never infer signup or connection requirements before selecting a stack.
    """
    if type(profile) is not dict or set(profile)!={"required","states"}:
        return _out("INVALID_PROFILE")
    required,states=profile["required"],profile["states"]
    if (type(required) is not list or len(required)>len(PROVIDERS)
        or any(type(p) is not str or p not in PROVIDERS for p in required)
        or len(set(required))!=len(required) or type(states) is not dict
        or set(states)!=set(required)):
        return _out("INVALID_PROFILE")
    for p in required:
        s=states[p]
        if (type(s) is not dict or set(s)!=set(ENUMS)
            or any(type(s[k]) is not str or s[k] not in vs for k,vs in ENUMS.items())):
            return _out("INVALID_PROFILE")
    # No stack selected yet: continue intake, don't demand any account.
    if not required:
        return _out("SELECT_REQUIRED_SERVICES_FIRST")
    # An observation explicitly reports wrong account or target, never proceed.
    for p in required:
        s=states[p]
        if s["connection"]=="wrong_account" or s["readback"]=="wrong_target":
            return _out("WRONG_ACCOUNT_OR_TARGET_HOLD",provider=p,
                        next_action="停止讀寫；核對 ChatGPT 工作空間及 Plugins/Apps 的連接帳戶；若可用，選擇正確帳戶或增加指定帳戶。不得重用錯誤資源；重做唯讀驗證。")
    for p in required:
        s=states[p]; name=PROVIDERS[p][0]
        extra={"provider":p,"sources":SOURCES+PROVIDER_SOURCES[p]}
        def go(status, action, **kw):
            return _out(status, next_action=action, **extra, **kw)
        if s["connection"]=="denied":
            return go("PERMISSION_DENIED_HOLD","先確認是使用者拒絕、機構管理限制、或供應商權限不足；尊重拒絕，改提較窄授權或替代架構，不反覆要求授權。")
        if s["account"]=="missing" and s["connection"]=="connected":
            return go("STATE_CONFLICT_HOLD","帳號不存在與已連接矛盾，先唯讀核對，不重新註冊。")
        if s["account"]=="unknown":
            return go("CHECK_ACCOUNT","先用已可用的連接工具查非敏感身份；無證據時只問是否已有可用的 "+name+" 帳號。")
        if s["account"]=="missing":
            return go("GUIDE_SIGNUP","帶領使用者在官方網站註冊，不代填密碼或驗證，不要求付款。",steps=signup(p))
        if s["account"]=="security_pending":
            return go("GUIDE_ACCOUNT_SECURITY","在 "+PROVIDERS[p][2]+" 的官方帳號安全設定完成必要驗證及可用雙重驗證；只回報安全狀態。")
        if s["connection"]=="unavailable":
            return go("ALTERNATIVE_PATH_HOLD","查外掛目錄、實際工作空間政策及安全官方 API/CLI；若無工具則提出最少人工路徑或可編輯替代架構，不承諾代辦。")
        if s["connection"]=="unknown":
            return go("DISCOVER_CONNECTION","先查可用工具及外掛；若已連接，只核對而不要求重新安裝。")
        if s["connection"]=="missing":
            return go("GUIDE_CONNECT","確認外掛實際可用後才帶領使用者連接正確帳戶。",steps=connect(p))
        if s["readback"]=="failed":
            return go("READBACK_FAILED_HOLD","用非敏感錯誤碼辨識未授權、連線、帳戶或工具限制；只修必要步驟，再唯讀重驗，不盲目重新連接。")
        if s["readback"]!="verified":
            return go("VERIFY_CONNECTION_READONLY","Agent 實際讀身份與指定資源 metadata；不查資料內容、不建立資源。")
        if s["capability"]=="unsupported":
            return go("CAPABILITY_GAP_HOLD","連接已存在但所需操作不支援；核官方替代路徑、最小人工操作或重新選型，不把讀權當寫權。")
        if s["capability"]=="unknown":
            return go("VERIFY_REQUIRED_CAPABILITY","比對本任務需要的操作、實際工具、scope 及限制；不以 schema 宣稱寫入成功。")
        if s["cost"]=="not_free_or_uncertain":
            return go("COST_HOLD","停止任何新增資源、付款或升級；提供免費替代方案或重新確認預算。")
        if s["cost"]=="unknown":
            return go("VERIFY_PLAN_AND_COST","核當前帳戶方案、剩餘配額和所需資源的實際價格；不可用公開免費方案代替。")
    return _out("READY_FOR_C1_EVIDENCE_REVIEW", required=list(required),
                next_action="逐一回讀本次真實且適用的帳號/目標/工具/方案證據；此路由結果不是完成證明或部署授權。未經確認不得建立資源。")

def _unique(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError("duplicate key")
        d[k]=v
    return d

def main():
    try:
        raw=sys.stdin.buffer.read(16385)
        if len(raw)>16384: raise ValueError("oversize")
        result=route(json.loads(raw.decode("utf-8"),object_pairs_hook=_unique))
    except (UnicodeError,ValueError,RecursionError):
        result=_out("INVALID_PROFILE")
    print(json.dumps(result,ensure_ascii=False))
    return 2 if result["status"]=="INVALID_PROFILE" else 0

if __name__=="__main__":
    raise SystemExit(main())
