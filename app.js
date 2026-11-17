"use strict";
(() => {
  const VERSION = "sim-v1";
  const $ = id => document.getElementById(id);
  let current = null;
  function integer(text, min, max) {
    if (!/^[0-9]{1,10}$/.test(text)) return null;
    const n = Number(text);
    return Number.isSafeInteger(n) && n >= min && n <= max ? n : null;
  }
  // Teaching-only deterministic PRNG. Rejection avoids modulo reduction bias.
  function simulate(n, seed) {
    let state = seed >>> 0;
    const next32 = () => {
      state = (state + 0x6D2B79F5) >>> 0;
      let t = Math.imul(state ^ (state >>> 15), state | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return (t ^ (t >>> 14)) >>> 0;
    };
    const draw = bound => {
      const limit = 4294967296 - (4294967296 % bound);
      let value;
      do { value = next32(); } while (value >= limit);
      return value % bound;
    };
    const groups = Array.from({length:n}, (_, i) => i < n / 2 ? "A" : "B");
    for (let i = n - 1; i > 0; i--) {
      const j = draw(i + 1);
      [groups[i], groups[j]] = [groups[j], groups[i]];
    }
    return groups.map((group, i) => ({id:i + 1, group, score:(group === "A" ? 50 : 58) + draw(11) + draw(11) + draw(11) - 15}));
  }
  function invalidate(message) {
    current = null;
    $("results").hidden = true;
    $("rows").replaceChildren();
    $("download").disabled = true;
    $("status").classList.remove("error");
    $("status").textContent = message;
    for (const id of ["sample", "seed"]) $(id).removeAttribute("aria-invalid");
  }
  function generate(event) {
    if (event) event.preventDefault();
    invalidate("");
    const n = integer($("sample").value, 20, 100);
    const seed = integer($("seed").value, 0, 4294967295);
    const badSample = n === null || n % 2 !== 0;
    if (badSample || seed === null) {
      if (badSample) $("sample").setAttribute("aria-invalid", "true");
      if (seed === null) $("seed").setAttribute("aria-invalid", "true");
      $("status").classList.add("error");
      $("status").textContent = "請確認：樣本數須為 20–100 的偶數；種子須為 0–4294967295 的整數。";
      $(badSample ? "sample" : "seed").focus();
      return;
    }
    const rows = simulate(n, seed);
    for (const group of ["A", "B"]) {
      const values = rows.filter(row => row.group === group);
      const mean = values.reduce((sum,row) => sum + row.score, 0) / values.length;
      const suffix = group.toLowerCase();
      $("count-" + suffix).textContent = values.length + " 人";
      $("mean-" + suffix).textContent = mean.toFixed(1);
      $("bar-" + suffix).value = mean;
    }
    const fragment = document.createDocumentFragment();
    for (const row of rows) {
      const tr = document.createElement("tr");
      for (const value of [row.id, row.group, row.score]) {
        const td = document.createElement("td"); td.textContent = String(value); tr.append(td);
      }
      fragment.append(tr);
    }
    $("rows").replaceChildren(fragment);
    current = {n, seed, rows};
    $("run-info").textContent = `樣本 ${n} 人 · 種子 ${seed} · ${VERSION}`;
    $("results").hidden = false;
    $("download").disabled = false;
    $("status").textContent = `已生成 ${n} 筆合成資料，兩組各 ${n / 2} 人。`;
  }
  $("simulation").addEventListener("submit", generate);
  for (const id of ["sample", "seed"]) $(id).addEventListener("input", () => invalidate("參數已變更，請重新產生資料。"));
  $("download").addEventListener("click", () => {
    if (!current) return;
    const {n, seed, rows} = current;
    // Only validated integers, fixed enums and fixed version reach CSV.
    const csv = ["sample_id,group,simulated_score,sample_size,seed,simulation_version",
      ...rows.map(r => `${r.id},${r.group},${r.score},${n},${seed},${VERSION}`)].join("\r\n") + "\r\n";
    const url = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8"}));
    const a = document.createElement("a");
    a.href = url; a.download = `research-methods-${n}-${seed}.csv`;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  generate();
})();
