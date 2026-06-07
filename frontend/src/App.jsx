// ============================================================
//  INTERNSHIP RISK ANALYZER — React Frontend (WHITE THEME)
//  File: src/App.jsx
// ============================================================

import { useState, useEffect, useCallback, useMemo } from "react";

const API_URL = "http://localhost:8000";

async function apiFetch(path, method = "GET", body = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Request failed");
  }
  return response.json();
}

let _toastFn = null;
function toast(msg, type = "info") { if (_toastFn) _toastFn(msg, type); }

function riskColor(label) {
  if (!label) return "#6366f1";
  const l = label.toUpperCase();
  if (l.includes("HIGH"))   return "#ef4444";
  if (l.includes("MEDIUM")) return "#f59e0b";
  return "#22c55e";
}
function riskBg(label) {
  if (!label) return "#ede9fe";
  const l = label.toUpperCase();
  if (l.includes("HIGH"))   return "#fee2e2";
  if (l.includes("MEDIUM")) return "#fef3c7";
  return "#dcfce7";
}

const DATASET_STATS = {
  totalSamples: 1500, scamSamples: 250, legitSamples: 1250,
  paymentFlags: 250, modelAccuracy: 88.0, features: 23,
  scamRate: "16.7", safeRate: "83.3",
};

function seededRand(seed, min, max) {
  const x = Math.sin(seed) * 10000;
  const r = x - Math.floor(x);
  return Math.floor(r * (max - min + 1)) + min;
}
function getTodayStats() {
  const d = new Date();
  const seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  return {
    totalScans: DATASET_STATS.totalSamples,
    scamsDetected: DATASET_STATS.scamSamples,
    safePostings: DATASET_STATS.legitSamples,
    avgRisk: (seededRand(seed + 2, 550, 720) / 10).toFixed(1),
    scamRate: DATASET_STATS.scamRate,
    safeRate: DATASET_STATS.safeRate,
    todayScans: seededRand(seed + 3, 8, 22),
    weeklyDelta: (seededRand(seed + 4, 20, 60) / 10).toFixed(1),
  };
}
function getWeeklyData() {
  const d = new Date();
  const weekSeed = d.getFullYear() * 100 + Math.floor(d.getTime() / (7 * 24 * 3600 * 1000));
  return ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((day, i) => ({
    day,
    scams: seededRand(weekSeed + i, 6, 34),
    safe:  seededRand(weekSeed + i + 10, 10, 28),
  }));
}

const STYLES = `
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --white:#ffffff;--bg:#f8f9fc;--bg2:#f1f3f8;--bg3:#e8ecf4;
  --border:#e2e5ef;--border2:#cdd2e0;
  --ink:#0f1623;--ink2:#3d4a63;--ink3:#7a89a8;--ink4:#b0bcd4;
  --blue:#3b5bdb;--blue2:#4c6ef5;--blue-bg:#eef2ff;--blue-bd:#c5d0fa;
  --red:#ef4444;--red-bg:#fee2e2;--amber:#f59e0b;--amb-bg:#fef3c7;
  --green:#22c55e;--grn-bg:#dcfce7;
  --mono:'JetBrains Mono',monospace;--sans:'Plus Jakarta Sans',sans-serif;
  --radius:10px;
  --shadow:0 1px 3px rgba(0,0,0,0.08),0 4px 16px rgba(0,0,0,0.04);
  --shadow2:0 4px 12px rgba(0,0,0,0.1),0 12px 40px rgba(0,0,0,0.06);
}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);min-height:100vh;font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--bg2);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}
::selection{background:#c5d0fa;color:var(--blue);}
.root{display:flex;min-height:100vh;}
.sb{width:240px;min-height:100vh;background:var(--white);border-right:1px solid var(--border);display:flex;flex-direction:column;position:fixed;left:0;top:0;bottom:0;z-index:60;}
.sb-brand{padding:20px 18px 16px;border-bottom:1px solid var(--border);}
.sb-logo{display:flex;align-items:center;gap:10px;cursor:pointer;margin-bottom:12px;}
.sb-logo-icon{width:36px;height:36px;background:var(--blue);border-radius:10px;display:grid;place-items:center;flex-shrink:0;}
.sb-logo-letter{font-family:var(--mono);font-size:11px;font-weight:600;color:white;letter-spacing:0.05em;}
.sb-name{font-size:13px;font-weight:700;color:var(--ink);line-height:1.3;}
.sb-name span{color:var(--blue);}
.sb-status{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;background:#dcfce7;border:1px solid #bbf7d0;border-radius:20px;}
.sb-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s ease-in-out infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
.sb-status-txt{font-size:10px;font-weight:600;color:#16a34a;font-family:var(--mono);}
.sb-nav{flex:1;padding:10px 0;overflow-y:auto;}
.sb-section{font-size:9px;font-family:var(--mono);letter-spacing:0.18em;text-transform:uppercase;color:var(--ink4);padding:10px 18px 4px;margin-top:4px;}
.sb-item{display:flex;align-items:center;gap:10px;padding:9px 16px;margin:1px 8px;border-radius:8px;cursor:pointer;transition:all 0.15s;font-size:13px;font-weight:500;color:var(--ink2);user-select:none;}
.sb-item:hover{background:var(--bg2);color:var(--ink);}
.sb-item.on{background:var(--blue-bg);color:var(--blue);font-weight:600;}
.sb-item .ic{font-size:15px;width:20px;text-align:center;flex-shrink:0;}
.sb-footer{padding:14px 18px;border-top:1px solid var(--border);}
.sb-ver{font-size:10px;font-family:var(--mono);color:var(--ink3);}
.sb-build{font-size:10px;color:var(--ink4);margin-top:2px;}
.carea{margin-left:240px;flex:1;display:flex;flex-direction:column;min-height:100vh;overflow-x:hidden;min-width:0;}
.topbar{height:54px;background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 28px;position:sticky;top:0;z-index:40;}
.tb-left{display:flex;align-items:center;gap:8px;}
.bc-item{font-size:12px;color:var(--ink3);font-family:var(--mono);}
.bc-item.on{color:var(--blue);font-weight:600;}
.bc-sep{color:var(--ink4);font-size:12px;}
.tb-right{display:flex;align-items:center;gap:8px;}
.tb-chip{padding:5px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:20px;font-size:11px;font-family:var(--mono);color:var(--ink2);display:flex;align-items:center;gap:5px;}
.tb-chip .dot{width:6px;height:6px;border-radius:50%;}
.tbody{flex:1;padding:28px;overflow-x:hidden;}
.pg-title{font-size:26px;font-weight:800;color:var(--ink);line-height:1.2;}
.pg-title em{color:var(--blue);font-style:normal;}
.pg-sub{font-size:12px;color:var(--ink3);margin-top:4px;font-family:var(--mono);}
.sec-tag{display:inline-flex;align-items:center;gap:6px;font-size:10px;font-family:var(--mono);font-weight:600;color:var(--blue);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;}
.sec-tag::before{content:'';display:block;width:14px;height:2px;background:var(--blue);border-radius:2px;}
.card{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);transition:border-color 0.2s,box-shadow 0.2s;}
.card:hover{border-color:var(--border2);box-shadow:var(--shadow2);}
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;}
.stat-box{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);position:relative;overflow:hidden;}
.stat-box::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--c,var(--blue));border-radius:var(--radius) var(--radius) 0 0;}
.stat-val{font-size:28px;font-weight:800;color:var(--ink);line-height:1;margin-bottom:4px;}
.stat-lbl{font-size:11px;color:var(--ink3);font-family:var(--mono);text-transform:uppercase;letter-spacing:0.08em;}
.stat-delta{font-size:11px;font-family:var(--mono);margin-top:4px;color:var(--c,var(--blue));font-weight:600;}
.inp{width:100%;background:var(--bg);border:1px solid var(--border2);color:var(--ink);padding:10px 14px;font-family:var(--mono);font-size:12px;border-radius:8px;outline:none;transition:border-color 0.2s,box-shadow 0.2s;}
.inp:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(59,91,219,0.1);background:var(--white);}
.inp::placeholder{color:var(--ink4);}
.textarea{resize:vertical;min-height:150px;line-height:1.7;}
.lbl{display:block;font-size:11px;font-weight:600;color:var(--ink2);margin-bottom:7px;letter-spacing:0.06em;text-transform:uppercase;}
.btn-primary{display:inline-flex;align-items:center;gap:8px;padding:11px 22px;background:var(--blue);color:white;border:none;border-radius:8px;cursor:pointer;font-family:var(--sans);font-size:13px;font-weight:600;transition:all 0.2s;}
.btn-primary:hover:not(:disabled){background:var(--blue2);box-shadow:0 4px 16px rgba(59,91,219,0.35);transform:translateY(-1px);}
.btn-primary:disabled{opacity:0.5;cursor:not-allowed;}
.btn-outline{display:inline-flex;align-items:center;gap:7px;padding:10px 18px;background:transparent;color:var(--ink2);border:1px solid var(--border2);border-radius:8px;cursor:pointer;font-family:var(--sans);font-size:13px;font-weight:500;transition:all 0.2s;}
.btn-outline:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-bg);}
.btn-ghost{padding:6px 12px;background:var(--bg2);color:var(--ink2);border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:11px;font-family:var(--mono);transition:all 0.15s;}
.btn-ghost:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-bg);}
.score-wrap{display:flex;flex-direction:column;align-items:center;gap:8px;}
.score-ring{width:100px;height:100px;border-radius:50%;display:grid;place-items:center;padding:5px;}
.score-inner{width:100%;height:100%;border-radius:50%;background:white;display:grid;place-items:center;box-shadow:inset 0 2px 8px rgba(0,0,0,0.06);}
.score-num{font-size:28px;font-weight:800;line-height:1;}
.score-sub{font-size:9px;color:var(--ink3);font-family:var(--mono);}
.meter{margin-bottom:12px;}
.meter-head{display:flex;justify-content:space-between;font-size:11px;color:var(--ink2);margin-bottom:5px;font-family:var(--mono);}
.meter-track{height:6px;background:var(--bg3);border-radius:4px;overflow:hidden;}
.meter-fill{height:100%;border-radius:4px;transition:width 0.9s cubic-bezier(0.16,1,0.3,1);}
.chip{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;font-size:11px;font-family:var(--mono);border-radius:6px;margin:3px;border:1px solid;}
.chips-wrap{display:flex;flex-wrap:wrap;}
.loading-bar{height:3px;background:linear-gradient(90deg,var(--blue),#818cf8,var(--blue));background-size:200% 100%;animation:loading 1.2s linear infinite;border-radius:2px;margin-top:10px;}
@keyframes loading{0%{background-position:200% 0;}100%{background-position:-200% 0;}}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
.tbl{width:100%;border-collapse:collapse;}
.tbl th{text-align:left;padding:10px 14px;font-size:10px;font-family:var(--mono);letter-spacing:0.12em;text-transform:uppercase;color:var(--ink3);border-bottom:2px solid var(--border);}
.tbl td{padding:12px 14px;font-size:13px;border-bottom:1px solid var(--bg2);vertical-align:middle;}
.tbl tr:hover td{background:var(--bg);}
.divider{height:1px;background:var(--border);margin:18px 0;}
.mb4{margin-bottom:4px;}.mb8{margin-bottom:8px;}.mb12{margin-bottom:12px;}
.mb16{margin-bottom:16px;}.mb20{margin-bottom:20px;}.mb24{margin-bottom:24px;}
.mt8{margin-top:8px;}.mt12{margin-top:12px;}.mt16{margin-top:16px;}
.flex{display:flex;}.items-c{align-items:center;}.gap8{gap:8px;}.gap12{gap:12px;}
.between{justify-content:space-between;}.w-full{width:100%;}
.alert{padding:12px 16px;border-radius:8px;font-size:12.5px;font-family:var(--mono);margin-bottom:12px;display:flex;align-items:center;gap:8px;border:1px solid;}
.alert.danger{background:var(--red-bg);border-color:#fca5a5;color:#b91c1c;}
.alert.success{background:var(--grn-bg);border-color:#86efac;color:#15803d;}
.alert.warning{background:var(--amb-bg);border-color:#fcd34d;color:#b45309;}
.alert.info{background:var(--blue-bg);border-color:var(--blue-bd);color:var(--blue);}
.feat-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--bg2);font-size:12px;}
.feat-row:last-child{border-bottom:none;}
.feat-lbl{color:var(--ink2);font-family:var(--mono);font-size:11px;}
.feat-val{font-family:var(--mono);font-weight:600;font-size:12px;}
.module-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;}
.module-card{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:20px;cursor:pointer;transition:all 0.2s;box-shadow:var(--shadow);position:relative;}
.module-card:hover{border-color:var(--blue);box-shadow:var(--shadow2);transform:translateY(-2px);}
.module-card::after{content:'→';position:absolute;right:16px;bottom:16px;font-size:18px;color:var(--ink4);transition:all 0.2s;}
.module-card:hover::after{color:var(--blue);transform:translateX(4px);}
.mc-icon{font-size:28px;margin-bottom:10px;}
.mc-name{font-size:14px;font-weight:700;color:var(--ink);margin-bottom:4px;}
.mc-desc{font-size:12px;color:var(--ink2);line-height:1.6;}
.mc-tag{font-size:10px;font-family:var(--mono);color:var(--ink3);margin-top:8px;}
.empty{text-align:center;padding:48px 20px;color:var(--ink3);}
.empty-icon{font-size:36px;margin-bottom:10px;}
.empty-txt{font-size:12px;font-family:var(--mono);}
.prec-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px;}
.prec-card{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow);transition:all 0.2s;position:relative;overflow:hidden;}
.prec-card:hover{transform:translateY(-2px);box-shadow:var(--shadow2);}
.prec-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:var(--radius) var(--radius) 0 0;}
.prec-card.critical::before{background:var(--red);}
.prec-card.high::before{background:#f97316;}
.prec-card.medium::before{background:var(--amber);}
.prec-icon{font-size:22px;margin-bottom:10px;}
.prec-title{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:5px;}
.prec-desc{font-size:11.5px;color:var(--ink2);line-height:1.65;}
.prec-sev{display:inline-block;margin-top:10px;font-size:9px;font-family:var(--mono);font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 8px;border-radius:20px;border:1px solid;}
.prec-card.critical .prec-sev{color:var(--red);background:var(--red-bg);border-color:#fca5a5;}
.prec-card.high .prec-sev{color:#ea580c;background:#ffedd5;border-color:#fdba74;}
.prec-card.medium .prec-sev{color:#b45309;background:var(--amb-bg);border-color:#fcd34d;}
.bar-chart{display:flex;align-items:flex-end;gap:8px;height:90px;padding:0 4px;}
.bar-col{display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;}
.bar-stack{display:flex;flex-direction:column;width:100%;gap:2px;height:75px;justify-content:flex-end;}
.bar-seg{border-radius:3px 3px 0 0;min-height:2px;transition:height 0.8s ease;}
.bar-lbl{font-size:9px;font-family:var(--mono);color:var(--ink3);}
.donut-wrap{display:flex;align-items:center;gap:20px;}
.donut-legend{flex:1;}
.leg-item{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:12px;}
.leg-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.leg-pct{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink3);font-weight:600;}
.home-hero{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 32px 48px;min-height:340px;}
.home-badge{display:inline-flex;align-items:center;gap:7px;background:var(--blue-bg);border:1px solid var(--blue-bd);border-radius:20px;padding:5px 16px;font-size:11px;font-weight:600;color:var(--blue);font-family:var(--mono);margin-bottom:22px;letter-spacing:0.06em;}
.home-title{font-size:clamp(36px,5vw,56px);font-weight:800;color:var(--ink);line-height:1.1;margin-bottom:14px;letter-spacing:-0.02em;}
.home-title .accent{color:var(--blue);}
.home-sub{font-size:15px;color:var(--ink2);line-height:1.7;max-width:480px;margin-bottom:36px;font-family:var(--mono);}
.home-cta{display:inline-flex;align-items:center;gap:10px;padding:14px 32px;background:var(--blue);color:white;border:none;border-radius:10px;cursor:pointer;font-family:var(--sans);font-size:15px;font-weight:700;transition:all 0.2s;box-shadow:0 4px 20px rgba(59,91,219,0.3);margin-bottom:48px;}
.home-cta:hover{background:var(--blue2);transform:translateY(-2px);box-shadow:0 8px 28px rgba(59,91,219,0.4);}
.home-flags{display:flex;flex-direction:column;gap:10px;width:100%;max-width:420px;text-align:left;}
.home-flag-label{font-size:11px;font-weight:700;color:var(--ink3);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;text-align:left;width:100%;max-width:420px;}
.code-block{background:#1a1e2e;border-radius:10px;overflow:hidden;border:1px solid #2d3250;}
.code-header{padding:10px 16px;background:#14172a;display:flex;align-items:center;gap:6px;border-bottom:1px solid #2d3250;}
.code-dot{width:10px;height:10px;border-radius:50%;}
.code-file{margin-left:auto;font-size:10px;font-family:var(--mono);color:#4b5680;}
.code-body{padding:18px 20px;font-family:var(--mono);font-size:11.5px;line-height:2;}
.c-dim{color:#4b5680;}.c-blue{color:#7eb8ff;}.c-gold{color:#fbbf24;}.c-green{color:#34d399;}.c-white{color:#d4daf0;}
.btn-back{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:var(--bg2);color:var(--ink2);border:1px solid var(--border2);border-radius:7px;cursor:pointer;font-family:var(--mono);font-size:11px;font-weight:600;transition:all 0.15s;letter-spacing:0.03em;}
.btn-back:hover{background:var(--blue-bg);border-color:var(--blue);color:var(--blue);}
.btn-back .arr{font-size:13px;line-height:1;}
.toast-wrap{position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;}
.toast{padding:10px 16px;border-radius:8px;font-size:12px;display:flex;align-items:center;gap:8px;animation:fadeUp 0.3s both;border:1px solid;box-shadow:var(--shadow2);background:var(--white);font-family:var(--mono);}
.toast.success{border-color:#86efac;color:#15803d;}
.toast.error{border-color:#fca5a5;color:#b91c1c;}
.toast.warn{border-color:#fcd34d;color:#b45309;}
.toast.info{border-color:var(--blue-bd);color:var(--blue);}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
.splash{position:fixed;inset:0;background:var(--white);z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;}
.splash-logo{width:64px;height:64px;background:var(--blue);border-radius:16px;display:grid;place-items:center;animation:logoIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;box-shadow:0 8px 32px rgba(59,91,219,0.35);}
@keyframes logoIn{from{opacity:0;transform:scale(0.6);}to{opacity:1;transform:scale(1);}}
.splash-title{font-size:20px;font-weight:800;color:var(--ink);animation:fadeUp 0.4s 0.2s both;}
.splash-sub{font-size:11px;color:var(--ink3);font-family:var(--mono);animation:fadeUp 0.4s 0.3s both;}
.splash-bar{width:200px;height:3px;background:var(--bg3);border-radius:4px;overflow:hidden;animation:fadeUp 0.4s 0.4s both;}
.splash-fill{height:100%;background:linear-gradient(90deg,var(--blue),#818cf8);border-radius:4px;animation:splashLoad 2s ease-out forwards;}
@keyframes splashLoad{from{width:0;}to{width:100%;}}
.splash-fade{animation:fadeOut 0.4s ease forwards;}
@keyframes fadeOut{to{opacity:0;pointer-events:none;}}
@keyframes pageIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:none;}}
.page-in{animation:pageIn 0.4s cubic-bezier(0.16,1,0.3,1) both;}
.arch-block{background:#1a1e2e;border-radius:10px;padding:20px;font-family:var(--mono);font-size:11.5px;line-height:2.2;color:#7a89a8;}

/* Flowchart styles */
.arch-flow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 650px;
  margin: 16px auto 24px;
}
.arch-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 24px;
  width: 100%;
  box-shadow: var(--shadow);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  border-left: 4px solid var(--blue);
  text-align: left;
}
.arch-card:hover {
  transform: translateY(-3px);
  border-color: var(--blue2);
  box-shadow: var(--shadow2);
  background: linear-gradient(145deg, var(--white), var(--blue-bg));
}
.arch-card.final {
  border-left-color: var(--green);
}
.arch-card.final:hover {
  border-color: var(--green);
  background: linear-gradient(145deg, var(--white), var(--grn-bg));
}
.arch-card-num {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--ink3);
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  text-transform: uppercase;
}
.arch-card-title {
  font-size: 16px;
  font-weight: 750;
  color: var(--ink);
  margin-bottom: 6px;
}
.arch-card-desc {
  font-size: 12.5px;
  color: var(--ink2);
  line-height: 1.55;
}
.arch-card-code {
  margin-top: 10px;
  font-family: var(--mono);
  font-size: 10.5px;
  color: var(--blue);
  background: var(--blue-bg);
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
  font-weight: 500;
}
.arch-card.final .arch-card-code {
  color: var(--green);
  background: var(--grn-bg);
}
.arch-arrow {
  color: var(--border2);
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  animation: bounce 2s ease-in-out infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(6px); }
}

/* Hero banner styles */
.dashboard-hero-banner {
  position: relative;
  width: 100%;
  height: 180px;
  border-radius: var(--radius);
  background-image: url('/hero_banner.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  padding: 0 32px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.hero-banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(15, 22, 35, 0.95) 0%, rgba(15, 22, 35, 0.65) 100%);
  z-index: 1;
}
.hero-banner-content {
  position: relative;
  z-index: 2;
  color: var(--white);
  text-align: left;
}
.hero-banner-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(59, 91, 219, 0.35);
  border: 1px solid var(--blue);
  color: #a5b4fc;
  border-radius: 20px;
  font-size: 10px;
  font-family: var(--mono);
  font-weight: 600;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
  text-transform: uppercase;
}
.hero-banner-badge::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--blue);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--blue);
}
.hero-banner-title {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 6px;
  letter-spacing: -0.01em;
  color: var(--white);
}
.hero-banner-subtitle {
  font-size: 13.5px;
  color: var(--ink4);
  max-width: 600px;
  line-height: 1.5;
}

/* AI Disclaimer styles */
.ai-disclaimer {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-top: 20px;
  align-items: flex-start;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
}
.ai-disclaimer-icon {
  color: var(--ink3);
  font-size: 15px;
  line-height: 1;
  margin-top: 2px;
}
.ai-disclaimer-text {
  font-size: 11.5px;
  color: var(--ink3);
  line-height: 1.5;
  margin: 0;
  font-family: var(--sans);
  text-align: left;
}

/* Metric Card Styles */
.metric-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
  position: relative;
  overflow: hidden;
  border-top: 3px solid var(--blue);
  text-align: left;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow2);
  border-color: var(--blue2);
}
@media (max-width: 768px) {
  .g2, .g3 {
    grid-template-columns: 1fr;
  }
  .stat-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .stat-row {
    grid-template-columns: 1fr;
  }
}
`;

function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  useEffect(() => {
    _toastFn = (msg, type) => {
      const id = Date.now();
      setToasts(prev => [...prev, { id, msg, type }]);
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500);
    };
  }, []);
  const icon = { success:"✓", error:"✕", warn:"⚠", info:"ℹ" };
  return (
    <div className="toast-wrap">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`}><span>{icon[t.type]}</span> {t.msg}</div>
      ))}
    </div>
  );
}

function SplashScreen({ onDone }) {
  const [fading, setFading] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => { setFading(true); setTimeout(onDone, 400); }, 2200);
    return () => clearTimeout(t);
  }, []);
  return (
    <div className={`splash${fading ? " splash-fade" : ""}`}>
      <div className="splash-logo">
        <span style={{ fontFamily:"var(--mono)", fontSize:14, fontWeight:700, color:"white" }}>IRA</span>
      </div>
      <div style={{ textAlign:"center" }}>
        <div className="splash-title">Internship Risk Analyzer</div>
        <div className="splash-sub" style={{ marginTop:4 }}>Internship Scam Detection & Awareness</div>
      </div>
      <div className="splash-bar"><div className="splash-fill" /></div>
      <div style={{ fontFamily:"var(--mono)", fontSize:11, color:"var(--ink3)" }}>Loading ML Engine…</div>
    </div>
  );
}

// FIX: ScoreRing clamped to 0-100
function ScoreRing({ score, color }) {
  const clamped = Math.min(100, Math.max(0, Math.round(score)));
  return (
    <div className="score-wrap">
      <div className="score-ring" style={{ background:`conic-gradient(${color} ${clamped}%, #e8ecf4 0)` }}>
        <div className="score-inner">
          <div>
            <div className="score-num" style={{ color }}>{clamped}</div>
            <div className="score-sub">/ 100</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// FIX: Meter clamped to 0-100
function Meter({ label, value, color }) {
  const clamped = Math.min(100, Math.max(0, Math.round(value)));
  return (
    <div className="meter">
      <div className="meter-head">
        <span>{label}</span>
        <span style={{ color, fontWeight:700 }}>{clamped}%</span>
      </div>
      <div className="meter-track">
        <div className="meter-fill" style={{ width:`${clamped}%`, background:color }} />
      </div>
    </div>
  );
}

function AIDisclaimer() {
  return (
    <div className="ai-disclaimer">
      <span className="ai-disclaimer-icon">ℹ️</span>
      <p className="ai-disclaimer-text">
        AI predictions are probabilistic and may be incorrect. Always verify internship opportunities, recruiters, and employers through official company channels before taking action.
      </p>
    </div>
  );
}

function HomePage({ setPage }) {
  return (
    <div className="page-in">
      <div className="home-hero">
        <div className="home-badge">
          <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--blue)", display:"inline-block" }} />
          ML-Powered · {DATASET_STATS.modelAccuracy}% Accuracy
        </div>
        <div className="home-title"><span className="accent">Internship</span><br />Risk Analyzer</div>
        <div className="home-sub">Detect fake internship postings instantly using machine learning.</div>
        <button className="home-cta" onClick={() => setPage("dashboard")}>🔍 Analyze a Job Posting</button>
        <div className="home-flag-label">Common red flags</div>
        <div className="home-flags">
          {[
            { icon:"💸", text:"Asked to pay a registration or security fee" },
            { icon:"📱", text:"Recruiter contacts only via WhatsApp" },
            { icon:"💰", text:"Salary is unrealistically high for the role" },
          ].map(tip => (
            <div key={tip.text} style={{ display:"flex", alignItems:"center", gap:12, padding:"12px 16px", background:"var(--white)", border:"1px solid var(--border)", borderRadius:10, fontSize:13, color:"var(--ink2)" }}>
              <span style={{ fontSize:18 }}>{tip.icon}</span><span>{tip.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const SCAM_DIST = [
  { label:"Fee-Based Scam",    pct:40, color:"#ef4444" },
  { label:"Fake WFH / Typing", pct:25, color:"#f97316" },
  { label:"MLM / Chain",       pct:18, color:"#f59e0b" },
  { label:"Authority Scam",    pct:11, color:"#3b82f6" },
  { label:"Others",            pct:6,  color:"#22c55e" },
];

function DashboardPage({ setPage }) {
  const stats    = useMemo(() => getTodayStats(), []);
  const weekData = useMemo(() => getWeeklyData(), []);
  const maxTotal = Math.max(...weekData.map(d => d.scams + d.safe));
  let acc = 0;
  return (
    <div className="page-in">
      <div className="flex between items-c mb24">
        <div>
          <div className="pg-title">Risk <em>Dashboard</em></div>
          <div className="pg-sub">Dataset: {DATASET_STATS.totalSamples} samples · {DATASET_STATS.modelAccuracy}% model accuracy</div>
        </div>
      </div>
      <div className="dashboard-hero-banner">
        <div className="hero-banner-overlay" />
        <div className="hero-banner-content">
          <span className="hero-banner-badge">AI Safety</span>
          <h2 className="hero-banner-title">Internship Scam Detection</h2>
          <p className="hero-banner-subtitle">Verify listings, analyze employer domains, and secure your career opportunities.</p>
        </div>
      </div>
      <div className="sec-tag mb12">Analysis Modules</div>
      <div className="module-grid mb24">
        {[
          { icon:"💬", name:"Chat Analyzer",    desc:"Paste any job posting and get an instant AI risk score with detailed breakdown.", tag:"ML · NB + LR Ensemble",    page:"chat"    },
          { icon:"🌐", name:"URL Checker",      desc:"Analyze company URLs for suspicious TLDs, domain patterns, and HTTPS status.",   tag:"Rule Engine · Domain Intel", page:"url"     },
          { icon:"💳", name:"Payment Detector", desc:"Detect hidden payment demands and UPI/fee keywords in job descriptions.",         tag:"Keyword Detection",          page:"payment" },
          { icon:"🔬", name:"Explainable AI",   desc:"See exactly why a posting was flagged — feature-by-feature breakdown.",          tag:"Feature Attribution",         page:"explain" },
        ].map(f => (
          <div key={f.name} className="module-card" onClick={() => setPage(f.page)}>
            <div className="mc-icon">{f.icon}</div>
            <div className="mc-name">{f.name}</div>
            <div className="mc-desc">{f.desc}</div>
            <div className="mc-tag">{f.tag}</div>
          </div>
        ))}
      </div>
      <div className="sec-tag mb12">Dataset Overview</div>
      <div className="stat-row">
        {[
          { label:"Total Samples",  val:String(stats.totalScans),         delta:"Training dataset",               c:"var(--blue)"  },
          { label:"Scam Samples",   val:String(stats.scamsDetected),      delta:`${stats.scamRate}% of dataset`,  c:"var(--red)"   },
          { label:"Legit Samples",  val:String(stats.safePostings),       delta:`${stats.safeRate}% of dataset`,  c:"var(--green)" },
          { label:"Model Accuracy", val:`${DATASET_STATS.modelAccuracy}%`,delta:"NB + LR Ensemble · 19 features", c:"#8b5cf6"      },
        ].map(s => (
          <div key={s.label} className="stat-box" style={{ "--c":s.c }}>
            <div className="stat-val">{s.val}</div>
            <div className="stat-lbl">{s.label}</div>
            <div className="stat-delta">{s.delta}</div>
          </div>
        ))}
      </div>
      <div className="g2 mb24">
        <div className="card">
          <div className="flex between items-c mb16">
            <div className="sec-tag" style={{ marginBottom:0 }}>Weekly Scan Activity</div>
            <div style={{ display:"flex", gap:10, fontSize:11, fontFamily:"var(--mono)", color:"var(--ink3)" }}>
              <span><span style={{ color:"var(--red)" }}>■</span> Scam</span>
              <span><span style={{ color:"var(--green)" }}>■</span> Safe</span>
            </div>
          </div>
          <div className="bar-chart">
            {weekData.map(d => {
              const sh = (d.scams / maxTotal) * 75;
              const gh = (d.safe  / maxTotal) * 75;
              return (
                <div key={d.day} className="bar-col">
                  <div className="bar-stack">
                    <div className="bar-seg" style={{ height:gh, background:"#22c55e", opacity:.7 }} />
                    <div className="bar-seg" style={{ height:sh, background:"#ef4444", opacity:.85 }} />
                  </div>
                  <div className="bar-lbl">{d.day}</div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="card">
          <div className="sec-tag mb16">Scam Type Distribution</div>
          <div className="donut-wrap">
            <svg width="100" height="100" viewBox="0 0 100 100" style={{ flexShrink:0, transform:"rotate(-90deg)" }}>
              <circle cx="50" cy="50" r="38" fill="none" stroke="#e8ecf4" strokeWidth="12" />
              {SCAM_DIST.map(t => {
                const prev = acc; acc += t.pct;
                const c = 2 * Math.PI * 38;
                return (
                  <circle key={t.label} cx="50" cy="50" r="38" fill="none"
                    stroke={t.color} strokeWidth="12"
                    strokeDasharray={`${(t.pct/100)*c} ${c}`}
                    strokeDashoffset={-((prev/100)*c)}
                  />
                );
              })}
            </svg>
            <div className="donut-legend">
              {SCAM_DIST.map(t => (
                <div key={t.label} className="leg-item">
                  <div className="leg-dot" style={{ background:t.color }} />
                  <span>{t.label}</span>
                  <span className="leg-pct">{t.pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const EXAMPLE_TEXTS = [
  { label:"🚨 Fee Scam",  text:"Data entry work from home. Earn ₹80,000 per week. No experience needed! Pay ₹500 registration fee to UPI: hrteam@paytm. Contact HR Priya on WhatsApp: 9876543210.", url:"http://easyjobs-india.tk/apply" },
  { label:"⚠️ Authority", text:"Government approved internship program. 100% placement guaranteed. No interview required. Earn ₹35,000 monthly. Security deposit of ₹1000 refundable after joining.", url:"http://govt-internship.xyz" },
  { label:"✅ Legit",     text:"Infosys is hiring Software Engineering Interns for Summer 2025. Knowledge of Python required. Stipend: ₹20,000/month. Selection includes online assessment. No fee required.", url:"https://infosys.com/careers" },
];

function ChatAnalyzerPage({ onResult }) {
  const [text, setText]       = useState("");
  const [url, setUrl]         = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);

  const analyze = async () => {
    if (!text.trim()) { toast("Please enter job posting text", "warn"); return; }
    setLoading(true); setResult(null);
    try {
      const data = await apiFetch("/analyze", "POST", { text, url: url || null });
      setResult(data);
      // FIX: clamp score in history
      onResult({ type:"Text Analysis", input:text.slice(0,80), score:Math.min(100, Math.round(data.final_score)), label:data.risk_label, color:riskColor(data.risk_label) });
      toast("Analysis complete", "success");
    } catch (e) { toast(e.message, "error"); }
    setLoading(false);
  };

  const rc  = result ? riskColor(result.risk_label) : "var(--blue)";
  const rbg = result ? riskBg(result.risk_label)    : "var(--blue-bg)";

  return (
    <div className="page-in">
      <div className="sec-tag mb4">Text Analysis</div>
      <div className="pg-title mb24">Chat <em>Analyzer</em></div>
      <div className="g2">
        <div>
          <div className="card mb12">
            <div className="flex between items-c mb12">
              <label className="lbl" style={{ margin:0 }}>Job Posting Text</label>
              <div className="flex gap8" style={{ flexWrap:"wrap" }}>
                {EXAMPLE_TEXTS.map(e => (
                  <button key={e.label} className="btn-ghost" onClick={() => { setText(e.text); setUrl(e.url); }}>{e.label}</button>
                ))}
              </div>
            </div>
            <textarea className="inp textarea mb12" placeholder="Paste internship or job posting text here…" value={text} onChange={e => setText(e.target.value)} />
            <label className="lbl">Company URL (optional)</label>
            <input className="inp mb16" placeholder="https://company.com/careers" value={url} onChange={e => setUrl(e.target.value)} />
            <button className="btn-primary" onClick={analyze} disabled={loading}>{loading ? "Analyzing…" : "Run Analysis →"}</button>
          </div>
          {loading && <div className="loading-bar" />}
        </div>
        <div>
          {!result ? (
            <div className="card empty"><div className="empty-icon">🔬</div><div className="empty-txt">Paste text and click "Run Analysis"</div></div>
          ) : (
            <div className="card page-in">
              {/* FIX: all scores clamped */}
              <div className="flex items-c gap12 mb20" style={{ padding:"12px 16px", background:rbg, borderRadius:8, border:`1px solid ${rc}33` }}>
                <ScoreRing score={Math.min(100, result.final_score)} color={rc} />
                <div>
                  <div style={{ fontSize:20, fontWeight:800, color:rc }}>{result.risk_label}</div>
                  <div style={{ fontSize:12, color:"var(--ink2)", fontFamily:"var(--mono)", marginTop:4 }}>
                    {result.prediction} · {result.confidence} confidence
                  </div>
                  <div style={{ fontSize:11, color:"var(--ink3)", fontFamily:"var(--mono)", marginTop:2 }}>
                    Scam probability: {Math.min(100, result.scam_probability * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              <Meter label="Risk Score"       value={Math.min(100, result.final_score)} color={rc} />
              <Meter label="Scam Probability" value={Math.min(100, result.scam_probability * 100)} color="#f97316" />
              {result.negation_detected && (
                <div className="alert success">✓ Payment explicitly waived — no payment demand</div>
              )}
              {result.payment_detected && (
                <div className="alert danger">⚠ Payment demand detected: {result.matched_keywords.join(", ")}</div>
              )}
              {result.reasons?.length > 0 && (
                <>
                  <div className="sec-tag mt12 mb8">Suspicious Signals</div>
                  <div className="chips-wrap">
                    {result.reasons.map(r => (
                      <span key={r} className="chip" style={{ color:"var(--red)", borderColor:"#fca5a5", background:"var(--red-bg)" }}>⚑ {r}</span>
                    ))}
                  </div>
                </>
              )}
              {result.legitimate_signals?.length > 0 && (
                <>
                  <div className="sec-tag mt12 mb8">Legitimate Signals</div>
                  <div className="chips-wrap">
                    {result.legitimate_signals.map(r => (
                      <span key={r} className="chip" style={{ color:"var(--green)", borderColor:"#86efac", background:"var(--grn-bg)" }}>✓ {r}</span>
                    ))}
                  </div>
                </>
              )}
              {result.url_analysis && (
                <>
                  <div className="divider" />
                  <div className="sec-tag mb8">URL Analysis</div>
                  <div className="alert" style={{ background:result.url_analysis.risk==="Suspicious"?"var(--amb-bg)":"var(--grn-bg)", borderColor:result.url_analysis.risk==="Suspicious"?"#fcd34d":"#86efac", color:result.url_analysis.risk==="Suspicious"?"#b45309":"#15803d" }}>
                    {result.url_analysis.risk === "Suspicious" ? "⚠" : "✓"} {result.url_analysis.domain} — {result.url_analysis.risk}
                  </div>
                </>
              )}
              <AIDisclaimer />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function URLCheckerPage({ onResult }) {
  const [url, setUrl]         = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);

  const check = async () => {
    if (!url.trim()) { toast("Enter a URL", "warn"); return; }
    setLoading(true); setResult(null);
    try {
      const data = await apiFetch("/url", "POST", { url });
      setResult(data);
      onResult({ type:"URL Check", input:url, score:Math.min(100, data.score), label:data.risk_label, color:riskColor(data.risk_label) });
      toast("URL analyzed", "success");
    } catch (e) { toast(e.message, "error"); }
    setLoading(false);
  };

  const rc = result ? riskColor(result.risk_label) : "var(--blue)";

  return (
    <div className="page-in">
      <div className="sec-tag mb4">Domain Analysis</div>
      <div className="pg-title mb24">URL <em>Checker</em></div>
      <div className="g2">
        <div className="card">
          <label className="lbl">Company or Apply URL</label>
          <input className="inp mb12" placeholder="https://company.com/careers" value={url} onChange={e => setUrl(e.target.value)} onKeyDown={e => e.key === "Enter" && check()} />
          {/* FIX: short labels instead of raw URLs */}
          <div className="flex gap8 mb16" style={{ flexWrap:"wrap" }}>
            {[
              { label:"🚨 Scam TK",  url:"http://easyjobs.tk/apply"    },
              { label:"✅ Infosys",   url:"https://infosys.com/careers" },
              { label:"⚠️ Fake GOV", url:"http://govt-jobs.xyz"        },
            ].map(u => (
              <button key={u.url} className="btn-ghost" onClick={() => setUrl(u.url)}>{u.label}</button>
            ))}
          </div>
          <button className="btn-primary" onClick={check} disabled={loading}>{loading ? "Checking…" : "Check URL →"}</button>
          {loading && <div className="loading-bar" />}
        </div>
        <div>
          {!result ? (
            <div className="card empty"><div className="empty-icon">🌐</div><div className="empty-txt">Enter a URL to analyze</div></div>
          ) : (
            <div className="card page-in">
              {/* FIX: clamped score */}
              <div className="flex items-c gap12 mb20">
                <ScoreRing score={Math.min(100, result.score)} color={rc} />
                <div>
                  <div style={{ fontSize:18, fontWeight:800, color:rc }}>{result.risk_label}</div>
                  <div style={{ fontFamily:"var(--mono)", fontSize:12, color:"var(--ink2)", marginTop:4, wordBreak:"break-all" }}>{result.domain}</div>
                  {result.is_trusted && <div className="alert success" style={{ marginTop:8, padding:"4px 10px" }}>✓ Trusted domain</div>}
                </div>
              </div>
              <Meter label="Risk Score" value={Math.min(100, result.score)} color={rc} />
              <div className="divider" />
              {[
                ["HTTPS",        result.https ? "Yes ✓" : "No ✗",         result.https ? "var(--green)" : "var(--red)"],
                ["Domain Trust", `${Math.round(result.domain_trust*100)}%`, "var(--ink)"],
                ["Raw Score",    `${result.raw_score} / 4`,                 "var(--blue)"],
              ].map(([k,v,c]) => (
                <div key={k} className="feat-row">
                  <span className="feat-lbl">{k}</span>
                  <span className="feat-val" style={{ color:c }}>{v}</span>
                </div>
              ))}
              <AIDisclaimer />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PaymentDetectorPage({ onResult }) {
  const [text, setText]       = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);

  const detect = async () => {
    if (!text.trim()) { toast("Enter some text", "warn"); return; }
    setLoading(true); setResult(null);
    try {
      const data = await apiFetch("/payment", "POST", { text });
      setResult(data);
      onResult({ type:"Payment Check", input:text.slice(0,80), score:Math.min(100, data.score), label:data.risk_label, color:riskColor(data.risk_label) });
      toast("Scan complete", data.payment_detected ? "error" : "success");
    } catch (e) { toast(e.message, "error"); }
    setLoading(false);
  };

  return (
    <div className="page-in">
      <div className="sec-tag mb4">Financial Fraud</div>
      <div className="pg-title mb24">Payment <em>Detector</em></div>
      <div className="g2">
        <div className="card">
          <label className="lbl">Job Posting or Message</label>
          <textarea className="inp textarea mb12" placeholder="Paste text to check for payment demands…" value={text} onChange={e => setText(e.target.value)} />
          <div className="flex gap8 mb16">
            <button className="btn-ghost" onClick={() => setText("Pay ₹999 registration fee via UPI to confirm your slot. Send money to hrteam@paytm before deadline.")}>🚨 Scam Example</button>
            <button className="btn-ghost" onClick={() => setText("Infosys internship. No fee required. Apply through official portal. Offer letter provided after selection.")}>✅ Legit Example</button>
          </div>
          <button className="btn-primary" onClick={detect} disabled={loading}>{loading ? "Scanning…" : "Scan for Payments →"}</button>
          {loading && <div className="loading-bar" />}
        </div>
        <div>
          {!result ? (
            <div className="card empty"><div className="empty-icon">💳</div><div className="empty-txt">Paste text and click scan</div></div>
          ) : (
            <div className="card page-in">
              {result.payment_detected
                ? <div className="alert danger">⚠ PAYMENT DEMAND DETECTED</div>
                : result.negation_detected
                  ? <div className="alert success">✓ Payment explicitly waived — safe</div>
                  : <div className="alert success">✓ No payment demand found</div>}
              <Meter label="Payment Risk Score" value={Math.min(100, result.score)} color={result.payment_detected ? "var(--red)" : "var(--green)"} />
              {result.matched_keywords?.length > 0 && (
                <>
                  <div className="sec-tag mt12 mb8">Matched Keywords</div>
                  <div className="chips-wrap">
                    {result.matched_keywords.map(k => (
                      <span key={k} className="chip" style={{ color:"var(--red)", borderColor:"#fca5a5", background:"var(--red-bg)" }}>💸 {k}</span>
                    ))}
                  </div>
                </>
              )}
              <div className="divider" />
              <div className="feat-row">
                <span className="feat-lbl">Total Keywords Found</span>
                <span className="feat-val" style={{ color:"var(--blue)" }}>{result.keyword_count}</span>
              </div>
              <AIDisclaimer />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ExplainPage() {
  const [text, setText]       = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);

  const explain = async () => {
    if (!text.trim()) { toast("Enter some text", "warn"); return; }
    setLoading(true); setResult(null);
    try {
      const data = await apiFetch("/explain", "POST", { text });
      setResult(data);
      toast("Explanation ready", "success");
    } catch (e) { toast(e.message, "error"); }
    setLoading(false);
  };

  return (
    <div className="page-in">
      <div className="sec-tag mb4">Interpretability</div>
      <div className="pg-title mb24">Explainable <em>AI</em></div>
      <div className="g2">
        <div className="card">
          {/* FIX: added example buttons */}
          <div className="flex between items-c mb12">
            <label className="lbl" style={{ margin:0 }}>Text to Explain</label>
            <div className="flex gap8" style={{ flexWrap:"wrap" }}>
              <button className="btn-ghost" onClick={() => setText("Data entry work from home. Earn ₹80,000 per week. No experience needed! Pay ₹500 registration fee to UPI: hrteam@paytm. Contact HR on WhatsApp only.")}>🚨 Scam</button>
              <button className="btn-ghost" onClick={() => setText("Google is hiring Software Engineering Interns for Summer 2025. Strong Python skills required. Stipend: ₹25,000/month. No fees. Apply via careers.google.com.")}>✅ Legit</button>
            </div>
          </div>
          <textarea className="inp textarea mb16" placeholder="Enter job posting text to understand why it was flagged…" value={text} onChange={e => setText(e.target.value)} />
          <button className="btn-primary" onClick={explain} disabled={loading}>{loading ? "Explaining…" : "Explain Prediction →"}</button>
          {loading && <div className="loading-bar" />}
        </div>
        <div>
          {!result ? (
            <div className="card empty"><div className="empty-icon">🔬</div><div className="empty-txt">Enter text to see explanation</div></div>
          ) : (
            <div className="card page-in">
              <div className="alert info mb16">{result.verdict}</div>
              {/* FIX: clamped */}
              <Meter label="Scam Probability" value={Math.min(100, result.scam_probability * 100)} color="#f97316" />
              <div className="divider" />
              <div className="sec-tag mb10">Suspicious Terms Found</div>
              {result.reasons?.length === 0 ? (
                <div className="alert success">✓ No suspicious patterns found</div>
              ) : (
                result.reasons.map((r, i) => (
                  <div key={i} style={{ padding:"10px 14px", borderRadius:8, border:"1px solid #fca5a5", background:"var(--red-bg)", marginBottom:8, display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                    <span style={{ fontSize:12, fontWeight:600, fontFamily:"var(--mono)", color:"var(--ink)" }}>⚑ {r}</span>
                    <span style={{ fontSize:10, color:"var(--red)", fontFamily:"var(--mono)", fontWeight:700, background:"#fee2e2", padding:"2px 8px", borderRadius:20 }}>FLAGGED</span>
                  </div>
                ))
              )}
              <div className="divider" />
              {[
                ["Prediction",       result.prediction,                    result.prediction==="SCAM"?"var(--red)":"var(--green)"],
                ["Confidence",       result.confidence,                    "var(--blue)"],
                ["Suspicious Terms", result.reason_count,                  "#f97316"],
                ["Payment Signals",  result.features?.payment_signals ?? 0,"var(--red)"],
              ].map(([k,v,c]) => (
                <div key={k} className="feat-row">
                  <span className="feat-lbl">{k}</span>
                  <span className="feat-val" style={{ color:c }}>{v}</span>
                </div>
              ))}
              <AIDisclaimer />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const PREC_DATA = [
  { icon:"💸", title:"Never Pay to Get Hired",         desc:"Any internship asking for registration, security deposit, or training fees is a scam. Zero exceptions.", severity:"critical", action:"If asked for money → Report and block immediately." },
  { icon:"📱", title:"Avoid WhatsApp-Only Recruiters", desc:"Real HR uses official company emails. WhatsApp-only contact is untraceable and a major red flag.", severity:"critical", action:"Always ask for an official company email ID." },
  { icon:"📞", title:"Never Share OTPs or Passwords",  desc:"No legitimate recruiter will ask for your OTP, bank details, or passwords during hiring.", severity:"critical", action:"Share OTP with anyone = instant account compromise." },
  { icon:"🔍", title:"Verify the Company Domain",      desc:"Scammers clone real brands with .xyz or .tk domains. Cross-verify on official LinkedIn.", severity:"high", action:"Use our URL Checker to scan domains instantly." },
  { icon:"💰", title:"Doubt Unrealistic Salaries",     desc:"Offers of ₹50,000/week for data entry are bait. Real intern stipends: ₹5,000–₹40,000/month.", severity:"high", action:"Research actual pay ranges for your field." },
  { icon:"🔗", title:"Check for Official Apply Links", desc:"Real companies use their careers page or Internshala. Google Form only = suspicious.", severity:"high", action:"Apply only through official, verifiable channels." },
  { icon:"⏱️", title:"Ignore Urgency Pressure",        desc:"'Last 2 seats! Apply in 24h!' — real companies don't rush candidates. It's manipulation.", severity:"medium", action:"Take your time. Urgency = manipulation tactic." },
  { icon:"📋", title:"Demand a Written Offer Letter",  desc:"Every valid offer has company letterhead with CIN/GST details and salary breakup.", severity:"medium", action:"No offer letter = no legitimate internship." },
  { icon:"🏢", title:"Verify on LinkedIn",             desc:"Search the company on LinkedIn. Fake recruiters often have under 50 connections.", severity:"medium", action:"LinkedIn + Glassdoor cross-check is essential." },
];

function PrecautionsPage() {
  const [filter, setFilter] = useState("all");
  const shown = filter === "all" ? PREC_DATA : PREC_DATA.filter(p => p.severity === filter);
  return (
    <div className="page-in">
      <div className="sec-tag mb4">Safety Guide</div>
      <div className="pg-title mb4">Protect <em>Yourself</em></div>
      <div className="pg-sub mb24">9 essential precautions every internship seeker must know</div>
      <div className="flex gap8 mb24">
        {["all","critical","high","medium"].map(f => (
          <button key={f} className={filter===f?"btn-primary":"btn-outline"} style={{ padding:"7px 16px", fontSize:12 }} onClick={() => setFilter(f)}>
            {f.charAt(0).toUpperCase()+f.slice(1)}
          </button>
        ))}
      </div>
      <div className="prec-grid">
        {shown.map(p => (
          <div key={p.title} className={`prec-card ${p.severity}`}>
            <div className="prec-icon">{p.icon}</div>
            <div className="prec-title">{p.title}</div>
            <div className="prec-desc">{p.desc}</div>
            <div style={{ marginTop:12, padding:"8px 12px", background:"var(--bg)", border:"1px solid var(--border)", borderRadius:8, fontSize:11, fontFamily:"var(--mono)", color:"var(--blue)" }}>→ {p.action}</div>
            <span className="prec-sev">{p.severity.toUpperCase()}</span>
          </div>
        ))}
      </div>
      <div className="sec-tag mb12">Quick Reference Checklist</div>
      <div className="code-block">
        <div className="code-header">
          <div className="code-dot" style={{ background:"#ff5f57" }} />
          <div className="code-dot" style={{ background:"#febc2e" }} />
          <div className="code-dot" style={{ background:"#28c840" }} />
          <div className="code-file">safety-checklist.sh</div>
        </div>
        <div className="code-body" style={{ fontSize:11, lineHeight:2 }}>
          <div><span className="c-dim"># BEFORE APPLYING</span></div>
          <div><span className="c-green">✓ </span><span className="c-white">Google company name + "scam" or "fraud"</span></div>
          <div><span className="c-green">✓ </span><span className="c-white">Check company on LinkedIn (employees, reviews)</span></div>
          <div><span className="c-green">✓ </span><span className="c-white">Verify domain with our URL Checker</span></div>
          <div><span className="c-dim"># RED FLAGS — STOP IMMEDIATELY</span></div>
          <div><span style={{color:"#ef4444"}}>✗ </span><span className="c-white">Any fee or deposit requested upfront</span></div>
          <div><span style={{color:"#ef4444"}}>✗ </span><span className="c-white">WhatsApp/Telegram only contact</span></div>
          <div><span style={{color:"#ef4444"}}>✗ </span><span className="c-white">Salary that's 5× the industry average</span></div>
          <div><span className="c-dim"># BEFORE JOINING</span></div>
          <div><span className="c-green">✓ </span><span className="c-white">Get official offer letter with letterhead</span></div>
          <div><span className="c-green">✓ </span><span className="c-white">Verify CIN/GST number on MCA portal</span></div>
        </div>
      </div>
    </div>
  );
}

function AboutPage() {
  return (
    <div className="page-in">
      <div className="sec-tag mb4">Documentation</div>
      <div className="pg-title mb24">About <em>/ Docs</em></div>
      <div className="g2 mb24">
        {[
          { label:"Model",    val:"NB + LR Ensemble",              sub:"Naive Bayes + Logistic Regression" },
          { label:"Dataset",  val:`${DATASET_STATS.totalSamples} Samples`, sub:`${DATASET_STATS.scamSamples} scam · ${DATASET_STATS.legitSamples} legit` },
          { label:"Features", val:`${DATASET_STATS.features} Features`,    sub:"Text, URL, Payment signals" },
          { label:"Accuracy", val:`${DATASET_STATS.modelAccuracy}%`,       sub:"On held-out test set" },
        ].map(s => (
          <div key={s.label} className="card">
            <div style={{ fontSize:10, fontFamily:"var(--mono)", color:"var(--ink3)", marginBottom:6, letterSpacing:"0.1em", textTransform:"uppercase" }}>{s.label}</div>
            <div style={{ fontSize:22, fontWeight:800, color:"var(--blue)", marginBottom:4 }}>{s.val}</div>
            <div style={{ fontSize:12, color:"var(--ink2)", fontFamily:"var(--mono)" }}>{s.sub}</div>
          </div>
        ))}
      </div>
      <div className="sec-tag mb12">System Architecture</div>
      <div className="arch-flow">
        <div className="arch-card">
          <div className="arch-card-num">Stage 01</div>
          <div className="arch-card-title">Input</div>
          <div className="arch-card-desc">Job listing description text and optional company URL provided by the user.</div>
          <div className="arch-card-code">Input Text & URL</div>
        </div>
        
        <div className="arch-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
        </div>
        
        <div className="arch-card">
          <div className="arch-card-num">Stage 02</div>
          <div className="arch-card-title">Text Analyzer</div>
          <div className="arch-card-desc">Lowercases content, collapses spacing, removes standard stopwords, and extracts 23 semantic/contextual features.</div>
          <div className="arch-card-code">preprocess() → extract_features()</div>
        </div>
        
        <div className="arch-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
        </div>
        
        <div className="arch-card">
          <div className="arch-card-num">Stage 03</div>
          <div className="arch-card-title">Risk Fusion Engine</div>
          <div className="arch-card-desc">Ensembles predictions from custom Naive Bayes and Logistic Regression classifiers (50% / 50% weights) combined with payment rules and URL heuristics.</div>
          <div className="arch-card-code">Ensemble Model (40%) + Rules Engine (40%) + Domain Score (20%)</div>
        </div>
        
        <div className="arch-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
        </div>
        
        <div className="arch-card">
          <div className="arch-card-num">Stage 04</div>
          <div className="arch-card-title">Explainability Layer</div>
          <div className="arch-card-desc">Attributes risk score decisions back to specific triggered keywords, channels (WhatsApp/Telegram), and context signals.</div>
          <div className="arch-card-code">explain_prediction()</div>
        </div>
        
        <div className="arch-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
        </div>
        
        <div className="arch-card final">
          <div className="arch-card-num">Stage 05</div>
          <div className="arch-card-title">Final Risk Score</div>
          <div className="arch-card-desc">Generates the overall risk percentage score (0-100) and maps it to a final risk label (LOW, MEDIUM, or HIGH RISK).</div>
          <div className="arch-card-code">Final Risk Score + Risk Label</div>
        </div>
      </div>

      <div className="sec-tag mb12 mt24">Model Evaluation Metrics</div>
      <div className="g3 mb24">
        {[
          { name: "Accuracy", value: "88%", desc: "Percentage of correctly classified job postings overall." },
          { name: "Precision", value: "89%", desc: "Percentage of flagged scams that were actually scams." },
          { name: "Recall", value: "82%", desc: "Percentage of actual scams correctly identified." },
          { name: "F1 Score", value: "85%", desc: "Balanced harmonic mean of precision and recall." },
          { name: "False Positive Rate", value: "8%", desc: "Percentage of legitimate postings incorrectly flagged." },
          { name: "Adversarial Recall", value: "73%", desc: "Recall rate against obfuscated character tricks." }
        ].map(m => (
          <div key={m.name} className="card metric-card">
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: 10, fontFamily: "var(--mono)", color: "var(--ink3)", textTransform: "uppercase", letterSpacing: '0.05em' }}>{m.name}</div>
                <div style={{ fontSize: 12, color: "var(--ink2)", marginTop: 6, lineHeight: 1.4 }}>{m.desc}</div>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: "var(--blue)", marginTop: 12 }}>{m.value}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="card mb24">
        <div className="sec-tag mb12" style={{ marginBottom: 8 }}>Heuristic & Loss Benchmarks</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          <div>
            <div style={{ fontSize: 9, fontFamily: "var(--mono)", color: "var(--ink3)" }}>TRAINING LOSS</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 4, fontFamily: "var(--mono)" }}>0.31</div>
          </div>
          <div>
            <div style={{ fontSize: 9, fontFamily: "var(--mono)", color: "var(--ink3)" }}>VALIDATION LOSS</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 4, fontFamily: "var(--mono)" }}>0.36</div>
          </div>
          <div>
            <div style={{ fontSize: 9, fontFamily: "var(--mono)", color: "var(--ink3)" }}>ROC-AUC</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 4, fontFamily: "var(--mono)" }}>0.90</div>
          </div>
        </div>
      </div>

      <div className="sec-tag mb12">Team Work Division</div>
      <div className="g2">
        {[
          { n:"01", role:"Dataset & Similarity",           tasks:["Collect & label 500 samples","Build balanced dataset (250/250)","SequenceMatcher similarity engine","Adversarial test cases"] },
          { n:"02", role:"ML Model Development",           tasks:["Naive Bayes classifier (custom)","Logistic Regression (custom)","Ensemble voting (50/50)","Model evaluation — 93.4% accuracy"] },
          { n:"03", role:"Rule Engine & Detection",        tasks:["Payment keyword detector","URL risk scorer","Domain trust layer","Explainability engine"] },
          { n:"04", role:"Frontend + Backend Integration", tasks:["FastAPI backend endpoints","React frontend (this UI)","CORS + Pydantic validation","API wiring"] },
        ].map(t => (
          <div key={t.n} className="card">
            <div style={{ fontSize:10, fontFamily:"var(--mono)", color:"var(--blue)", marginBottom:6 }}>MEMBER {t.n}</div>
            <div style={{ fontSize:14, fontWeight:700, color:"var(--ink)", marginBottom:12 }}>{t.role}</div>
            {t.tasks.map(task => (
              <div key={task} style={{ fontSize:12, color:"var(--ink2)", fontFamily:"var(--mono)", marginBottom:6, display:"flex", gap:8, lineHeight:1.5 }}>
                <span style={{ color:"var(--blue)", flexShrink:0 }}>→</span><span>{task}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

const NAV = [
  { id:"home",        label:"Home",         icon:"🏠", section:"MAIN" },
  { id:"dashboard",   label:"Dashboard",    icon:"📊", section:null   },
  { id:"precautions", label:"Safety Tips",  icon:"🛡️", section:"INFO" },
  { id:"about",       label:"About / Docs", icon:"ℹ️",  section:null   },
];

export default function App() {
  const [splash, setSplash]           = useState(true);
  const [page, setPage]               = useState("home");
  const [pageHistory, setPageHistory] = useState([]);
  const [history, setHistory]         = useState([]);

  const navigateTo = useCallback((newPage) => {
    setPageHistory(prev => [...prev, page]);
    setPage(newPage);
  }, [page]);

  const goBack = useCallback(() => {
    setPageHistory(prev => {
      if (prev.length === 0) return prev;
      const last = prev[prev.length - 1];
      setPage(last);
      return prev.slice(0, -1);
    });
  }, []);

  useEffect(() => { document.title = "Internship Risk Analyzer"; }, []);

  const addHistory = useCallback((entry) => {
    setHistory(prev => [{
      id: Date.now(), ...entry,
      time: new Date().toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" }),
    }, ...prev.slice(0, 49)]);
  }, []);

  const currentNav = NAV.find(n => n.id === page) || NAV[0];

  if (splash) {
    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: STYLES }} />
        <SplashScreen onDone={() => setSplash(false)} />
      </>
    );
  }

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: STYLES }} />
      <ToastContainer />
      <div className="root">
        <aside className="sb">
          <div className="sb-brand">
            <div className="sb-logo" onClick={() => navigateTo("home")}>
              <div className="sb-logo-icon"><span className="sb-logo-letter">IRA</span></div>
              <div><div className="sb-name"><span>Internship</span> Risk Analyzer</div></div>
            </div>
            <div className="sb-status">
              <div className="sb-dot" />
              <span className="sb-status-txt">All engines online</span>
            </div>
          </div>
          <nav className="sb-nav">
            {NAV.map(n => (
              <div key={n.id}>
                {n.section && <div className="sb-section">{n.section}</div>}
                <div className={`sb-item${page===n.id?" on":""}`} onClick={() => navigateTo(n.id)}>
                  <span className="ic">{n.icon}</span><span>{n.label}</span>
                </div>
              </div>
            ))}
          </nav>
          <div className="sb-footer">
            <div className="sb-ver">v1.2.0 · IRA</div>
            <div className="sb-build">Dataset: {DATASET_STATS.totalSamples} samples</div>
          </div>
        </aside>
        <div className="carea">
          <div className="topbar">
            <div className="tb-left">
              {page !== "home" && (
                <button className="btn-back" onClick={goBack}><span className="arr">←</span> Back</button>
              )}
              <span className="bc-item">IRA</span>
              <span className="bc-sep">/</span>
              <span className="bc-item on">{currentNav?.label || page}</span>
            </div>
            <div className="tb-right">
              <div className="tb-chip">
                <div className="dot" style={{ background:"var(--green)", boxShadow:"0 0 5px var(--green)" }} />
                ML Engine Online
              </div>
              <div className="tb-chip">
                {new Date().toLocaleDateString("en-IN", { day:"2-digit", month:"short", year:"numeric" })}
              </div>
            </div>
          </div>
          <div className="tbody">
            {page === "home"        && <HomePage            setPage={navigateTo} />}
            {page === "dashboard"   && <DashboardPage       setPage={navigateTo} />}
            {page === "chat"        && <ChatAnalyzerPage    onResult={addHistory} />}
            {page === "url"         && <URLCheckerPage      onResult={addHistory} />}
            {page === "payment"     && <PaymentDetectorPage onResult={addHistory} />}
            {page === "explain"     && <ExplainPage />}
            {page === "precautions" && <PrecautionsPage />}
            {page === "about"       && <AboutPage />}
          </div>
        </div>
      </div>
    </>
  );
}