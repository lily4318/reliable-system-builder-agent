"""Synthetic local Chromium training; requires Python Playwright and Chromium.
No external resources, human responses, or physical onset measurement.
Run: python test_experiment_timing.py
"""
import json
import os
import shutil
import unittest
from playwright.sync_api import sync_playwright

HTML = r'''<!doctype html><meta charset="utf-8"><title>Synthetic trial lab</title>
<button id="start">Start</button><button id="abort">Abort</button>
<div id="stimulus" style="font-size:48px" hidden>●</div><output id="state">idle</output>
<script>
const stim = document.querySelector('#stimulus'), out = document.querySelector('#state');
const rows = [], held = new Set();
const config = Object.freeze({version:'timing-lab-v1', unit:'ms', window:400, keys:['KeyF','KeyJ']});
let trial = null, seq = 0, timer = 0, frame = 0;
const strict = !location.hash.includes('legacy');
// The legacy comparator is deliberately unsafe and only for synthetic tests.
function state(s) { out.textContent = s; }
function finish(status, reason, event=null) {
  if (!trial) return;
  const t = trial; trial = null;
  cancelAnimationFrame(frame); clearTimeout(timer); stim.hidden = true;
  const response = event ? event.timeStamp : null;
  rows.push(Object.freeze({id:t.id, version:config.version, unit:config.unit,
    requested_at:t.requested, dom_write_at:t.write, frame_ready_at:t.ready,
    response_at:response, handler_at:event?performance.now():null, finished_at:performance.now(),
    rt_ms:status==='valid' ? (strict ? response-t.write : Date.now()-t.wall) : null,
    key:event?event.code:null, status, reason}));
  state('idle');
}
function start() {
  if (trial || (strict && (document.hidden || !document.hasFocus()))) return;
  const t = trial = {id:++seq,requested:performance.now(),write:null,ready:null,wall:Date.now()};
  state('pending');
  frame = requestAnimationFrame(() => {
    if (trial!==t) return;
    if (strict && (document.hidden || !document.hasFocus())) return finish('invalid','not-focused');
    stim.hidden = false; t.write = performance.now();
    frame = requestAnimationFrame(() => {
      if (trial!==t) return;
      if (strict && (document.hidden || !document.hasFocus())) return finish('invalid','not-focused');
      t.ready = performance.now();
      if (strict && t.ready-t.write>=config.window) return finish('invalid','frame-delay');
      state('ready');
      timer = setTimeout(() => {
        if (trial===t) {
          if (strict && (document.hidden || !document.hasFocus())) finish('invalid','not-focused');
          else finish('missing','deadline');
        }
      },Math.max(0, t.write+config.window-performance.now()));
    });
  });
}
function interrupt(reason) { if (strict && trial) finish('invalid',reason); }
document.querySelector('#start').addEventListener('click',start);
document.querySelector('#abort').addEventListener('click',()=>finish('invalid','abort'));
window.addEventListener('blur',()=>interrupt('blur'));
document.addEventListener('visibilitychange',()=>{if(document.hidden) interrupt('hidden');});
window.addEventListener('pagehide',()=>interrupt('pagehide'));
window.addEventListener('keyup',e=>{if(!strict || e.isTrusted) held.delete(e.code);});
window.addEventListener('keydown',e=>{
  if (!config.keys.includes(e.code) || (strict && !e.isTrusted)) return;
  const repeated = e.repeat || held.has(e.code); held.add(e.code);
  if (!trial) return;
  if (strict && repeated) return;
  if (strict && (document.hidden || !document.hasFocus())) return finish('invalid','not-focused',e);
  if (!strict) return finish('valid','response',e);
  if (trial.ready===null || !Number.isFinite(e.timeStamp) || e.timeStamp<trial.ready)
    return finish('invalid','early-or-clock',e);
  if (e.timeStamp>performance.now() || e.timeStamp>trial.write+config.window)
    return finish('invalid','late-or-clock',e);
  finish('valid','response',e);
});
window.snapshot=()=>JSON.parse(JSON.stringify(rows));
</script>'''

class TrialTiming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'), headless=os.getenv('LAB_HEADFUL')!='1', args=['--no-sandbox','--disable-background-networking'])
        print('BROWSER', cls.browser.version, flush=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.p.stop()
    def setUp(self):
        self.context = self.browser.new_context(offline=True)
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.page.goto('about:blank'+('#legacy' if os.getenv('LAB_MODE')=='legacy' else ''))
        self.page.set_content(HTML)
        self.page.bring_to_front()
    def start(self):
        self.page.locator('#start').click()
        self.page.wait_for_function("document.querySelector('#state').textContent==='ready'")
        self.assertTrue(self.page.locator('#stimulus').is_visible())
    def rows(self): return self.page.evaluate('snapshot()')
    def end(self):
        self.page.wait_for_function('snapshot().length>0')
        self.assertFalse(self.page.locator('#stimulus').is_visible())
        return self.rows()[-1]
    def test_response_and_wall_clock_jump(self):
        self.start()
        self.page.evaluate('Date.now=()=>1')
        self.page.keyboard.press('f')
        r=self.end(); self.assertEqual((r['status'],r['unit'],r['key']),('valid','ms','KeyF'))
        self.assertGreaterEqual(r['response_at'],r['frame_ready_at'])
        self.assertGreaterEqual(r['rt_ms'],0); self.assertLessEqual(r['rt_ms'],400)
        self.assertAlmostEqual(r['response_at']-r['dom_write_at'],r['rt_ms'],places=5)
        print('RT_PROXY_MS',r['rt_ms'],'HANDLER_LAG_MS',r['handler_at']-r['response_at'],flush=True)
    def test_early_key_before_frame(self):
        self.page.evaluate("document.querySelector('#start').click(); window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyF'}))")
        # Programmatic keyboard input is not a trusted response; abort preserves invalid row.
        self.page.locator('#abort').click(); r=self.end(); self.assertEqual(r['status'],'invalid'); self.assertIsNone(r['rt_ms'])
    def test_repeat_held_key_and_unique_row(self):
        self.page.keyboard.down('f'); self.start(); self.page.keyboard.down('f'); self.page.keyboard.up('f')
        self.page.keyboard.press('j'); r=self.end(); self.assertEqual((r['status'],r['key']),('valid','KeyJ'))
        self.page.keyboard.press('f'); self.assertEqual(len(self.rows()),1)
    def test_blur_event(self):
        self.start(); self.page.evaluate("window.dispatchEvent(new Event('blur'))")
        r=self.end(); self.assertEqual((r['status'],r['reason'],r['rt_ms']),('invalid','blur',None))
    def test_hidden_event(self):
        self.start(); self.page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true}); document.dispatchEvent(new Event('visibilitychange'))")
        r=self.end(); self.assertEqual((r['status'],r['reason'],r['rt_ms']),('invalid','hidden',None))
    def test_delayed_frame(self):
        self.page.evaluate("document.querySelector('#start').click(); requestAnimationFrame(()=>{const end=performance.now()+450; while(performance.now()<end){}})")
        r=self.end(); self.assertEqual((r['status'],r['reason'],r['rt_ms']),('invalid','frame-delay',None))
    def test_pagehide_event(self):
        self.start(); self.page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide'))")
        r=self.end(); self.assertEqual((r['status'],r['reason'],r['rt_ms']),('invalid','pagehide',None))
    def test_abort_then_new_trial(self):
        self.start(); self.page.locator('#abort').click(); self.assertEqual(self.end()['reason'],'abort')
        self.start(); self.page.keyboard.press('j'); self.page.wait_for_function('snapshot().length===2')
        self.assertEqual([(r['id'],r['status']) for r in self.rows()],[(1,'invalid'),(2,'valid')])
    def test_timeout_missing_not_zero(self):
        self.start(); r=self.end(); self.assertEqual((r['status'],r['reason'],r['rt_ms']),('missing','deadline',None))
    def test_synthetic_input_rejected(self):
        self.start(); self.page.evaluate("window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyF'}))")
        self.page.keyboard.press('j'); r=self.end(); self.assertEqual((r['status'],r['key']),('valid','KeyJ'))
    def test_real_tab_switch(self):
        other=self.context.new_page(); self.page.bring_to_front(); self.start(); other.bring_to_front()
        observed=self.page.evaluate('({hidden:document.hidden,focus:document.hasFocus()})')
        print('TAB_STATE',observed,flush=True)
        if not observed['hidden'] and observed['focus']:
            other.close(); self.skipTest('automation did not generate a real focus/visibility transition')
        r=self.end(); self.assertEqual(r['status'],'invalid'); self.assertIn(r['reason'],('blur','hidden','not-focused'))
        self.assertIsNone(r['rt_ms']); other.close()
    def test_export_rows_preserve_null_and_version(self):
        self.start(); self.page.locator('#abort').click(); self.end()
        self.start(); self.page.keyboard.press('j'); self.page.wait_for_function('snapshot().length===2')
        data=json.loads(json.dumps(self.rows(),allow_nan=False)); self.assertEqual([r['id'] for r in data],[1,2]); self.assertIsNone(data[0]['rt_ms']); self.assertEqual({r['version'] for r in data},{'timing-lab-v1'})

if __name__=='__main__': unittest.main(verbosity=2)
