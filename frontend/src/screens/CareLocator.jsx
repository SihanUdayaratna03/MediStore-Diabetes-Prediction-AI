import TopBar from '../components/ui/TopBar'
import CareMap from '../components/maps/CareMap'
import '../components/maps/CareMap.css'

export default function CareLocator({ onBack, riskLevel = 'all', preselectedCategory = 'all' }) {
  return (
    <div className="ms-care-locator-page">
      <TopBar moduleName="Care &amp; Diabetic Supply Network" accent="sky" onBack={onBack} />
      <main className="ms-care-locator-main">
        <CareMap riskLevel={riskLevel} preselectedCategory={preselectedCategory} />
      </main>
    </div>
  )
}