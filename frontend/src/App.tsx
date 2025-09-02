import Header from './components/Header';
import ScrapingDashboard from './components/ScrapingDashboard';
import ClusteringInterface from './components/ClusteringInterface';
import './App.css';

function App() {
  return (
    <>
      <Header />
      <main className="container py-4">
        <div className="row g-4">
          <div className="col-lg-6">
            <ScrapingDashboard />
          </div>
          <div className="col-lg-6">
            <ClusteringInterface />
          </div>
        </div>
      </main>
    </>
  );
}

export default App;