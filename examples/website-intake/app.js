"use strict";
const $=id=>document.getElementById(id);
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
let boot, spec=null, revision=0, confirmed=false, pendingImport=null, importRevision=0;
let decisions=new Map(), fields=new Map();
const status=text=>{$("status").textContent=text};
const reset=()=>{
  revision++;spec=null;confirmed=false;decisions.clear();
  $("reviews").replaceChildren();$("preview").replaceChildren();
  $("finalize").disabled=true;$("export").disabled=true;$("final-status").textContent="";
};
function progress(){
  const count=[...fields.values()].filter(x=>x.value.trim()).length;
  $("progress").textContent="已填寫 "+count+" / 13 題（允許待確認）";
}
function invalidate(){reset();progress();status("答案已修改；請重新產生規格。舊確認已清除。");}
function validAnswers(a){
  const keys=boot.questions.map(q=>q.id);
  return a && typeof a==="object" && !Array.isArray(a) &&
    Object.entries(a).every(([k,v])=>keys.includes(k)&&(v===null||(typeof v==="string"&&v.length<=2000)));
}
function load(a){
  if(!validAnswers(a))throw Error("回答格式不正確");
  fields.forEach((n,k)=>{n.value=a[k]??""});
  invalidate();
}
function currentAnswers(){return Object.fromEntries([...fields].map(([k,n])=>[k,n.value]));}
function cancelFinal(){confirmed=false;$("export").disabled=true;$("final-status").textContent="尚未確認整份草稿。";}
function createReview(item){
  const state={choice:null,text:"",confirmed:false};
  decisions.set(item.id,state);
  const card=el("article");card.className="review";card.dataset.item=item.id;
  card.append(el("h3",item.question));
  const controls=el("div");controls.className="choices";controls.setAttribute("role","group");controls.setAttribute("aria-label",item.question);
  const label=el("label","可編輯的確認文字");label.htmlFor=item.id+"-text";
  const area=el("textarea");area.id=item.id+"-text";area.maxLength=3000;area.disabled=true;
  const save=el("button","確認本項文字");save.disabled=true;save.className="confirm-item";
  const cancel=el("button","取消本項選擇");cancel.className="cancel-item";cancel.disabled=true;
  const msg=el("p","待選擇");msg.className="item-status";msg.setAttribute("role","status");
  const change=()=>{state.confirmed=false;cancelFinal();msg.textContent="尚未確認；可繼續修改。";save.disabled=!state.choice||!state.text.trim();cancel.disabled=!state.choice;renderPreview();};
  for(const choice of item.choices){
    const lab=el("label"),radio=el("input");radio.type="radio";radio.name=item.id;radio.value=choice.id;
    radio.addEventListener("change",()=>{state.choice=choice.id;state.text=choice.proposed_text;area.disabled=false;area.value=state.text;change();});
    lab.append(radio,document.createTextNode(" "+choice.label));controls.append(lab);
  }
  area.addEventListener("input",()=>{state.text=area.value;change()});
  save.addEventListener("click",()=>{if(state.choice&&state.text.trim()){state.confirmed=true;save.disabled=true;msg.textContent="本項文字已確認（未傳送）";cancelFinal();renderPreview()}});
  cancel.addEventListener("click",()=>{controls.querySelectorAll("input").forEach(r=>r.checked=false);state.choice=null;state.text="";area.value="";area.disabled=true;change();msg.textContent="待選擇";});
  card.append(controls,label,area,save,cancel,msg);return card;
}
const headings={sections:"13 題使用者原始需求",functional_spec:"功能規格",nonfunctional_spec:"非功能規格",requirement_traceability:"需求追溯與驗收",architecture_design_draft:"架構草稿",delivery_plan_draft:"交付與維運計畫",test_acceptance_plan:"測試及驗收",unanswered_questions:"尚待確認事項",scope_limits:"範圍限制",approval_steps:"確認程序"};
const labels={purpose:"網站目的",user_roles:"使用者與角色",flows:"核心流程",pages:"頁面",authentication_authorization:"登入與權限",data_forms:"資料與表單",state_booking_rules:"預約及狀態規則",notifications:"通知",administration:"後台",privacy_approval:"隱私與核准",infrastructure_integrations:"整合與基礎設施",responsive_accessibility_localization:"介面與無障礙",performance_availability_and_security:"效能、可用性及安全",release_acceptance_maintenance:"上線、驗收及維護",ui_pages_from_user:"頁面",user_flow_from_user:"流程",service_modules:"服務模組",data_storage_and_lifecycle:"儲存及生命週期",existing_infrastructure_from_user:"現有系統",design_decision_status:"設計狀態",mvp_priority_from_user:"MVP 優先序",work_packages:"工作包",deployment_status:"部署狀態",live_intake_status:"收件狀態"};
function renderValue(parent,v){
  if(Array.isArray(v)){const ul=el("ul");for(const x of v){const li=el("li");renderValue(li,x);ul.append(li)}parent.append(ul);}
  else if(v!==null&&typeof v==="object"){const dl=el("dl");for(const [k,x] of Object.entries(v)){dl.append(el("dt",labels[k]||k));const dd=el("dd");renderValue(dd,x);dl.append(dd)}parent.append(dl)}
  else parent.append(document.createTextNode(String(v??"待確認")));
}
function renderPreview(){
  const p=$("preview");p.replaceChildren();if(!spec)return;
  for(const [key,title] of Object.entries(headings)){p.append(el("h3",title));renderValue(p,spec[key])}
  p.append(el("h3","推導需求與逐項決策"));
  if(!decisions.size)p.append(el("p","目前無推導需求。"));
  for(const item of spec.inferred_requirement_review_items){
    const d=decisions.get(item.id);
    const suggestion=spec.inferred_requirements_unconfirmed.find(x=>x.title===item.question);
    p.append(el("h4",item.question),el("p",suggestion?.proposal||""),
      el("p","來源題目："+(suggestion?.basis||[]).map(k=>boot.questions.find(q=>q.id===k)?.number||k).join("、")));
    p.append(el("p",d.confirmed?"本機已確認："+({accept:"接受",modify:"修改",reject:"不採用"}[d.choice])+" — "+d.text:"待確認"+(d.choice?"（編輯中）":"")));
  }
  $("finalize").disabled=![...decisions.values()].every(x=>x.confirmed);
}
function exportObject(){
  if(!spec||!confirmed||![...decisions.values()].every(x=>x.confirmed))throw Error("確認尚未完成");
  return {kind:"local_reviewed_website_draft",answers:currentAnswers(),specification_draft:spec,
    local_decisions:spec.inferred_requirement_review_items.map(item=>({id:item.id,title:item.question,choice:decisions.get(item.id).choice,text:decisions.get(item.id).text,local_text_confirmed:true})),
    local_document_review_confirmed:true,real_agent_executed:false,specification_approved:false,write_authorized:false,deployment_authorized:false,live_intake_authorized:false};
}
async function generate(){
  reset();const epoch=revision;
  $("generate").disabled=true;status("本機產生中…");
  try{
    const response=await fetch("/draft",{method:"POST",headers:{"Content-Type":"application/json","X-Local-Token":boot.token},body:JSON.stringify(currentAnswers())});
    if(!response.ok)throw Error("無法產生規格");
    const result=await response.json();
    if(epoch!==revision)return;
    spec=result;
    $("reviews").replaceChildren(...spec.inferred_requirement_review_items.map(createReview));
    if(!decisions.size)$("reviews").append(el("p","目前無推導需求；仍需檢視整份規格。"));
    renderPreview();status("草稿已產生；逐項確認後，才可確認整份草稿。");
  }catch(e){if(epoch===revision)status("產生失敗：請檢查回答格式與本機程式是否仍在執行。");}
  finally{$("generate").disabled=false;}
}
async function init(){
  boot=await (await fetch("/bootstrap")).json();
  for(const q of boot.questions){
    const wrapper=el("div");wrapper.className="question";
    const label=el("label",q.number+"．"+q.prompt);label.htmlFor="answer-"+q.id;
    const n=el("textarea");n.id="answer-"+q.id;n.maxLength=2000;n.placeholder="輸入回答，或留空待確認";
    n.addEventListener("input",invalidate);
    const choice=el("select");choice.setAttribute("aria-label",q.prompt+" 常用回答");
    for(const [value,text] of [["","常用回答（可再修改）"],["待確認","待確認"],["不適用","不適用"],["不需要","不需要"]]){const o=el("option",text);o.value=value;choice.append(o)}
    choice.addEventListener("change",()=>{if(choice.value){n.value=choice.value;invalidate();choice.value=""}});
    fields.set(q.id,n);wrapper.append(label,choice,n);$("questions").append(wrapper);
  }
  for(const c of boot.examples){const o=el("option",c.id+"｜"+c.title);o.value=c.id;$("example").append(o)}
  $("load-example").addEventListener("click",()=>load(boot.examples.find(c=>c.id===$("example").value).answers));
  $("import-file").addEventListener("change",async()=>{
    const epoch=++importRevision;
    pendingImport=null;$("apply-import").disabled=true;$("import-preview").hidden=true;
    const f=$("import-file").files[0];if(!f)return;
    try{if(f.size>65536)throw Error();const a=JSON.parse((await f.text()).replace(/^\uFEFF/,""));if(!validAnswers(a))throw Error();if(epoch!==importRevision)return;pendingImport=a;$("import-preview").textContent=JSON.stringify(a,null,2);$("import-preview").hidden=false;$("apply-import").disabled=false;}
    catch(e){if(epoch===importRevision)status("匯入檔案格式錯誤；原答案未更動。")}
  });
  $("apply-import").addEventListener("click",()=>{if(pendingImport){load(pendingImport);pendingImport=null;$("apply-import").disabled=true;$("import-preview").hidden=true;}});
  $("generate").addEventListener("click",generate);
  $("finalize").addEventListener("click",()=>{if(spec&&[...decisions.values()].every(d=>d.confirmed)){confirmed=true;$("export").disabled=false;$("final-status").textContent="本機草稿已確認；未傳送、未部署。"}});
  $("export").addEventListener("click",()=>{const data=exportObject();const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));const a=el("a");a.href=url;a.download="website-reviewed-draft.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  load(boot.prefill);$("load-example").disabled=false;$("generate").disabled=false;status("已就緒；請核對預填資料或填寫 13 題。");
  if(boot.test_mode)window.intakeTest={exportObject,currentAnswers,examples:boot.examples,generate,
    report:result=>fetch("/test-result",{method:"POST",headers:{"Content-Type":"application/json","X-Local-Token":boot.token},body:JSON.stringify(result)})};
}
init().catch(()=>status("無法載入本機介面，請重新啟動程式。"));
