// Таймер подготовки к случайному билету. Запускается по явному нажатию.
(() => {
  const clock = document.getElementById('prep-countdown');
  const minutes = document.getElementById('prep-minutes');
  let left = 5 * 60;
  let deadline = null;
  let interval = null;

  function render() {
    clock.textContent = `${Math.floor(left / 60).toString().padStart(2, '0')}:${(left % 60).toString().padStart(2, '0')}`;
  }
  function pause() {
    if (deadline !== null) left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    deadline = null;
    clearInterval(interval);
    interval = null;
    render();
  }
  function tick() {
    left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    render();
    if (left === 0) {
      pause();
      clock.setAttribute('aria-label', 'Время подготовки закончилось');
    }
  }
  document.getElementById('prep-start').addEventListener('click', () => {
    if (interval || left === 0) return;
    deadline = Date.now() + left * 1000;
    interval = setInterval(tick, 250);
    tick();
  });
  document.getElementById('prep-pause').addEventListener('click', pause);
  document.getElementById('prep-reset').addEventListener('click', () => {
    pause();
    const value = Math.max(1, Math.min(60, Number(minutes.value) || 5));
    minutes.value = value;
    left = value * 60;
    render();
  });
  minutes.addEventListener('change', () => document.getElementById('prep-reset').click());
  render();
})();
