"use strict";
const $=id=>document.getElementById(id);
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
const state={actor:null,csrf:"",page:1,total:0,pending:null,pendingActor:null,busy:false,view:"public",epoch:0,requests:0};
const pendingKey="editorial-pending-local-action-v1";
const labels={DRAFT:"草稿",SUBMITTED:"等待審核",RETURNED:"退回修改",APPROVED:"審核通過",PUBLISHED:"已發布",SUPERSEDED:"舊發布版",WITHDRAWN:"已下架"};
const errors={FORBIDDEN:"權限不足或來源不符",AUTH_REQUIRED:"登入已失效，請重新登入",INVALID_LOGIN:"登入資料錯誤",INVALID_INPUT:"資料格式或長度不正確",STALE:"版本已變更，請重新讀取",INVALID_STATE:"目前狀態不允許操作",OPEN_REVISION:"已有未完成修訂稿",TOKEN_CONFLICT:"操作識別碼衝突",NOT_FOUND:"找不到資料"};
const msg=t=>$("status").textContent=t;
const randomToken=()=>Array.from(crypto.getRandomValues(new Uint8Array(16)),x=>x.toString(16).padStart(2,"0")).join("");
async function request(path,data){
  const opt={cache:"no-store"};
  if(data!==undefined)Object.assign(opt,{method:"POST",headers:{"Content-Type":"application/json","X-CSRF-Token":state.csrf},body:JSON.stringify(data)});
  state.requests++;document.querySelector("main").setAttribute("aria-busy","true");
  try{const r=await fetch(path,opt);const v=await r.json();return {status:r.status,v}}
  finally{state.requests--;document.querySelector("main").setAttribute("aria-busy",String(state.requests>0))}
}
async function get(path){
  const {status,v}=await request(path);
  if(status!==200)throw Object.assign(Error(errors[v.error]||"讀取失敗"),{status});
  return v;
}
function show(panel){
  state.view=panel;state.epoch++;
  for(const p of ["public","login","work"])$(p+"-panel").hidden=p!==panel;
  $("work-nav").hidden=!state.actor;$("logout").hidden=!state.actor;
  $("login-nav").hidden=!!state.actor;
}
function actorData(data){
  state.actor=data.actor;state.csrf=data.csrf;
  $("work-nav").hidden=!state.actor;$("logout").hidden=!state.actor;$("login-nav").hidden=!!state.actor;
  $("create-panel").hidden=state.actor?.role!=="author";
  $("reconcile").disabled=!state.pending||state.actor?.username!==state.pendingActor;
}
async function list(){
  const epoch=++state.epoch;
  const query=new URLSearchParams({q:$("search").value,category:$("filter").value,page:String(state.page)});
  const result=await get("/api/articles?"+query);
  if(epoch!==state.epoch||state.view!=="public")return;
  state.total=result.total;
  $("articles").replaceChildren();
  if(!result.items.length)$("articles").append(el("p","沒有符合的文章。"));
  for(const item of result.items){
    const card=el("article");card.className="article-card";
    const link=el("a",item.title);link.href="/?article="+item.id;link.addEventListener("click",e=>{e.preventDefault();location.hash="article-"+item.id;safe(()=>detail(item.id))});
    card.append(el("p",item.category),link);$("articles").append(card);
  }
  $("page-label").textContent="第 "+state.page+" 頁 / 共 "+result.total+" 篇";
  $("prev").disabled=state.page<=1;$("next").disabled=state.page*20>=result.total;
}
async function detail(id){
  const epoch=++state.epoch;
  $("article-detail").hidden=true;$("detail-title").textContent="";$("detail-body").textContent="";$("detail-category").textContent="";
  const article=await get("/api/article?id="+encodeURIComponent(id));
  if(epoch!==state.epoch||state.view!=="public")return;
  $("detail-title").textContent=article.title;$("detail-category").textContent=article.category;
  $("detail-body").textContent=article.body;$("article-detail").hidden=false;
}
function field(tag,id,label,text,max){
  const l=el("label",label);l.htmlFor=id;
  const n=el(tag);n.id=id;n.value=text;n.required=true;if(max)n.maxLength=max;
  return [l,n];
}
function actionButton(container,title,op,row,extra=()=>({})){
  const b=el("button",title);b.type="button";b.dataset.op=op;
  b.addEventListener("click",()=>safe(()=>mutate({op,article_id:row.article_id,revision_id:row.id,expected:row.version,...extra()})));
  container.append(b);return b;
}
function card(row,all){
  const box=el("article");box.className="revision";box.dataset.revision=String(row.id);
  box.append(el("h3",row.title),el("p","作者 "+row.owner+" · 第 "+row.revision_no+" 版 · "+labels[row.status]),el("p",row.category));
  const content=el("p",row.body);content.className="body-text";box.append(content);
  if(row.reason)box.append(el("p","退回理由："+row.reason));
  const controls=el("div");controls.className="controls";
  if(state.actor.role==="author"){
    if(["DRAFT","RETURNED"].includes(row.status)){
      const form=el("form");
      const [tl,title]=field("input","title-"+row.id,"標題",row.title,120);
      const cat=el("select");cat.id="category-"+row.id;for(const c of ["生活","文化","科技"]){const o=el("option",c);o.value=c;cat.append(o)}cat.value=row.category;
      const cl=el("label","分類");cl.htmlFor=cat.id;
      const [bl,body]=field("textarea","body-"+row.id,"內文",row.body,10000);
      const save=el("button","儲存修改");save.dataset.op="edit";
      form.append(tl,title,cl,cat,bl,body,save);
      form.addEventListener("submit",e=>{e.preventDefault();safe(()=>mutate({op:"edit",article_id:row.article_id,revision_id:row.id,expected:row.version,title:title.value,category:cat.value,body:body.value}))});
      box.append(form);
      if(row.status==="DRAFT")actionButton(controls,"提交審核","submit",row);
    }
    const related=all.filter(r=>r.article_id===row.article_id);
    if(["PUBLISHED","WITHDRAWN"].includes(row.status)&&row.revision_no===Math.max(...related.map(r=>r.revision_no))&&!related.some(r=>["DRAFT","RETURNED","SUBMITTED","APPROVED"].includes(r.status)))
      actionButton(controls,"建立修訂稿","clone",row);
  }else{
    if(row.status==="SUBMITTED"){
      actionButton(controls,"核准","approve",row);
      const form=el("form"),[lab,reason]=field("textarea","reason-"+row.id,"退回理由","",500),b=el("button","退回修改");
      b.dataset.op="return";form.append(lab,reason,b);
      form.addEventListener("submit",e=>{e.preventDefault();safe(()=>mutate({op:"return",article_id:row.article_id,revision_id:row.id,expected:row.version,reason:reason.value}))});
      box.append(form);
    }
    if(row.status==="APPROVED")actionButton(controls,"發布文章","publish",row);
    if(row.status==="PUBLISHED")actionButton(controls,"下架文章","withdraw",row);
  }
  box.append(controls);return box;
}
async function work(){
  const epoch=++state.epoch;
  const data=await get("/api/workspace");
  if(epoch!==state.epoch||state.view!=="work")return;
  $("workspace-title").textContent=(data.actor.role==="author"?"作者":"編輯")+"工作台｜"+data.actor.username;
  $("revisions").replaceChildren(...data.revisions.map(r=>card(r,data.revisions)));
  if(!data.revisions.length)$("revisions").append(el("p","目前沒有稿件。"));
  $("events").replaceChildren(...data.events.map(e=>el("p",e.actor+" · 文章 "+e.article_id+" / 稿件 "+e.revision_id+" / 版本 "+e.revision_version+" · "+e.action+" · "+(labels[e.before_state]||"—")+" → "+labels[e.after_state]+" · "+new Date(e.at*1000).toLocaleString("zh-TW")+(e.review_reason?" · 退回理由："+e.review_reason:""))));
}
function retainPending(token,owner){
  state.pending=token;state.pendingActor=owner;
  try{sessionStorage.setItem(pendingKey,JSON.stringify({token,owner}))}catch(e){/* memory + visible action id fallback */}
}
function clearPending(){
  state.pending=null;state.pendingActor=null;$("reconcile-panel").hidden=true;
  try{sessionStorage.removeItem(pendingKey)}catch(e){}
}
function unknown(token,owner=state.pendingActor){
  retainPending(token,owner);$("reconcile-panel").hidden=false;
  $("reconcile").disabled=state.actor?.username!==owner;
  $("reconcile-status").textContent="操作識別碼："+token+"（僅可由原帳號查詢）";
  msg("操作結果不明；已暫停其他寫入。請以原帳號唯讀查詢收據。");
}
function restorePending(){
  try{const p=JSON.parse(sessionStorage.getItem(pendingKey)||"null");if(p&&typeof p.owner==="string"&&/^[a-f0-9]{32}$/.test(p.token))unknown(p.token,p.owner)}catch(e){}
}
async function mutate(payload){
  if(state.busy||state.pending){msg("先完成現有操作及收據查核。");return}
  state.busy=true;const token=randomToken();
  retainPending(token,state.actor.username);
  try{
    let response;
    try{response=await request("/api/action",{...payload,token})}
    catch(e){unknown(token);return}
    if(response.status>=500){unknown(token);return}
    const {v}=response;
    clearPending();
    if(v.ok){msg("操作完成。");if(payload.op==="create"){$("new-title").value="";$("new-body").value=""}}

    else msg(errors[v.code||v.error]||"操作遭拒絕。");
    await work();
  }finally{state.busy=false}
}
async function safe(fn){try{await fn()}catch(e){msg(e.message||"操作失敗");if(e.status===401){actorData(await get("/api/bootstrap"));$("revisions").replaceChildren();$("events").replaceChildren();show("login")}}}
async function init(){
  actorData(await get("/api/bootstrap"));show("public");await list();restorePending();
  const aid=new URLSearchParams(location.search).get("article")||location.hash.replace(/^#article-/,"");
  if(/^[1-9][0-9]*$/.test(aid))await safe(()=>detail(aid));
  $("public-nav").onclick=()=>safe(async()=>{show("public");$("article-detail").hidden=true;await list()});
  $("work-nav").onclick=()=>safe(async()=>{show("work");await work()});
  $("login-nav").onclick=()=>{show("login");$("username").focus()};
  $("login-form").onsubmit=e=>{e.preventDefault();safe(async()=>{
    if(state.busy)return;
    state.busy=true;
    try{
      const {status,v}=await request("/api/login",{username:$("username").value,password:$("password").value});
      $("password").value="";
      if(status!==200){msg(errors[v.error]||"登入失敗");return}
      actorData(v);show("work");msg(state.pending?"已登入；先核對原操作收據":"登入成功");await work();
    }finally{state.busy=false}
  })};
  $("logout").onclick=()=>safe(async()=>{
    if(state.busy){msg("請先完成現有操作。");return}
    state.busy=true;
    try{const {status,v}=await request("/api/logout",{});
      if(status!==200)throw Error("登出結果未確認，請重新讀取頁面。");
      actorData(v);$("revisions").replaceChildren();$("events").replaceChildren();$("new-title").value="";$("new-body").value="";show("public");msg("已登出");await list();
    }finally{state.busy=false}
  });
  $("create-form").onsubmit=e=>{e.preventDefault();safe(()=>mutate({op:"create",title:$("new-title").value,category:$("new-category").value,body:$("new-body").value}))};
  $("refresh").onclick=()=>safe(work);
  $("search-form").onsubmit=e=>{e.preventDefault();state.page=1;$("article-detail").hidden=true;safe(list)};
  $("prev").onclick=()=>{if(state.page>1){state.page--;$("article-detail").hidden=true;safe(list)}};
  $("next").onclick=()=>{if(state.page*20<state.total){state.page++;$("article-detail").hidden=true;safe(list)}};
  $("close-detail").onclick=()=>{$("article-detail").hidden=true;location.hash=""};
  $("reconcile").onclick=()=>safe(async()=>{
    if(!state.pending||state.actor?.username!==state.pendingActor)return;
    const r=await get("/api/receipt?token="+state.pending);
    $("reconcile-status").textContent=r.observed?"已查得結果："+r.result.code:"未觀測到收據；不得自動重送，先核對原資料與狀態。";
    if(r.observed){clearPending();msg("原操作結果："+r.result.code);await work()}
  });
  if(!state.pending)msg("本機刊物已就緒");
  if(document.querySelector('script[src="/browser-test.js"]'))window.editorialTest={report:r=>request("/test-result",r)};
}
init().catch(()=>msg("載入失敗；請確認本機服務。"));
