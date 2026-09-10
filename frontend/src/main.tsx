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

type Deployment = {
  id: number;
  workflow: string;
  service: string;
  environment: string;
  status: string;
  conclusion: string | null;
  branch: string;
  commit: string;
  time: string;
  created_at?: string;
  url: string | null;
};

type DeploymentStep = {
  number: number | null;
  name: string;
  status: string | null;
  conclusion: string | null;
  started_at: string | null;
  completed_at: string | null;
};

type DeploymentJob = {
  id: number;
  name: string;
  status: string | null;
  conclusion: string | null;
  started_at: string | null;
  completed_at: string | null;
  url: string | null;
  steps: DeploymentStep[];
};

type DeploymentDetails = {
  deployment: Deployment | null;
  jobs: DeploymentJob[];
};

function App() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [selectedDeployment, setSelectedDeployment] = useState<Deployment | null>(null);
  const [details, setDetails] = useState<DeploymentDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [overviewResponse, incidentsResponse, deploymentsResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/overview`),
          fetch(`${API_BASE_URL}/api/v1/incidents`),
          fetch(`${API_BASE_URL}/api/v1/deployments`),
        ]);

        if (!overviewResponse.ok) throw new Error(`Overview API returned ${overviewResponse.status}`);
        if (!incidentsResponse.ok) throw new Error(`Incidents API returned ${incidentsResponse.status}`);
        if (!deploymentsResponse.ok) throw new Error(`Deployments API returned ${deploymentsResponse.status}`);

        const [overviewData, incidentsData, deploymentsData] = await Promise.all([
          overviewResponse.json() as Promise<Overview>,
          incidentsResponse.json() as Promise<Incident[]>,
          deploymentsResponse.json() as Promise<Deployment[]>,
        ]);

        setOverview(overviewData);
        setIncidents(incidentsData);
        setDeployments(deploymentsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load dashboard data');
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  async function openDeployment(deployment: Deployment) {
    setSelectedDeployment(deployment);
    setDetails(null);
    setDetailsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/deployments/${deployment.id}`);
      if (!response.ok) throw new Error(`Deployment details API returned ${response.status}`);
      const data = (await response.json()) as DeploymentDetails;
      setDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load deployment details');
    } finally {
      setDetailsLoading(false);
    }
  }

  function closeDeployment() {
    setSelectedDeployment(null);
    setDetails(null);
  }

  const deploymentTotal = overview?.deployments.total ?? 0;
  const successful = overview?.deployments.successful ?? 0;
  const failed = overview?.deployments.failed ?? 0;
  const successRate = deploymentTotal ? ((successful / deploymentTotal) * 100).toFixed(1) : '0.0';
  const activeIncident = incidents[0];

  if (selectedDeployment) {
    return (
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand"><span className="brand-mark">AI</span><div><strong>CI/CD Platform</strong><small>Platform Engineering</small></div></div>
          <nav>
            {['Overview', 'Deployments', 'Incidents', 'Services', 'AI Agent', 'Audit Logs'].map((item, i) => <div className={`nav-item ${i === 1 ? 'active' : ''}`} key={item}><span>{['⌂','↗','⚠','◈','✦','≡'][i]}</span>{item}</div>)}
          </nav>
          <div className="sidebar-footer">Production<br/><span>asia-south1</span></div>
        </aside>

        <main className="content">
          <header className="topbar">
            <div>
              <button className="back-button" onClick={closeDeployment}>← Back to deployments</button>
              <p className="eyebrow">DELIVERY EVIDENCE</p>
              <h1>Deployment Details</h1>
            </div>
            <div className="user-chip"><span className="status-dot"/> System healthy <b>KM</b></div>
          </header>

          {error && <div className="api-error">Backend connection failed: {error}</div>}

          <section className="deployment-hero panel">
            <div>
              <p className="eyebrow">GITHUB ACTIONS RUN</p>
              <h2 className="deployment-title">{selectedDeployment.workflow}</h2>
              <div className="deployment-identifiers">
                <span>Run #{selectedDeployment.id}</span>
                <span>{selectedDeployment.branch}</span>
                <span className="mono">{selectedDeployment.commit}</span>
                <span>{selectedDeployment.environment}</span>
              </div>
            </div>
            <Status status={selectedDeployment.status}/>
          </section>

          <section className="panel evidence-panel">
            <div className="panel-header">
              <div><p className="eyebrow">EXECUTION EVIDENCE</p><h2>Jobs & steps</h2></div>
              {selectedDeployment.url && <a className="external-link" href={selectedDeployment.url} target="_blank" rel="noreferrer">Open GitHub run ↗</a>}
            </div>

            {detailsLoading ? <div className="empty-state">Loading GitHub Actions job evidence…</div> : details?.jobs.length ? details.jobs.map((job) => (
              <div className="job-card" key={job.id}>
                <div className="job-header">
                  <div><strong>{job.name}</strong><span>Job #{job.id}</span></div>
                  <Status status={job.conclusion === 'success' ? 'SUCCESS' : job.status === 'completed' ? 'FAILED' : 'RUNNING'}/>
                </div>
                <div className="step-list">
                  {job.steps.map((step) => <div className="evidence-step" key={`${job.id}-${step.number}-${step.name}`}>
                    <span className={`step-icon ${step.conclusion === 'success' ? 'success' : step.conclusion === 'failure' ? 'failure' : 'pending'}`}>
                      {step.conclusion === 'success' ? '✓' : step.conclusion === 'failure' ? '!' : '•'}
                    </span>
                    <div><strong>{step.name}</strong><span>{step.status === 'completed' ? (step.conclusion || 'completed') : (step.status || 'pending')}</span></div>
                  </div>)}
                </div>
              </div>
            )) : <div className="empty-state">No GitHub Actions job evidence returned.</div>}
          </section>

          <section className="panel evidence-summary">
            <div className="panel-header"><div><p className="eyebrow">AGENT INPUT</p><h2>Evidence summary</h2></div></div>
            <div className="evidence-grid">
              <Evidence label="Source" value="GitHub Actions" />
              <Evidence label="Workflow" value={selectedDeployment.workflow} />
              <Evidence label="Commit" value={selectedDeployment.commit} mono />
              <Evidence label="Environment" value={selectedDeployment.environment} />
            </div>
            <p className="evidence-note">This execution evidence is the input layer for the future AI investigation pipeline. Diagnosis and remediation are intentionally not performed on this page.</p>
          </section>
        </main>
      </div>
    );
  }

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
          <div className="panel deployments"><div className="panel-header"><div><p className="eyebrow">DELIVERY</p><h2>Recent deployments</h2></div><button onClick={() => deployments[0] && openDeployment(deployments[0])}>View details →</button></div>
            <div className="table">
              {loading ? <div className="empty-state">Loading deployment data from GitHub Actions…</div> : deployments.length === 0 ? <div className="empty-state">No GitHub Actions deployments found.</div> : deployments.slice(0, 6).map((deployment) => (
                <button className="row row-button" key={deployment.id} onClick={() => openDeployment(deployment)}>
                  <div><strong>{deployment.service}</strong><span>{deployment.workflow} · {deployment.branch} · {deployment.commit}</span></div>
                  <Status status={deployment.status}/>
                  <span className="muted">{deployment.time}</span>
                </button>
              ))}
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
          <Activity time="LIVE" text="Deployment history is loaded from GitHub Actions"/>
          <Activity time="LIVE" text="Dashboard metrics are loaded from FastAPI"/>
          <Activity time="NEXT" text="Deployment details expose jobs and steps as evidence"/>
        </div></section>
      </main>
    </div>
  );
}

function Metric({label,value,detail,danger,accent}:{label:string;value:string;detail:string;danger?:boolean;accent?:boolean}) { return <div className={`metric ${danger?'danger':''} ${accent?'accent':''}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div> }
function Status({status}:{status:string}) { return <span className={`status ${status.toLowerCase()}`}><i/> {status}</span> }
function Step({done,text}:{done?:boolean;text:string}) { return <div className="step"><span className={done?'check':'pending'}>{done?'✓':'•'}</span>{text}</div> }
function Activity({time,text}:{time:string;text:string}) { return <div className="activity-row"><time>{time}</time><span>{text}</span></div> }
function Evidence({label,value,mono}:{label:string;value:string;mono?:boolean}) { return <div className="evidence-item"><span>{label}</span><strong className={mono?'mono':''}>{value}</strong></div> }

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
