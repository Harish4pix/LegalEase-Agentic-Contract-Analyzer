export default function RiskGauge({ score = 0, level = 'low' }) {
  const angle = Math.max(0, Math.min(100, score)) * 3.6
  return (
    <div className={`risk-gauge ${level}`} style={{ '--score-angle': `${angle}deg` }}>
      <div className="risk-gauge__inner">
        <strong>{score}</strong>
        <span>/ 100</span>
      </div>
    </div>
  )
}
