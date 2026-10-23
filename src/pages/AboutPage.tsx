import { Link } from 'react-router-dom'
import brainDecoration from '../assets/contact/image 12.png'
import missionVisionArt from '../assets/about/Screenshot 2026-10-08 141633 1.png'
import missionIcon from '../assets/about/Screenshot_2026-10-08_142502-removebg-preview 1.png'
import visionIcon from '../assets/about/Screenshot_2026-10-08_142607-removebg-preview 1.png'
import styles from './AboutPage.module.css'

const REASONS = [
  {
    title: 'Production-Ready AI Architecture',
    description: 'Reliable AI solutions designed for real-world business needs.',
  },
  {
    title: 'Scalable Engineering',
    description: 'High-performance software built to adapt and grow with your business.',
  },
  {
    title: 'Dedicated Strategic Advisory',
    description: 'Expert guidance that aligns technology with business goals.',
  },
  {
    title: 'Security & Compliance Standards',
    description: 'Security-focused development that helps protect business data.',
  },
]

export default function AboutPage() {
  return (
    <div className={styles.page}>
      <img
        src={brainDecoration}
        alt=""
        aria-hidden="true"
        className={styles.slidingLogo}
      />

      <main className={styles.main}>
        <Link to="/" className={styles.backButton} aria-label="Back to home">
          <span aria-hidden="true">←</span>
        </Link>

        <section className={styles.missionSection} aria-labelledby="mission-title">
          <div className={styles.missionIntro}>
            <p className={styles.eyebrow}>OUR MISSION &amp; VISION</p>
            <h2 id="mission-title">Driven by purpose! Focused on the future!</h2>
            <p>
              We are committed to creating meaningful solutions, empowering people through
              technology, and building a better tomorrow together.
            </p>
          </div>

          <div className={styles.missionGrid}>
            <img
              src={missionVisionArt}
              alt="BrainMint team collaborating around a table"
              className={styles.missionArt}
            />
            <div className={styles.statementList}>
              <article className={`${styles.statementCard} ${styles.missionCard}`}>
                <img src={missionIcon} alt="" />
                <div>
                  <h3>OUR MISSION</h3>
                  <p>
                    To dedicate advanced research, business process engineering, and
                    cutting-edge software innovation to working together with clients to
                    transform their enterprise operations and build stronger, future-ready
                    businesses.
                  </p>
                </div>
              </article>
              <article className={`${styles.statementCard} ${styles.visionCard}`}>
                <img src={visionIcon} alt="" />
                <div>
                  <h3>OUR VISION</h3>
                  <p>Transforming the world through excellence in research and cutting-edge technologies.</p>
                </div>
              </article>
            </div>
          </div>
        </section>

        <section className={styles.whySection} aria-labelledby="why-title">
          <div className={styles.whyIntro}>
            <h1 id="why-title">Why Businesses Choose BrainMint</h1>
            <p>
              We combine AI innovation, scalable engineering, strategic expertise, and
              security-focused development to deliver reliable digital solutions that help
              businesses grow.
            </p>
          </div>

          <div className={styles.reasonGrid}>
            {REASONS.map((reason) => (
              <article className={styles.reasonCard} key={reason.title}>
                <span className={styles.checkmark} aria-hidden="true">✓</span>
                <h2>{reason.title}</h2>
                <p>{reason.description}</p>
              </article>
            ))}
          </div>

          <Link to="/contact" className={styles.exploreButton}>
            Explore More
          </Link>
        </section>
      </main>

      <button
        type="button"
        className={styles.scrollTop}
        aria-label="Scroll to top"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        ↑
      </button>
    </div>
  )
}
