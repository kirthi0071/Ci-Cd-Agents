import { useEffect, useState } from 'react';
import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'https://ai-cicd-agent-jeal5mhmha-el.a.run.app').replace(/\/$/, '');

type Overview = {
  deployments: { total: number; successful: number; failed: number };
  active_incidents: number;
  ai_investigations: number;
};

type Incident = {
  id: string;
  service: string;
  environment: string;
  severity: string;
  status: string;
  summary: string;
};

function App() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [overviewResponse, incidentsResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/overview`),
          fetch(`${API_BASE_URL}/api/v1/incidents`),
        ]);

        if (!overviewResponse.ok) {
          throw new Error(`Overview API returned ${overviewResponse.status}`);
        }
        if (!incidentsResponse.ok) {
          throw new Error(`Incidents API returned ${incidentsResponse.status}`);
        }

        const [overviewData, incidentsData] = await Promise.all([
          overviewResponse.json() as Promise<Overview>,
          incidentsResponse.json() as Promise<Incident[]>,
        ]);

        setOverview(overviewData);
        setIncidents(incidentsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load dashboard data');
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  const deploymentTotal = overview?.deployments.total ?? 0;
  const successful = overview?.deployments.successful ?? 0;
  const failed = overview?.deployments.failed ?? 0;
  const successRate = deploymentTotal ? ((successful / deploymentTotal) * 100).toFixed(1) : '0.0';
  const activeIncident = incidents[0];

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

        {error && <div className="api-error">Backend connection failed: {error}</div>}

        <section className="metrics">
          <Metric label="Deployments" value={loading ? '—' : String(deploymentTotal)} detail="Last 24 hours" />
          <Metric label="Successful" value={loading ? '—' : String(successful)} detail={loading ? 'Loading API data' : `${successRate}% success rate`} />
          <Metric label="Failed" value={loading ? '—' : String(failed)} detail={loading ? 'Loading API data' : 'Requires attention'} danger />
          <Metric label="AI Investigations" value={loading ? '—' : String(overview?.ai_investigations ?? 0)} detail={loading ? 'Loading API data' : `${overview?.active_incidents ?? 0} active incident`} accent />
        </section>

        <section className="grid-main">
          <div className="panel deployments"><div className="panel-header"><div><p className="eyebrow">DELIVERY</p><h2>Recent deployments</h2></div><button>View all →</button></div>
            <div className="table">
              {loading ? <div className="empty-state">Loading deployment data from FastAPI…</div> : <div className="empty-state">Deployment history API is the next backend slice.</div>}
            </div>
          </div>

          <div className="panel incident"><div className="panel-header"><div><p className="eyebrow">AI INVESTIGATION</p><h2>Active incident</h2></div><span className="severity">{activeIncident?.severity ?? '—'}</span></div>
            {loading ? <div className="empty-state">Loading incident data from FastAPI…</div> : activeIncident ? <>
              <div className="incident-title"><span className="failure-icon">!</span><div><strong>{activeIncident.id} · {activeIncident.service}</strong><p>{activeIncident.summary}</p></div></div>
              <div className="incident-meta"><span>{activeIncident.environment}</span><span>{activeIncident.status}</span></div>
              <div className="progress"><div className="progress-label"><span>Investigation progress</span><b>Not started</b></div><div className="bar"><i style={{ width: '0%' }}/></div></div>
              <div className="steps"><Step text="Incident received from backend"/><Step text="Evidence collection not started"/><Step text="AI diagnosis not started"/></div>
              <button className="primary">Open investigation →</button>
            </> : <div className="empty-state">No active incidents.</div>}
          </div>
        </section>

        <section className="panel activity"><div className="panel-header"><div><p className="eyebrow">OBSERVABILITY</p><h2>Platform activity</h2></div><span className="live"><i/> LIVE</span></div><div className="activity-list">
          <Activity time="—" text="Dashboard data is now loaded from the FastAPI backend"/>
          <Activity time="—" text="GitHub Actions → Cloud Run deployment is operational"/>
          <Activity time="—" text="AI investigation pipeline will be connected in the next phase"/>
        </div></section>
      </main>
    </div>
  );
}

function Metric({label,value,detail,danger,accent}:{label:string;value:string;detail:string;danger?:boolean;accent?:boolean}) { return <div className={`metric ${danger?'danger':''} ${accent?'accent':''}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div> }
function Step({done,text}:{done?:boolean;text:string}) { return <div className="step"><span className={done?'check':'pending'}>{done?'✓':'•'}</span>{text}</div> }
function Activity({time,text}:{time:string;text:string}) { return <div className="activity-row"><time>{time}</time><span>{text}</span></div> }

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
