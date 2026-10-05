const API="http://127.0.0.1:5000/api";
const $=id=>document.getElementById(id);
const esc=v=>String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
const bytes=n=>{n=Number(n||0);if(!n)return"0 B";let u=["B","KB","MB","GB"],i=Math.min(Math.floor(Math.log(n)/Math.log(1024)),3);return`${(n/1024**i).toFixed(i?1:0)} ${u[i]}`};
const time=s=>{let d=new Date(s);return isNaN(d)?"—":d.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"})};
function toast(s){let t=$("toast");t.textContent=s;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2500)}
function table(es){if(!es.length)return'<div class="empty">No activity recorded yet.</div>';return`<table class="table"><tr><th>TIME</th><th>DEVICE</th><th>EVENT</th><th>FILE</th><th>SIZE</th><th>RISK</th></tr>${es.map(e=>`<tr><td>${time(e.timestamp)}</td><td>${esc(e.device)}</td><td>${esc(e.event_type)}</td><td>${esc(e.path)}</td><td>${bytes(e.size_bytes)}</td><td><span class="risk ${e.risk}">${e.risk}</span></td></tr>`).join("")}</table>`}
function render(d){$("devicesN").textContent=d.stats.devices;$("eventsN").textContent=d.stats.events;$("alertsN").textContent=d.stats.alerts;$("highN").textContent=d.stats.high_risk;
$("deviceList").innerHTML=d.devices.length?d.devices.map(x=>`<div class="device"><div><strong>▣ ${esc(x.name)}</strong><small>${esc(x.mountpoint)} · ${esc(x.protocol)}</small></div><span class="connected">CONNECTED</span></div>`).join(""):'<div class="empty">No external volumes detected.</div>';
$("allDevices").innerHTML=d.devices.length?d.devices.map(x=>`<article class="card"><h3>${esc(x.name)}</h3><p>Mount: ${esc(x.mountpoint)}</p><p>Device: ${esc(x.device_id)}</p><p>Protocol: ${esc(x.protocol)}</p><p>Connected: ${esc(x.connected_at)}</p></article>`).join(""):'<div class="empty">Connect a USB storage device.</div>';
$("recent").innerHTML=table(d.events.slice(0,8));$("allEvents").innerHTML=table(d.events);
$("allAlerts").innerHTML=d.alerts.length?d.alerts.map(x=>`<article class="alert ${x.risk.toLowerCase()}"><strong>${esc(x.device)} · ${esc(x.event_type)} <span class="risk ${x.risk}">${x.risk}</span></strong><p>${esc(x.details)}</p><p>${esc(x.path)} · ${time(x.timestamp)}</p></article>`).join(""):'<div class="empty">No medium or high-risk events.</div>';
$("updated").textContent="Updated "+new Date().toLocaleTimeString()}
async function load(){try{let r=await fetch(API+"/state");if(!r.ok)throw 0;render(await r.json())}catch{$("updated").textContent="Backend offline"}}
async function post(path,msg){try{await fetch(API+path,{method:"POST"});toast(msg);load()}catch{toast("Start the Python backend first.")}}
document.querySelectorAll(".nav").forEach(b=>b.onclick=()=>{document.querySelectorAll(".nav").forEach(x=>x.classList.remove("active"));document.querySelectorAll(".page").forEach(x=>x.classList.remove("active"));b.classList.add("active");$(b.dataset.page).classList.add("active")});
document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>document.querySelector(`[data-page="${b.dataset.go}"]`).click());
$("scan").onclick=()=>post("/scan","OS volume scan completed.");$("demo").onclick=()=>post("/demo/bulk","Demo HIGH-risk event added.");
load();setInterval(load,1000);
