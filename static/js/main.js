/* AI NutriGuide – Main JS */

// ── SIDEBAR TOGGLE ──────────────────────────────────
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');
const hamburger = document.getElementById('hamburger');

function openSidebar()  { sidebar?.classList.add('open'); overlay?.classList.add('open'); }
function closeSidebar() { sidebar?.classList.remove('open'); overlay?.classList.remove('open'); }

hamburger?.addEventListener('click', openSidebar);
overlay?.addEventListener('click', closeSidebar);

// ── ACTIVE NAV LINK ─────────────────────────────────
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.getAttribute('href') === window.location.pathname) {
    link.classList.add('active');
  }
});

// ── DAY TABS (DIET PLAN) ─────────────────────────────
function initDayTabs() {
  const tabs = document.querySelectorAll('.day-tab');
  const panels = document.querySelectorAll('.day-panel');
  if (!tabs.length) return;
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.style.display = 'none');
      tab.classList.add('active');
      const target = document.getElementById('day-' + tab.dataset.day);
      if (target) target.style.display = 'grid';
    });
  });
}
initDayTabs();

// ── GROCERY CHECKBOXES ───────────────────────────────
function initGrocery() {
  document.querySelectorAll('.grocery-item input[type=checkbox]').forEach(cb => {
    const saved = localStorage.getItem('grocery_' + cb.id);
    if (saved === 'true') { cb.checked = true; updateGroceryStyle(cb); }
    cb.addEventListener('change', () => {
      localStorage.setItem('grocery_' + cb.id, cb.checked);
      updateGroceryStyle(cb);
    });
  });
}
function updateGroceryStyle(cb) {
  const label = cb.nextElementSibling;
  if (label) label.style.textDecoration = cb.checked ? 'line-through' : 'none';
}
initGrocery();

// ── DELETE ACTIVITY ──────────────────────────────────
document.querySelectorAll('.btn-delete-act').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Remove this activity?')) return;
    const id = btn.dataset.id;
    const res = await fetch('/api/delete-activity/' + id, { method:'POST' });
    if (res.ok) { btn.closest('.act-item')?.remove(); }
  });
});

// ── FORM VALIDATION ──────────────────────────────────
document.querySelectorAll('form[data-validate]').forEach(form => {
  form.addEventListener('submit', e => {
    let valid = true;
    form.querySelectorAll('[required]').forEach(field => {
      field.style.borderColor = '';
      if (!field.value.trim()) {
        field.style.borderColor = '#e74c3c';
        valid = false;
      }
    });
    if (!valid) {
      e.preventDefault();
      const msg = form.querySelector('.form-error');
      if (msg) { msg.style.display = 'block'; msg.textContent = 'Please fill all required fields.'; }
    }
  });
});

// ── PASSWORD MATCH ────────────────────────────────────
const pass1 = document.getElementById('password');
const pass2 = document.getElementById('confirm_password');
if (pass1 && pass2) {
  function checkMatch() {
    pass2.style.borderColor = (pass2.value && pass1.value !== pass2.value) ? '#e74c3c' : '';
  }
  pass1.addEventListener('input', checkMatch);
  pass2.addEventListener('input', checkMatch);
}

// ── AUTO HIDE ALERTS ─────────────────────────────────
document.querySelectorAll('.alert').forEach(a => {
  setTimeout(() => { a.style.opacity='0'; a.style.transition='opacity .5s';
    setTimeout(()=>a.remove(), 500); }, 4000);
});

// ── BMI COLOUR ON PROFILE SETUP ──────────────────────
function updateBMI() {
  const h = parseFloat(document.getElementById('height')?.value);
  const w = parseFloat(document.getElementById('weight')?.value);
  const bmiDisplay = document.getElementById('bmi-preview');
  if (!bmiDisplay || !h || !w || h < 50 || w < 10) return;
  const bmi = (w / ((h/100)**2)).toFixed(1);
  let cat = 'Underweight', col = '#3498db';
  if (bmi >= 18.5 && bmi < 25) { cat = 'Normal';      col = '#2ecc71'; }
  else if (bmi < 30)            { cat = 'Overweight';  col = '#f39c12'; }
  else if (bmi >= 30)           { cat = 'Obese';       col = '#e74c3c'; }
  bmiDisplay.innerHTML = `BMI: <strong style="color:${col}">${bmi}</strong> <span style="color:${col}">(${cat})</span>`;
}
document.getElementById('height')?.addEventListener('input', updateBMI);
document.getElementById('weight')?.addEventListener('input', updateBMI);

// ── PROGRESS BAR ANIMATION ───────────────────────────
window.addEventListener('load', () => {
  document.querySelectorAll('.prog-fill[data-width]').forEach(el => {
    setTimeout(() => { el.style.width = el.dataset.width + '%'; }, 200);
  });
});

console.log('🌿 AI NutriGuide loaded');
