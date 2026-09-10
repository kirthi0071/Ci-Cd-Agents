import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const deployments = [
  ['payment-api', 'production', 'SUCCESS', '2m ago'],
  ['analytics-api', 'production', 'SUCCESS', '8m ago'],
  ['user-api', 'production', 'FAILED', '14m ago'],
  ['inventory-api', 'production', 'SUCCESS', '21m ago'],
];

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">AI</span><div><strong>CI/CD Platform</strong><small>Platform Engineering</small></div></div>
        <nav>
          {['Overview', 'Deployments', 'Incidents', 'Services', 'AI Agent', 'Audit Logs'].map((item, i) => <div className={`nav-item ${i === 0 ? 'active' : ''}`} key={item}><span>{['⌂','↗','⚠','◈','✦','≡'][i]}</span>{item}</div>)}
        </nav>
        <div className="sidebar-footer">Production<br/><span>asia-south1</span></div>
      </aside>

      <main className="content">
        <header className="topbar"><div><p className="eyebrow">PLATFORM OVERVIEW</p><h1>Deployment Command Center</h1></div><div className="user-chip"><span className="status-dot"/> System healthy <b>KM</b></div></header>

        <section className="metrics">
          <Metric label="Deployments" value="24" detail="Last 24 hours" />
          <Metric label="Successful" value="21" detail="87.5% success rate" />
          <Metric label="Failed" value="3" detail="Requires attention" danger />
          <Metric label="AI Investigations" value="1" detail="1 active incident" accent />
        </section>

        <section className="grid-main">
          <div className="panel deployments"><div className="panel-header"><div><p className="eyebrow">DELIVERY</p><h2>Recent deployments</h2></div><button>View all →</button></div>
            <div className="table">{deployments.map(([service, env, status, time]) => <div className="row" key={service}><div><strong>{service}</strong><span>{env}</span></div><Status status={status}/><span className="muted">{time}</span></div>)}</div>
          </div>

          <div className="panel incident"><div className="panel-header"><div><p className="eyebrow">AI INVESTIGATION</p><h2>Active incident</h2></div><span className="severity">HIGH</span></div>
            <div className="incident-title"><span className="failure-icon">!</span><div><strong>INC-1024 · user-api</strong><p>Cloud Run revision failed startup checks</p></div></div>
            <div className="progress"><div className="progress-label"><span>Investigation progress</span><b>82%</b></div><div className="bar"><i/></div></div>
            <div className="steps"><Step done text="GitHub Actions logs collected"/><Step done text="Cloud Run revision inspected"/><Step done text="Cloud Logging queried"/><Step text="Correlating evidence"/></div>
            <button className="primary">Open investigation →</button>
          </div>
        </section>

        <section className="panel activity"><div className="panel-header"><div><p className="eyebrow">OBSERVABILITY</p><h2>Platform activity</h2></div><span className="live"><i/> LIVE</span></div><div className="activity-list"><Activity time="20:31:57" text="AI agent identified a Cloud Run startup failure"/><Activity time="20:31:53" text="Cloud Logging evidence collected for INC-1024"/><Activity time="20:31:49" text="GitHub Actions deployment failure received"/><Activity time="20:31:31" text="Cloud Run deployment started for user-api"/></div></section>
      </main>
    </div>
  );
}

function Metric({label,value,detail,danger,accent}:{label:string;value:string;detail:string;danger?:boolean;accent?:boolean}) { return <div className={`metric ${danger?'danger':''} ${accent?'accent':''}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div> }
function Status({status}:{status:string}) { return <span className={`status ${status.toLowerCase()}`}><i/> {status}</span> }
function Step({done,text}:{done?:boolean;text:string}) { return <div className="step"><span className={done?'check':'pending'}>{done?'✓':'•'}</span>{text}</div> }
function Activity({time,text}:{time:string;text:string}) { return <div className="activity-row"><time>{time}</time><span>{text}</span></div> }

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
