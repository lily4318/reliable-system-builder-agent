// Synthetic advisory-only GAS diagnostic training, not a live API or deployment tool.
function lab() {
  // Advisory training oracle. All inputs are synthetic observations, not live evidence.
  const base={target:"A",observedTarget:"A",unknownWrite:false,source:"new",head:"new",versionContent:"new",expectedVersion:8,activeVersion:8,urlDeployment:"D",expectedDeployment:"D",entry:"exec",access:"ANYONE",expectedAccess:"ANYONE",executeAs:"USER_DEPLOYING",expectedExecuteAs:"USER_DEPLOYING",unexpectedAccess:false,normal:"ok",clean:"ok",sameActor:true,cleanComparable:true,actorTested:true,identityRequired:true,visitor:"known",effective:"owner",roleNegative:"denied",rpc:"ok",resource:"ok",oauth:"ok",runtimeMarker:"new"};
  function diagnose(x,strict){
    if(!strict){
      if(x.normal==="ok"&&x.runtimeMarker===x.source)return "OBSERVATIONS_CONSISTENT";
      if(x.clean==="ok")return "SESSION_SUSPECT";
      return "CHECK_RUNTIME";
    }
    if(!x.target||x.target!==x.observedTarget||x.urlDeployment!==x.expectedDeployment||x.entry!=="exec")return "VERIFY_TARGET";
    if(x.unknownWrite===true)return "READ_ONLY_RECONCILE";
    if(x.unexpectedAccess===true||x.roleNegative==="allowed")return "SECURITY_HOLD";
    if(!["MYSELF","DOMAIN","ANYONE","ANYONE_ANONYMOUS"].includes(x.access)||!["USER_ACCESSING","USER_DEPLOYING"].includes(x.executeAs))return "MISSING_EVIDENCE";
    if(x.access!==x.expectedAccess||x.executeAs!==x.expectedExecuteAs)return "POLICY_MISMATCH";
    if(!x.source||!x.head||!x.versionContent||!Number.isSafeInteger(x.activeVersion)||!Number.isSafeInteger(x.expectedVersion))return "MISSING_EVIDENCE";
    if(x.head!==x.source)return "SOURCE_DRIFT";
    if(x.activeVersion!==x.expectedVersion||x.versionContent!==x.source)return "DEPLOYMENT_DRIFT";
    if(x.clean==="ok"&&x.normal==="fail"&&x.sameActor===true&&x.cleanComparable===true)return "SESSION_SUSPECT";
    if(!x.actorTested||x.clean!=="ok"||x.normal!=="ok")return "CHECK_ACCESS_CONTEXT";
    if(x.identityRequired===true&&x.visitor!=="known")return "IDENTITY_HOLD";
    if(x.oauth!=="ok")return "CHECK_SCOPES";
    if(x.rpc!=="ok")return "CHECK_RPC";
    if(x.resource!=="ok")return "CHECK_RESOURCE";
    if(x.runtimeMarker!==x.source)return "CHECK_RUNTIME";
    if(x.roleNegative!=="denied")return "MISSING_EVIDENCE";
    return "OBSERVATIONS_CONSISTENT";
  }
  // Deliberately fixed expected outcomes; not derived from implementation.
  const cases=[
    ["all consistent",{},"OBSERVATIONS_CONSISTENT"],
    ["wrong script",{observedTarget:"B"},"VERIFY_TARGET"],
    ["old deployment URL",{urlDeployment:"C"},"VERIFY_TARGET"],
    ["dev link",{entry:"dev"},"VERIFY_TARGET"],
    ["lost mutation response",{unknownWrite:true},"READ_ONLY_RECONCILE"],
    ["public admin",{roleNegative:"allowed"},"SECURITY_HOLD"],
    ["unexpected anonymous admission",{unexpectedAccess:true},"SECURITY_HOLD"],
    ["anonymous vs signed-in",{access:"ANYONE_ANONYMOUS"},"POLICY_MISMATCH"],
    ["different execution principal",{executeAs:"USER_ACCESSING"},"POLICY_MISMATCH"],
    ["unknown access",{access:null},"MISSING_EVIDENCE"],
    ["head drift",{head:"old"},"SOURCE_DRIFT"],
    ["old active version",{activeVersion:7},"DEPLOYMENT_DRIFT"],
    ["content mismatch same version",{versionContent:"old"},"DEPLOYMENT_DRIFT"],
    ["missing fixed version content",{versionContent:null},"MISSING_EVIDENCE"],
    ["clean same actor works",{normal:"fail"},"SESSION_SUSPECT"],
    ["clean different actor works",{normal:"fail",sameActor:false},"CHECK_ACCESS_CONTEXT"],
    ["clean context incomparable",{normal:"fail",cleanComparable:false},"CHECK_ACCESS_CONTEXT"],
    ["owner only tested",{actorTested:false},"CHECK_ACCESS_CONTEXT"],
    ["both fail",{normal:"fail",clean:"fail"},"CHECK_ACCESS_CONTEXT"],
    ["blank active user but effective owner",{visitor:"blank"},"IDENTITY_HOLD"],
    ["partial OAuth grant",{oauth:"missing"},"CHECK_SCOPES"],
    ["visible page RPC failure",{rpc:"fail"},"CHECK_RPC"],
    ["backend file denied",{resource:"denied"},"CHECK_RESOURCE"],
    ["runtime build mismatch",{runtimeMarker:"old"},"CHECK_RUNTIME"],
    ["no negative role test",{roleNegative:"untested"},"MISSING_EVIDENCE"],
    ["unknown write precedence",{unknownWrite:true,normal:"fail",head:"old"},"READ_ONLY_RECONCILE"],
    ["security before cookie",{unexpectedAccess:true,normal:"fail"},"SECURITY_HOLD"],
    ["anonymous public nonprivileged no identity",{access:"ANYONE_ANONYMOUS",expectedAccess:"ANYONE_ANONYMOUS",identityRequired:false,visitor:"blank"},"OBSERVATIONS_CONSISTENT"]
  ];
  const results={};
  for(const strict of [false,true]){
    results[strict?"strict":"legacy"]=cases.map(([name,delta,expected])=>{
      const x={...base,...delta},before=JSON.stringify(x);
      const actual=diagnose(x,strict);
      return {name,expected,actual,pass:actual===expected&&JSON.stringify(x)===before};
    });
  }
  return results;
}
const result=lab();
console.log(JSON.stringify(result,null,2));
if(result.strict.some(x=>!x.pass)||result.legacy.every(x=>x.pass))process.exitCode=1;
