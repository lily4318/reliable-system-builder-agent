/* Headless browser DOM/event acceptance, synthetic cases only. */
"use strict";
(async()=>{
  const $=id=>document.getElementById(id);
  const check=(condition,message)=>{if(!condition)throw Error(message)};
  async function until(fn){for(let i=0;i<300;i++){if(fn())return;await new Promise(r=>setTimeout(r,20))}throw Error("browser wait exceeded")}
  const edit=(node,text)=>{node.value=text;node.dispatchEvent(new Event("input",{bubbles:true}))};
  const choose=(node,value)=>{node.value=value;node.dispatchEvent(new Event("change",{bubbles:true}))};
  const cases=[];
  try{
    await until(()=>window.intakeTest);
    const api=window.intakeTest;
    check(document.querySelectorAll(".question").length===13,"question count");
    check($("answer-purpose").value==="合成既有答案（啟動預填）","startup prefill");
    check($("export").disabled,"initial export disabled");
    for(const c of api.examples){
      choose($("example"),c.id);$("load-example").click();
      check(Object.entries(c.answers).every(([k,v])=>$("answer-"+k).value===v),"prefill "+c.id);
      check($("export").disabled,"loading invalidates export");
      $("generate").click();
      await until(()=>$("status").textContent.startsWith("草稿已產生"));
      const cards=[...document.querySelectorAll(".review")];
      check($("preview").textContent.includes("功能規格")&&$("preview").textContent.includes("架構草稿")&&$("preview").textContent.includes("需求追溯與驗收"),"full preview");
      check($("export").disabled,"no automatic export");
      for(let i=0;i<cards.length;i++){
        const card=cards[i],choice=["accept","modify","reject"][i%3];
        card.querySelector('input[value="'+choice+'"]').click();
        check(!card.querySelector("textarea").disabled,"editable after click");
        check(!$("export").disabled===false,"selection does not export");
        check(card.querySelector(".item-status").textContent.includes("尚未確認"),"no auto confirm");
        edit(card.querySelector("textarea"),"合成測試自訂文字 "+choice);
        card.querySelector(".confirm-item").click();
        check(card.querySelector(".item-status").textContent.includes("本項文字已確認"),"manual item confirm");
      }
      check(!$("finalize").disabled,"all decisions ready including empty");
      $("finalize").click();
      check(!$("export").disabled,"explicit final confirm");
      const output=api.exportObject();
      check(output.local_decisions.length===cards.length,"decision coverage");
      check(output.local_decisions.every((d,i)=>d.choice===["accept","modify","reject"][i%3]&&d.text==="合成測試自訂文字 "+d.choice),"edited decisions preserved");
      check(!output.specification_approved&&!output.write_authorized&&!output.deployment_authorized&&!output.real_agent_executed,"no authorization or model claim");
      check(output.specification_draft.sections.length===13,"source sections");
      if(cards.length){
        edit(cards[0].querySelector("textarea"),"重新修改本項文字");
        check($("export").disabled&&$("finalize").disabled,"edit invalidates final and item");
        cards[0].querySelector(".cancel-item").click();
        check(cards[0].querySelector("textarea").disabled,"cancel clears selection");
        cards[0].querySelector('input[value="reject"]').click();
        edit(cards[0].querySelector("textarea"),"");
        check(cards[0].querySelector(".confirm-item").disabled,"blank decision blocked");
        edit(cards[0].querySelector("textarea"),"重新確認拒絕文字");
        cards[0].querySelector(".confirm-item").click();$("finalize").click();
      }
      // Inspect the actual export click payload, intercept disk download in test mode.
      let blob=null,filename=null;
      const oldURL=URL.createObjectURL,oldClick=HTMLAnchorElement.prototype.click;
      URL.createObjectURL=b=>{blob=b;return oldURL.call(URL,b)};
      HTMLAnchorElement.prototype.click=function(){filename=this.download};
      try{$("export").click();check(blob&&filename==="website-reviewed-draft.json","export click payload");
          const downloaded=JSON.parse(await blob.text());check(downloaded.local_document_review_confirmed&&!downloaded.deployment_authorized,"export JSON");}
      finally{URL.createObjectURL=oldURL;HTMLAnchorElement.prototype.click=oldClick;}
      edit($("answer-purpose"),"本案例修改後的目的");
      check($("preview").textContent===""&&$("export").disabled&&$("finalize").disabled,"stale confirmation removed");
      $("generate").click();await until(()=>$("status").textContent.startsWith("草稿已產生"));
      check($("preview").textContent.includes("本案例修改後的目的"),"updated preview");
      cases.push({id:c.id,review_count:cards.length,pass:true});
    }
    // Browser file import, preview before applying, reject malformed and unknown keys.
    const putFile=async data=>{
      const transfer=new DataTransfer();transfer.items.add(new File([JSON.stringify(data)],"answers.json",{type:"application/json"}));
      $("import-file").files=transfer.files;$("import-file").dispatchEvent(new Event("change",{bubbles:true}));
    };
    const before=$("answer-purpose").value;
    await putFile({purpose:"合成檔案預填",notice:null});
    await until(()=>$("apply-import").disabled===false);
    check($("answer-purpose").value===before,"import preview no overwrite");
    $("apply-import").click();check($("answer-purpose").value==="合成檔案預填","explicit import");
    await putFile({unexpected:"invalid"});
    await until(()=>$("status").textContent.includes("格式錯誤"));
    check($("answer-purpose").value==="合成檔案預填","bad import preserves answers");
    const select=document.querySelector(".question select");choose(select,"待確認");
    check($("answer-purpose").value==="待確認","common answer selection");
    edit($("answer-purpose"),"自由修改常用答案");check($("answer-purpose").value==="自由修改常用答案","free text edit");
    await api.report({status:"PASS",cases,import_test:true,export_payload_test:true,model_executed:false});
  }catch(e){if(window.intakeTest)await window.intakeTest.report({status:"FAIL",cases,error:String(e.message).slice(0,200)});}
})();
