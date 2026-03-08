// Sports Misery Calculator - Frontend JavaScript v2
const API = '';  // Same origin

// ------------------------------------------------------------------
// State
// ------------------------------------------------------------------
let allTeams = {};
let step = 1;

// ------------------------------------------------------------------
// Init
// ------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    await loadTeams();
    renderStep(1);
    setupNav();
    updateYearLabel(1990);
});

async function loadTeams() {
    try {
        const res = await fetch(`${API}/api/teams`);
        allTeams = await res.json();
        populateDropdowns();
    } catch (e) {
        console.error('Failed to load teams:', e);
        showError('Could not connect to the server. Make sure the backend is running.');
    }
}

function populateDropdowns() {
    const leagueMap = { NFL: 'nfl-team', NBA: 'nba-team', MLB: 'mlb-team', NHL: 'nhl-team' };
    for (const [league, selectId] of Object.entries(leagueMap)) {
        const sel = document.getElementById(selectId);
        if (!sel) continue;
        (allTeams[league] || []).forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.name;
            sel.appendChild(opt);
        });
    }
}

// ------------------------------------------------------------------
// Navigation
// ------------------------------------------------------------------
function setupNav() {
    document.getElementById('btn-next-1')?.addEventListener('click', () => goToStep(2));
    document.getElementById('btn-next-2')?.addEventListener('click', () => {
        populateReview();
        goToStep(3);
    });
    document.getElementById('btn-back-2')?.addEventListener('click', () => goToStep(1));
    document.getElementById('btn-back-3')?.addEventListener('click', () => goToStep(2));
    document.getElementById('btn-calculate')?.addEventListener('click', calculate);
    document.getElementById('btn-reset')?.addEventListener('click', () => {
        document.getElementById('results-section').style.display = 'none';
        goToStep(1);
    });

    const slider = document.getElementById('fan-start-year');
    const yearDisplay = document.getElementById('year-display');
    if (slider && yearDisplay) {
        slider.addEventListener('input', () => {
            yearDisplay.textContent = slider.value;
            updateYearLabel(parseInt(slider.value));
        });
    }
}

function updateYearLabel(year) {
    const label = document.getElementById('year-label');
    if (!label) return;
    const yearsWatching = 2025 - year;
    if (year <= 1975) label.textContent = `OG fan — ${yearsWatching} years of potential suffering`;
    else if (year <= 1990) label.textContent = `Veteran fan — ${yearsWatching} years`;
    else if (year <= 2000) label.textContent = `Millennial fan — ${yearsWatching} years`;
    else if (year <= 2012) label.textContent = `Modern era fan — ${yearsWatching} years`;
    else label.textContent = `Newer fan — ${yearsWatching} years`;
}

function goToStep(n) {
    if (n === 2) {
        const year = parseInt(document.getElementById('fan-start-year')?.value);
        if (!year || year < 1950 || year > 2020) {
            shakeElement(document.getElementById('step-1'));
            return;
        }
    }
    if (n === 3) {
        const teams = getSelectedTeams();
        if (Object.keys(teams).length === 0) {
            shakeElement(document.getElementById('step-2'));
            showToast('Pick at least one team to continue.');
            return;
        }
    }
    step = n;
    renderStep(n);
}

function renderStep(n) {
    for (let i = 1; i <= 3; i++) {
        const el = document.getElementById(`step-${i}`);
        if (el) el.classList.toggle('active', i === n);
    }
    document.querySelectorAll('.progress-dot').forEach((dot, idx) => {
        dot.classList.toggle('active', idx + 1 <= n);
        dot.classList.toggle('complete', idx + 1 < n);
    });
}

function populateReview() {
    const year = document.getElementById('fan-start-year').value;
    const selIds = { NFL: 'nfl-team', NBA: 'nba-team', MLB: 'mlb-team', NHL: 'nhl-team' };
    const badges = { NFL: '🏈', NBA: '🏀', MLB: '⚾', NHL: '🏒' };
    const box = document.getElementById('review-box');
    if (!box) return;
    let html = `<div class="summary-row">
        <span class="summary-label">Since</span>
        <span class="summary-val">📅 ${year}</span>
    </div>`;
    for (const [l, id] of Object.entries(selIds)) {
        const sel = document.getElementById(id);
        if (sel && sel.value) {
            html += `<div class="summary-row">
                <span class="summary-label">${l}</span>
                <span class="summary-val">${badges[l]} ${sel.options[sel.selectedIndex].text}</span>
            </div>`;
        }
    }
    box.innerHTML = html;
}

// ------------------------------------------------------------------
// Calculation
// ------------------------------------------------------------------
function getSelectedTeams() {
    const result = {};
    const leagues = { NFL: 'nfl-team', NBA: 'nba-team', MLB: 'mlb-team', NHL: 'nhl-team' };
    for (const [league, id] of Object.entries(leagues)) {
        const sel = document.getElementById(id);
        if (sel && sel.value) result[league] = sel.value;
    }
    return result;
}

async function calculate() {
    const fanStart = parseInt(document.getElementById('fan-start-year').value);
    const teams = getSelectedTeams();

    const payload = {
        fan_start_year: fanStart,
        nfl_team: teams['NFL'] || null,
        nba_team: teams['NBA'] || null,
        mlb_team: teams['MLB'] || null,
        nhl_team: teams['NHL'] || null,
    };

    const btn = document.getElementById('btn-calculate');
    btn.textContent = 'Calculating...';
    btn.disabled = true;

    // Hide any previous error
    document.getElementById('error-msg').style.display = 'none';

    try {
        const res = await fetch(`${API}/api/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Server error');
        renderResults(data);
    } catch (e) {
        showError(e.message);
    } finally {
        btn.textContent = 'Calculate My Misery 💀';
        btn.disabled = false;
    }
}

// ------------------------------------------------------------------
// Results rendering (v2 format)
// ------------------------------------------------------------------
function renderResults(data) {
    const section = document.getElementById('results-section');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });

    // Headline score
    document.getElementById('overall-score').textContent = Math.round(data.total_score).toLocaleString();
    document.getElementById('misery-label').textContent = `${data.emoji} ${data.label}`;

    // Percentile line
    const pctEl = document.getElementById('percentile-line');
    if (pctEl && data.percentile) {
        pctEl.textContent = `You are ${data.percentile.comparison_text}`;
    }

    // Gauge — normalize to a visible range.
    // Scores can be negative (great teams) to ~3000+ (legendary suffering).
    // Map -500 → 0%, 0 → 30%, 1000 → 65%, 2000+ → 95%
    const gaugeScore = data.total_score;
    const gaugePct = Math.max(2, Math.min(98, 30 + (gaugeScore / 2000) * 65));
    const gauge = document.getElementById('gauge-fill');
    setTimeout(() => {
        gauge.style.width = `${gaugePct}%`;
        gauge.className = 'gauge-fill ' + getMiseryClass(data.label);
    }, 100);

    // Team cards
    const container = document.getElementById('team-cards');
    container.innerHTML = '';
    data.team_results.forEach(tr => container.appendChild(buildTeamCard(tr)));

    // Comparison table (only for multi-team)
    if (data.team_results.length > 1) {
        renderComparisonTable(data.team_results);
    } else {
        document.getElementById('comparison-section').style.display = 'none';
    }

    // Animate timeline bars after DOM settles
    setTimeout(animateTimelineBars, 300);
}

function getMiseryClass(label) {
    if (label.includes('Legendary'))    return 'legendary';
    if (label.includes('Chronic'))      return 'chronic';
    if (label.includes('Perpetual'))    return 'perpetual';
    if (label.includes('Occasional'))   return 'occasional';
    if (label.includes('Lucky'))        return 'lucky';
    return 'winner';
}

function scoreColor(score) {
    // score: negative = joy (green), positive = misery (red)
    if (score <= -30)  return '#44bb88';
    if (score <= 0)    return '#88cc44';
    if (score <= 20)   return '#ffcc00';
    if (score <= 40)   return '#ff9900';
    if (score <= 60)   return '#ff6633';
    return '#ff2244';
}

function buildTeamCard(tr) {
    const card = document.createElement('div');
    card.className = 'team-card';

    const champs = tr.championships.length;
    const finalsLosses = tr.finals_losses.length;
    const playoffPct = tr.seasons_watched > 0
        ? Math.round((tr.playoff_appearances / tr.seasons_watched) * 100) : 0;
    const worstYear = tr.worst_season?.year || '—';
    const worstScore = tr.worst_season?.score?.toFixed(0) || '—';
    const bestYear = tr.best_season?.year || '—';
    const scoreColor_ = scoreColor(tr.total_score / Math.max(tr.seasons_watched, 1));

    card.innerHTML = `
        <div class="team-card-header">
            <div class="team-badge ${tr.league.toLowerCase()}">${tr.league}</div>
            <h3 class="team-name">${tr.team_name}</h3>
            <div class="team-score-pill" style="background:${scoreColor_}">
                ${Math.round(tr.total_score).toLocaleString()}
            </div>
        </div>

        <div class="team-stats-row">
            <div class="stat-item">
                <span class="stat-val">${tr.avg_score_per_season?.toFixed(1) || '—'}</span>
                <span class="stat-lbl">Avg / Season</span>
            </div>
            <div class="stat-item">
                <span class="stat-val">${champs}</span>
                <span class="stat-lbl">Championships</span>
            </div>
            <div class="stat-item">
                <span class="stat-val">${playoffPct}%</span>
                <span class="stat-lbl">Playoff Rate</span>
            </div>
            <div class="stat-item">
                <span class="stat-val">${tr.seasons_watched}</span>
                <span class="stat-lbl">Seasons</span>
            </div>
        </div>

        <div class="season-highlights">
            <div class="highlight worst">
                <span class="hl-label">Worst Season</span>
                <span class="hl-val">${worstYear} <span class="hl-score">(+${worstScore} pts)</span></span>
            </div>
            <div class="highlight best">
                <span class="hl-label">Best Season</span>
                <span class="hl-val">${bestYear}${champs > 0 ? ' 🏆' : ''}</span>
            </div>
        </div>

        ${buildMiniTimeline(tr)}

        ${champs > 0 ? `<div class="champ-years">🏆 ${tr.championships.join(', ')}</div>` : ''}
        ${finalsLosses > 0 ? `<div class="finals-loss-years">💔 Finals losses: ${tr.finals_losses.join(', ')}</div>` : ''}
    `;

    return card;
}

function buildMiniTimeline(tr) {
    const timeline = tr.season_timeline;
    if (!timeline || Object.keys(timeline).length === 0) return '';

    const years = Object.keys(timeline).sort();
    const scores = years.map(y => timeline[y].score);
    const maxAbs = Math.max(...scores.map(Math.abs), 1);

    const bars = years.map(y => {
        const s = timeline[y].score;
        const hb = timeline[y].heartbreak_desc;
        const pct = Math.abs(s) / maxAbs * 100;
        const color = scoreColor(s);
        const direction = s >= 0 ? 'up' : 'down';
        const title = hb ? `${y}: ${hb}` : `${y}: ${s > 0 ? '+' : ''}${s.toFixed(0)} pts`;
        return `<div class="tl-bar ${direction}"
                     style="height:0%;--target:${pct}%;background:${color}"
                     title="${title}"
                     data-target="${pct}"></div>`;
    }).join('');

    return `
        <div class="timeline-wrap">
            <div class="timeline-label">Season-by-Season Misery</div>
            <div class="timeline-bars">${bars}</div>
            <div class="timeline-axis">
                <span>${years[0]}</span>
                <span>${years[Math.floor(years.length / 2)]}</span>
                <span>${years[years.length - 1]}</span>
            </div>
        </div>
    `;
}

function animateTimelineBars() {
    document.querySelectorAll('.tl-bar').forEach(bar => {
        const target = bar.dataset.target;
        requestAnimationFrame(() => { bar.style.height = target + '%'; });
    });
}

function renderComparisonTable(results) {
    document.getElementById('comparison-section').style.display = 'block';
    const tbody = document.querySelector('#comparison-table tbody');
    tbody.innerHTML = '';

    const headerRow = document.querySelector('#comparison-table thead tr');
    headerRow.innerHTML = ['', ...results.map(r => r.team_name)].map(h => `<th>${h}</th>`).join('');

    const rows = [
        ['Total Score',       r => Math.round(r.total_score).toLocaleString()],
        ['Avg / Season',      r => r.avg_score_per_season?.toFixed(1)],
        ['Championships',     r => r.championships.length],
        ['Finals Losses',     r => r.finals_losses.length],
        ['Playoff Rate',      r => Math.round((r.playoff_appearances / r.seasons_watched) * 100) + '%'],
        ['Worst Season',      r => r.worst_season ? `${r.worst_season.year} (+${r.worst_season.score.toFixed(0)})` : '—'],
    ];

    rows.forEach(([label, fn]) => {
        const row = document.createElement('tr');
        const rawVals = results.map(r => parseFloat(String(fn(r)).replace(/[^0-9.-]/g, '')) || 0);
        const maxVal = Math.max(...rawVals);
        row.innerHTML = `<td class="comp-name">${label}</td>` +
            results.map((r, i) => {
                const isWorst = rawVals[i] === maxVal && results.length > 1;
                return `<td class="${isWorst ? 'worst-cell' : ''}">${fn(r)}</td>`;
            }).join('');
        tbody.appendChild(row);
    });
}

// ------------------------------------------------------------------
// Utilities
// ------------------------------------------------------------------
function showError(msg) {
    const el = document.getElementById('error-msg');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
}

function showToast(msg) {
    let toast = document.getElementById('toast');
    if (!toast) { toast = document.createElement('div'); toast.id = 'toast'; document.body.appendChild(toast); }
    toast.textContent = msg;
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3000);
}

function shakeElement(el) {
    if (!el) return;
    el.classList.add('shake');
    setTimeout(() => el.classList.remove('shake'), 600);
}
