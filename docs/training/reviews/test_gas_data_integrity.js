// Synthetic Sheets provider fault model. Not real GAS/Sheets API or production code.
function lab(){
  // Explicit synthetic provider: no Google APIs, real participants or clocks.
  const clone=x=>JSON.parse(JSON.stringify(x));
  function system(strict=true){
    let book={capacity:1,available:1,rows:[],receipts:[],audit:[],outbox:[],pending:null,revision:0};
    let lock=false,late=null,cache={},calls=0,sent=0;
    const snapshot=()=>clone(book);
    const token=r=>JSON.stringify([r.actor,r.study,r.token]);
    const payload=r=>JSON.stringify([r.study,r.operation,r.qty,r.note]);
    const request=(r,fault="none")=>{
      if(lock)return "BUSY";
      lock=true;
      try{
        if(!r.actor||r.study!=="S"||r.operation!=="reserve"||r.qty!==1||typeof r.note!=="string"||!r.token)return "INVALID";
        const key=token(r),p=payload(r);
        const prior=strict?book.receipts.find(x=>x.key===key):cache[key];
        if(prior)return prior.payload===p?"REPLAY_"+prior.status:"CONFLICT";
        if(strict&&book.pending)return "RECONCILE";
        if(fault==="quota_before")return "BACKOFF";
        if(strict){
          // Model assumption: this durable intent is acknowledged before sending batch.
          book.pending={key,payload:p};
          if(fault==="after_intent")return "UNKNOWN";
        }
        const next=snapshot(),status=next.available>=1?"OK":"FULL";
        if(status==="OK"){next.available--;next.rows.push({key,note:r.note});next.outbox.push({key,state:"pending"});}
        const rec={key,payload:p,status};
        next.receipts.push(rec); next.audit.push({key,status});next.pending=null;next.revision++;
        calls++;
        if(fault==="invalid_batch"){
          if(strict){book.pending=null;return "REJECTED";} // definitive rejection in model only
          book.available=next.available;book.rows=next.rows;return "REJECTED";
        }
        if(fault==="late_commit"){late=next;return "UNKNOWN";}
        book=next;cache[key]=rec;
        return fault==="lost_ack"?"UNKNOWN":status;
      }finally{lock=false;}
    };
    function assertConsistent(b){
      const ids=b.rows.map(x=>x.key),keys=b.receipts.map(x=>x.key);
      return b.available>=0&&b.available+b.rows.length===b.capacity&&new Set(ids).size===ids.length&&new Set(keys).size===keys.length&&b.audit.length===b.receipts.length&&b.receipts.filter(x=>x.status==="OK").length===b.rows.length&&b.outbox.length===b.rows.length&&b.rows.every(x=>b.receipts.some(y=>y.key===x.key&&y.status==="OK")&&b.audit.some(y=>y.key===x.key&&y.status==="OK")&&b.outbox.some(y=>y.key===x.key));
    }
    return {request,snapshot,consistent:()=>assertConsistent(book),
      busy:(r)=>{lock=true;try{return request(r)}finally{lock=false}},
      evict:()=>{cache={}},
      late:()=>{if(late){book=late;late=null;}},
      calls:()=>calls,
      reconcile:r=>{const p=book.receipts.find(x=>x.key===token(r));return p?(p.payload===payload(r)?"FOUND_"+p.status:"CONFLICT"):(book.pending?"UNKNOWN":"ABSENT_NOT_PROOF");},
      notify:(lose=false)=>{const x=book.outbox[0];if(!x)return "NONE";if(strict&&x.state!=="pending")return "HOLD";if(strict)x.state="sending";sent++;if(lose)return "UNKNOWN";x.state="sent";return "SENT";},
      sent:()=>sent,
      restoreCheck:(candidate,trusted)=>strict?JSON.stringify(candidate)===JSON.stringify(trusted)&&!candidate.pending&&assertConsistent(candidate):candidate.rows.length===trusted.rows.length,
      outsideWrite:()=>{book.available++}
    };
  }
  const a={actor:"A",study:"S",token:"1",operation:"reserve",qty:1,note:"=1+1"},b={...a,actor:"B"};
  const eq=(x,y)=>{if(JSON.stringify(x)!==JSON.stringify(y))throw Error(JSON.stringify({actual:x,expected:y}))};
  const tests=[
    ["shared last seat",s=>{eq(s.request(a),"OK");eq(s.request(b),"FULL");eq(s.snapshot().available,0);eq(s.consistent(),true)}],
    ["busy no writes",s=>{const before=s.snapshot();eq(s.busy(a),"BUSY");eq(s.snapshot(),before);eq(s.calls(),0)}],
    ["same token replay after cache eviction",s=>{eq(s.request(a),"OK");let before=s.snapshot();s.evict();eq(s.request(a),"REPLAY_OK");eq(s.snapshot(),before)}],
    ["changed payload conflicts",s=>{s.request(a);eq(s.request({...a,note:"changed"}),"CONFLICT");eq(s.snapshot().rows.length,1)}],
    ["durable denial replay",s=>{s.request(a);s.request(b);s.evict();let before=s.snapshot();eq(s.request(b),"REPLAY_FULL");eq(s.snapshot(),before)}],
    ["reject invalid actor",s=>{let before=s.snapshot();eq(s.request({...a,actor:""}),"INVALID");eq(s.snapshot(),before)}],
    ["definite invalid batch no partial changes",s=>{let before=s.snapshot();eq(s.request(a,"invalid_batch"),"REJECTED");eq(s.snapshot(),before)}],
    ["quota before send",s=>{let before=s.snapshot();eq(s.request(a,"quota_before"),"BACKOFF");eq(s.snapshot(),before);eq(s.calls(),0);eq(s.request(a),"OK")}],
    ["lost ack readback no duplicate",s=>{eq(s.request(a,"lost_ack"),"UNKNOWN");eq(s.reconcile(a),"FOUND_OK");s.evict();eq(s.request(a),"REPLAY_OK");eq(s.calls(),1)}],
    ["delayed commit blocks all new shared writes",s=>{eq(s.request(a,"late_commit"),"UNKNOWN");eq(s.reconcile(a),"UNKNOWN");eq(s.request(b),"RECONCILE");eq(s.request(a),"RECONCILE");eq(s.calls(),1);s.late();eq(s.reconcile(a),"FOUND_OK");eq(s.request(b),"FULL");eq(s.consistent(),true)}],
    ["crash after intent preserves fence",s=>{eq(s.request(a,"after_intent"),"UNKNOWN");eq(s.reconcile(a),"UNKNOWN");eq(s.request(b),"RECONCILE");eq(s.calls(),0)}],
    ["absence does not prove abort",s=>{eq(s.reconcile(a),"ABSENT_NOT_PROOF")}],
    ["formula-looking string kept literal in model",s=>{s.request(a);eq(s.snapshot().rows[0].note,"=1+1")}],
    ["notification lost ack not blindly resent",s=>{s.request(a);eq(s.notify(true),"UNKNOWN");eq(s.notify(),"HOLD");eq(s.sent(),1);eq(s.snapshot().rows.length,1)}],
    ["restore checks receipts not row count",s=>{s.request(a);let good=s.snapshot(),bad=clone(good);bad.receipts=[];eq(s.restoreCheck(good,good),true);eq(s.restoreCheck(bad,good),false)}],
    ["restore checks stale content same row count",s=>{s.request(a);let good=s.snapshot(),bad=clone(good);bad.rows[0].note="old";eq(s.restoreCheck(bad,good),false)}],
    ["restore refuses unresolved pending",s=>{s.request(a,"after_intent");let pending=s.snapshot();eq(s.restoreCheck(pending,pending),false)}],
    ["outside writer violates lock assumption",s=>{s.request(a);s.outsideWrite();eq(s.consistent(),false)}]
  ];
  const results={};for(const strict of [true,false])results[strict?"strict":"legacy"]=tests.map(([name,test])=>{try{test(system(strict));return {name,pass:true}}catch(e){return {name,pass:false,error:String(e)}}});
  return results;
}
const result=lab();console.log(JSON.stringify(result,null,2));if(result.strict.some(x=>!x.pass)||result.legacy.every(x=>x.pass))process.exitCode=1;
