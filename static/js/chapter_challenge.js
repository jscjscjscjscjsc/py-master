/* A small, data-driven practice ritual shared by every chapter. */
const InkChallenge = (() => {
  const state = { chapter: 0, kp: 0, title: '', exercises: [], score: 0, index: 0, timer: 30, handle: null, mode: null };
  const $ = id => document.getElementById(id);
  const modes = [
    { name: '墨痕速答', hint: '先辨核心，再落笔。连续答对会留下完整墨印。' },
    { name: '星图连线', hint: '把概念与运行结果连起来，答案会点亮一颗星。' },
    { name: '断句辨误', hint: '找出 Python 语句中真正改变结果的那一笔。' },
    { name: '卷中推演', hint: '先预测，再验证；把代码当作可以推演的思想。' }
  ];
  function open(chapter, kp, title, exercises) {
    state.chapter = chapter; state.kp = kp; state.title = title;
    state.exercises = Array.isArray(exercises) && exercises.length ? exercises : [{ question: '请回到知识点阅读后再试一次。', options: ['继续阅读'], answer: 0, explanation: '先完成知识点阅读，再来试笔。' }];
    state.score = 0; state.index = 0; state.timer = 30;
    state.mode = modes[(Number(chapter) - 1) % modes.length];
    $('ink-challenge-modal').classList.add('active'); $('ink-challenge-modal').setAttribute('aria-hidden', 'false');
    $('ink-challenge-title').textContent = title + ' · ' + state.mode.name;
    render(); startTimer();
  }
  function render() {
    const ex = state.exercises[state.index % state.exercises.length];
    $('ink-challenge-score').textContent = `连中 ${state.score}`;
    $('ink-challenge-body').innerHTML = `<div class="ink-question">${escapeHtml(ex.question || '请思考后落笔')}</div><div class="ink-options">${(ex.options || []).map((o, i) => `<button onclick="InkChallenge.answer(${i})"><span>${String.fromCharCode(65+i)}</span>${escapeHtml(String(o).replace(/^\w[.、]\s*/, ''))}</button>`).join('')}</div><p class="ink-hint">${escapeHtml(state.mode.hint)}</p>`;
  }
  function answer(choice) {
    const ex = state.exercises[state.index % state.exercises.length];
    const correct = Number(ex.answer) === choice;
    const body = $('ink-challenge-body');
    if (correct) { state.score += 1; body.innerHTML = `<div class="ink-result success">✦ 落笔准确<br><small>${escapeHtml(ex.explanation || '概念已掌握。')}</small></div><button class="ink-next" onclick="InkChallenge.next()">继续试笔 →</button>`; }
    else { state.score = 0; body.innerHTML = `<div class="ink-result fail">墨迹散开了<br><small>再读一遍知识点，然后重新选择。</small></div><button class="ink-next" onclick="InkChallenge.next()">重新落笔 →</button>`; }
    $('ink-challenge-score').textContent = `连中 ${state.score}`;
    localStorage.setItem(`pymaster-ink-${state.chapter}-${state.kp}`, String(state.score));
  }
  function next() { state.index += 1; state.timer = 30; render(); }
  function startTimer() { clearInterval(state.handle); state.handle = setInterval(() => { state.timer -= 1; $('ink-challenge-timer').textContent = `00:${String(Math.max(0,state.timer)).padStart(2,'0')}`; if (state.timer <= 0) { clearInterval(state.handle); $('ink-challenge-body').innerHTML = '<div class="ink-result fail">今日试笔已止<br><small>慢一点，理解比速度更重要。</small></div>'; } }, 1000); }
  function close() { clearInterval(state.handle); $('ink-challenge-modal').classList.remove('active'); $('ink-challenge-modal').setAttribute('aria-hidden', 'true'); }
  function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  return { open, answer, next, close };
})();
