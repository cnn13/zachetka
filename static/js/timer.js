// Помодоро: при досрочном переходе на перерыв рабочее время не обнуляется.
// Состояние также восстанавливается после обновления страницы в том же браузере.
(() => {
  const WORK = 25 * 60;
  const BREAK = 5 * 60;
  const modeButtons = {
    work: document.getElementById('work-btn'),
    rest: document.getElementById('break-btn'),
  };
  const clock = document.getElementById('countdown');
  const progress = document.getElementById('progress-bar');
  if (!clock) return;
  const subjectSelect = document.getElementById('subject-select');
  const csrfInput = document.querySelector('#timer-token-form [name=csrfmiddlewaretoken]');

  const storageKey = `zachetka:timer:v2:${clock.dataset.user || 'guest'}`;
  let state = { mode: 'work', workLeft: WORK, restLeft: BREAK, running: false, deadline: null, pendingSessions: [] };
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved && ['work', 'rest'].includes(saved.mode) &&
        [saved.workLeft, saved.restLeft].every(n => Number.isFinite(n) && n >= 0) &&
        typeof saved.running === 'boolean') {
      state = { ...state, ...saved };
    }
  } catch (_error) {
    // У приватных браузеров хранилище иногда недоступно; таймер всё равно работает.
  }

  if (!Array.isArray(state.pendingSessions)) state.pendingSessions = [];
  if (state.running && !Number.isFinite(state.deadline)) {
    state.running = false;
    state.deadline = null;
  }

  const currentField = () => state.mode === 'work' ? 'workLeft' : 'restLeft';
  const fullDuration = () => state.mode === 'work' ? WORK : BREAK;
  const write = () => {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (_error) { /* не мешаем отсчёту */ }
  };

  function render() {
    const left = state[currentField()];
    clock.textContent = `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`;
    progress.style.width = `${Math.min(100, 100 * (fullDuration() - left) / fullDuration())}%`;
    modeButtons.work.classList.toggle('on', state.mode === 'work');
    modeButtons.rest.classList.toggle('on', state.mode === 'rest');
  }

  function sessionToken() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    return `${Date.now()}_${Math.random().toString(36).slice(2)}_x`;
  }

  async function flushSessions() {
    if (!csrfInput || !state.pendingSessions.length) return;
    for (const item of [...state.pendingSessions]) {
      try {
        const response = await fetch('/timer/save_session/', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfInput.value },
          body: JSON.stringify({ token: item.token, subject_name: item.subject, duration_minutes: 25 })
        });
        if (!response.ok) break;
        state.pendingSessions = state.pendingSessions.filter(s => s.token !== item.token);
        write();
      } catch (_error) { break; }
    }
  }

  function recalculate() {
    if (!state.running || !Number.isFinite(state.deadline)) return;
    state[currentField()] = Math.max(0, Math.ceil((state.deadline - Date.now()) / 1000));
    if (state[currentField()] === 0) {
      const finished = state.mode;
      state.running = false;
      state.deadline = null;
      state.mode = finished === 'work' ? 'rest' : 'work';
      // Сессия записывается только после полного завершения рабочего периода.
      if (finished === 'work') {
        state.pendingSessions.push({ token: sessionToken(), subject: subjectSelect ? subjectSelect.value : 'Подготовка к экзаменам' });
        state.workLeft = WORK;
        flushSessions();
      } else state.restLeft = BREAK;
      clock.setAttribute('aria-label', finished === 'work' ? 'Работа окончена, можно начать перерыв' : 'Перерыв окончен, можно продолжить работу');
    }
    write();
  }

  function pause() {
    recalculate();
    state.running = false;
    state.deadline = null;
    write();
    render();
  }

  function switchMode(next) {
    if (next === state.mode) return;
    // Фиксируем оставшиеся секунды старого режима, потом переключаемся.
    pause();
    state.mode = next;
    write();
    if (subjectSelect) subjectSelect.disabled = next === 'rest';
    render();
  }

  function start() {
    recalculate();
    if (state.running) return;
    if (state[currentField()] === 0) state[currentField()] = fullDuration();
    state.running = true;
    state.deadline = Date.now() + state[currentField()] * 1000;
    write();
    render();
  }

  function reset() {
    pause();
    state[currentField()] = fullDuration();
    write();
    render();
  }

  modeButtons.work.addEventListener('click', () => switchMode('work'));
  modeButtons.rest.addEventListener('click', () => switchMode('rest'));
  document.getElementById('start-btn').addEventListener('click', start);
  document.getElementById('pause-btn').addEventListener('click', pause);
  document.getElementById('reset-btn').addEventListener('click', reset);

  // Если вкладка была в фоне, восстанавливаем время по времени завершения, не по тикам.
  setInterval(() => { recalculate(); render(); if (state.pendingSessions.length) flushSessions(); }, 1000);
  recalculate();
  if (subjectSelect) subjectSelect.disabled = state.mode === 'rest';
  render();
  flushSessions();
})();
