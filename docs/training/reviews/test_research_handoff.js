// Synthetic research-dictionary handoff lab. No real data, network, deployment or production permissions.
function runLab() {
  const assert=(b,msg)=>{if(!b)throw Error(msg)};
  const eq=(a,b,msg)=>assert(JSON.stringify(a)===JSON.stringify(b),msg);
  const clone=x=>JSON.parse(JSON.stringify(x));
  // This intentionally tiny canonical encoding handles only the lab's fixed JSON domain.
  const canonical=x=>x===null||typeof x!=="object"?JSON.stringify(x):Array.isArray(x)?"["+x.map(canonical).join(",")+"]":"{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+canonical(x[k])).join(",")+"}";
  const v1={id:"R-LATENCY",revision:1,field:"latency",unit:"ms",min:0,max:5000,missing:"null-only",format:"int"};
  const v2={...v1,revision:2,unit:"10ms",max:500,missing:"null-only"};
  const decision={id:"SYNTHETIC-D2",scope:"local-synthetic-only",dictionary:v2,excluded:["live-intake","external-deployment","automatic-migration"]};
  const roles=["architecture","implementation","qa"];
  const artifact=(kind,d)=>({kind,requirement:d.id,dictionary:clone(d),status:"PASS"});
  const context=()=>({decision:clone(decision),artifacts:roles.map(k=>artifact(k,v2)),source:{dictionary:clone(v2),revision:7,rows:[{id:"P001",latency:150},{id:"P002",latency:null},{id:"P003",latency:0}]}});
  function ready(c,strict) {
    const d=decision.dictionary;
    if(!strict)return c.artifacts.length===3&&c.artifacts.every(x=>x.status==="PASS"&&x.requirement===d.id);
    return canonical(c.decision)===canonical(decision)&&c.artifacts.length===roles.length&&roles.every(k=>{
      const matches=c.artifacts.filter(x=>x.kind===k);
      return matches.length===1&&matches[0].status==="PASS"&&matches[0].requirement===d.id&&canonical(matches[0].dictionary)===canonical(d);
    })&&canonical(c.source.dictionary)===canonical(d);
  }
  function exportData(c,strict) {
    if(!ready(c,strict))throw Error("STALE_OR_UNAPPROVED_HANDOFF");
    const d=c.artifacts.find(x=>x.kind==="implementation").dictionary;
    const rows=clone(c.source.rows).sort((a,b)=>a.id.localeCompare(b.id));
    if(!Number.isSafeInteger(c.source.revision)||c.source.revision<0)throw Error("BAD_REVISION");
    const seen=new Set();
    for(const r of rows){
      if(!/^P[0-9]{3}$/.test(r.id)||seen.has(r.id)||!(r.latency===null||(Number.isInteger(r.latency)&&r.latency>=d.min&&r.latency<=d.max)))throw Error("BAD_ROW");
      seen.add(r.id);
    }
    const csv="id,latency,status\n"+rows.map(r=>`${r.id},${r.latency===null?"":r.latency},${r.latency===null?"missing":"observed"}\n`).join("");
    return {manifest:{dictionary:clone(d),decision_id:c.decision.id,source_revision:c.source.revision,row_count:rows.length},csv};
  }
  // Independent parsing route and literal expectations, not generated from the writer.
  function qaExport(bundle,expected) {
    if(canonical(bundle.manifest)!==canonical(expected.manifest))throw Error("MANIFEST_MISMATCH");
    const lines=bundle.csv.split("\n");
    if(lines.shift()!=="id,latency,status"||lines.pop()!=="")throw Error("CSV_FORMAT");
    const values=lines.map(line=>{
      const m=/^(P[0-9]{3}),([0-9]*),(missing|observed)$/.exec(line);
      if(!m||((m[2]==="")!==(m[3]==="missing")))throw Error("CSV_VALUE");
      return [m[1],m[2]===""?null:Number(m[2]),m[3]];
    });
    eq(values,expected.rows,"ORACLE_MISMATCH");
  }
  const expected={manifest:{dictionary:{id:"R-LATENCY",revision:2,field:"latency",unit:"10ms",min:0,max:500,missing:"null-only",format:"int"},decision_id:"SYNTHETIC-D2",source_revision:7,row_count:3},rows:[["P001",150,"observed"],["P002",null,"missing"],["P003",0,"observed"]]};
  function reject(c,strict){const before=canonical(c);let rejected=false;try{exportData(c,strict)}catch(e){rejected=true}assert(rejected,"unsafe handoff accepted");eq(canonical(c),before,"mutation on rejection")}
  const cases={
    current_contract(s){const c=context();const b=exportData(c,s);qaExport(b,expected);eq(exportData(c,s),b,"non-repeatable export")},
    stale_architecture(s){const c=context();c.artifacts[0]=artifact("architecture",v1);reject(c,s)},
    stale_developer(s){const c=context();c.artifacts[1]=artifact("implementation",v1);reject(c,s)},
    stale_qa(s){const c=context();c.artifacts[2]=artifact("qa",v1);reject(c,s)},
    same_revision_changed_unit(s){const c=context();c.artifacts[1].dictionary.unit="ms";reject(c,s)},
    old_source_not_auto_converted(s){const c=context();c.source.dictionary=clone(v1);reject(c,s)},
    duplicate_role(s){const c=context();c.artifacts[2]=clone(c.artifacts[0]);reject(c,s)},
    modified_scope(s){const c=context();c.decision.excluded=[];reject(c,s)},
    missing_semantics_changed(s){const c=context();c.artifacts[2].dictionary.missing="zero";reject(c,s)},
    empty_export_has_manifest(s){const c=context();c.source.rows=[];qaExport(exportData(c,s),{manifest:{...expected.manifest,row_count:0},rows:[]})},
    valid_looking_wrong_values(s){const b=exportData(context(),s);b.csv=b.csv.replace("P001,150,","P001,15,");let denied=false;try{qaExport(b,expected)}catch(e){denied=true}assert(denied,"wrong value accepted")},
    bounds_and_zero(s){const c=context();c.source.rows[0].latency=501;reject(c,s)},
    no_implicit_migration(s){const c=context();c.source.dictionary=clone(v1);c.source.rows[0].latency=150;reject(c,s)}
  };
  const results={};
  for(const [mode,strict] of [["legacy",false],["strict",true]]){
    const log=[];
    for(const [name,test] of Object.entries(cases)){try{test(strict);log.push({name,pass:true})}catch(e){log.push({name,pass:false,error:e.message})}}
    results[mode]=log;
  }
  return results;
}
const result=runLab();
console.log(JSON.stringify(result,null,2));
if(result.strict.some(x=>!x.pass)||result.legacy.every(x=>x.pass))process.exitCode=1;
