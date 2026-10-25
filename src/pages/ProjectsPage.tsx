import { useNavigate } from 'react-router-dom'
import brainSymbol from '../assets/brand/brainmint-bg-logo.png'
import styles from './ProjectsPage.module.css'

interface VerticalItem {
  id: string
  title: string
  description: string
  iconType: 'cross' | 'users' | 'phone'
}

const VERTICAL_ITEMS: VerticalItem[] = [
  {
    id: 'ai-automation',
    title: 'Enterprise AI & Automation',
    description: 'Custom LLMs, multi-agent workflows, and scalable machine learning pipelines engineered for seamless integration',
    iconType: 'cross',
  },
  {
    id: 'custom-software',
    title: 'Custom Software Engineering',
    description: 'Complete lifecycle support covering architectural design, model fine- tuning, cloud deployment, and system scaling.',
    iconType: 'users',
  },
  {
    id: 'management-consulting',
    title: 'Management Consulting',
    description: 'Direct access to experienced AI strategists, cloud architects, and software leaders.',
    iconType: 'phone',
  },
  {
    id: 'security-compliance',
    title: 'Enterprise Security & Compliance',
    description: 'SOC2-aligned development standards, strict data governance, and secure infrastructure options.',
    iconType: 'phone',
  },
  {
    id: 'alliance-partner',
    title: 'Alliance Partner Program',
    description: 'Program drives strategic co- innovation, ecosystem integration, and technology alliances by co-developing and integrating enterprise solutions alongside tech vendors while expanding market reach through joint technical execution',
    iconType: 'phone',
  },
]

function CrossIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

function UsersIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
    </svg>
  )
}

function PhoneIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.57 3.9c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.52c0-.55-.45-1-.99-1z" />
    </svg>
  )
}

function ItemIcon({ type }: { type: VerticalItem['iconType'] }) {
  switch (type) {
    case 'cross':
      return <CrossIcon />
    case 'users':
      return <UsersIcon />
    case 'phone':
      return <PhoneIcon />
  }
}

export default function ProjectsPage() {
  const navigate = useNavigate()

  return (
    <div className={styles.page}>
      <div className={styles.leftBrainWrap} aria-hidden="true">
        <img src={brainSymbol} alt="" className={styles.leftBrainImg} />
      </div>

      <div className={styles.contentContainer}>
        <button
          type="button"
          className={styles.backButton}
          aria-label="Go back"
          onClick={() => navigate(-1)}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
        </button>

        <section className={styles.headerSection}>
          <h1 className={styles.heading}>We Help Our Clients Grow Their Business</h1>
          <p className={styles.subtitle}>
            BrainMint AI Consultancy is dedicated to fusing cutting-edge AI engineering, machine learning architecture,
            and enterprise software solutions. We transform complex data landscapes into autonomous workflows,
            predictive insights, and high-impact business systems
          </p>
        </section>

        <div className={styles.card}>
          <span className={styles.badge}>Check Our Verticals</span>

          <ul className={styles.verticalsList} role="list">
            {VERTICAL_ITEMS.map((item) => (
              <li key={item.id} className={styles.verticalItem}>
                <div className={styles.itemIconWrap}>
                  <ItemIcon type={item.iconType} />
                </div>
                <div className={styles.itemText}>
                  <h2 className={styles.itemTitle}>{item.title}</h2>
                  <p className={styles.itemDesc}>{item.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <button
        type="button"
        className={styles.scrollTopBtn}
        aria-label="Scroll to top of page"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <line x1="12" y1="19" x2="12" y2="5" />
          <polyline points="5 12 12 5 19 12" />
        </svg>
      </button>
    </div>
  )
}
