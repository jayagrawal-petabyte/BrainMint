import { Link } from 'react-router-dom'
import teamCollaboration from '../assets/brand/team-collaboration.png'
import brainSymbol from '../assets/brand/brainmint-symbol.png'
import styles from './HomePage.module.css'




function IllustrationProvenExperience() {
  return (
    <svg viewBox="0 0 120 100" fill="none" aria-hidden="true" className={styles.cardIllustration}>
      <rect x="30" y="28" width="68" height="52" rx="6" fill="#FF8FAB" transform="rotate(-8 64 54)"/>
      <rect x="22" y="22" width="68" height="52" rx="6" fill="#6C8EF5" transform="rotate(-3 56 48)"/>
      <rect x="18" y="16" width="68" height="52" rx="6" fill="#ffffff" stroke="#e0e0e0" strokeWidth="1"/>
      <rect x="24" y="22" width="28" height="20" rx="3" fill="#E8EDFF"/>
      <rect x="26" y="24" width="10" height="7" rx="1" fill="#9BA8FF"/>
      <rect x="26" y="33" width="20" height="2" rx="1" fill="#C4CAFF"/>
      <rect x="56" y="24" width="22" height="3" rx="1.5" fill="#E0E3FF"/>
      <rect x="56" y="30" width="16" height="3" rx="1.5" fill="#E0E3FF"/>
      <rect x="24" y="46" width="54" height="2.5" rx="1.25" fill="#E0E3FF"/>
      <rect x="24" y="52" width="40" height="2.5" rx="1.25" fill="#E0E3FF"/>
      <rect x="24" y="58" width="48" height="2.5" rx="1.25" fill="#E0E3FF"/>
    </svg>
  )
}

function IllustrationCollaborativeTeam() {
  return (
    <svg viewBox="0 0 120 100" fill="none" aria-hidden="true" className={styles.cardIllustration}>
      <path d="M96 18 L98 22 L102 20 L98 24 L100 28 L96 24 L92 28 L94 24 L90 20 L94 22Z" fill="#FFB74D" opacity="0.8"/>
      <ellipse cx="38" cy="56" rx="14" ry="18" fill="#F48FB1"/>
      <circle cx="38" cy="32" r="12" fill="#F06292"/>
      <circle cx="38" cy="32" r="8" fill="#F8BBD0"/>
      <ellipse cx="60" cy="52" rx="14" ry="22" fill="#7986CB"/>
      <circle cx="60" cy="26" r="12" fill="#5C6BC0"/>
      <circle cx="60" cy="26" r="8" fill="#C5CAE9"/>
      <ellipse cx="82" cy="60" rx="13" ry="16" fill="#FFD54F"/>
      <circle cx="82" cy="36" r="11" fill="#FFC107"/>
      <circle cx="82" cy="36" r="7.5" fill="#FFF9C4"/>
    </svg>
  )
}

function IllustrationClientCentric() {
  return (
    <svg viewBox="0 0 120 100" fill="none" aria-hidden="true" className={styles.cardIllustration}>
      <line x1="28" y1="35" x2="20" y2="27" stroke="#FFC107" strokeWidth="2" strokeLinecap="round"/>
      <line x1="24" y1="48" x2="14" y2="48" stroke="#FFC107" strokeWidth="2" strokeLinecap="round"/>
      <line x1="28" y1="62" x2="20" y2="70" stroke="#FFC107" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="62" cy="48" r="30" fill="#7986CB" opacity="0.15"/>
      <circle cx="62" cy="48" r="30" stroke="#7986CB" strokeWidth="2.5"/>
      <circle cx="62" cy="48" r="20" fill="#7986CB" opacity="0.25"/>
      <circle cx="62" cy="48" r="20" stroke="#7986CB" strokeWidth="2.5"/>
      <circle cx="62" cy="48" r="10" fill="#7986CB" opacity="0.5"/>
      <circle cx="62" cy="48" r="10" stroke="#7986CB" strokeWidth="2.5"/>
      <circle cx="62" cy="48" r="4" fill="#7986CB"/>
      <path d="M74 60 L88 74 L84 76 L88 84 L82 82 L80 88 L76 76 L74 60Z"
            fill="#EF5350" stroke="#C62828" strokeWidth="1"/>
    </svg>
  )
}

function IllustrationInnovationGrowth() {
  return (
    <svg viewBox="0 0 120 100" fill="none" aria-hidden="true" className={styles.cardIllustration}>
      <path d="M96 16 L97.5 20 L101.5 18 L97.5 22 L99 26 L95.5 22 L92 26 L93.5 22 L90 18 L94 20Z"
            fill="#FFD54F" opacity="0.9"/>
      <rect x="28" y="62" width="16" height="20" rx="4" fill="#7986CB"/>
      <rect x="50" y="50" width="16" height="32" rx="4" fill="#7986CB"/>
      <rect x="72" y="38" width="16" height="44" rx="4" fill="#7986CB"/>
      <rect x="22" y="82" width="78" height="2" rx="1" fill="#C5CAE9"/>
      <path d="M84 22 C84 22 90 16 96 10" stroke="#FF7043" strokeWidth="3" strokeLinecap="round"/>
      <path d="M90 8 L96 10 L94 16" stroke="#FF7043" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

const FEATURE_CARDS = [
  {
    number:       '01',
    title:        'Proven Experience',
    description:  'Our past projects showcase our ability to turn ideas into practical and impactful solutions.',
    bg:           '#F0EDFF',
    badgeBg:      '#E8E3FF',
    badgeColor:   '#7C6AF7',
    illustration: <IllustrationProvenExperience />,
  },
  {
    number:       '02',
    title:        'Collaborative Team',
    description:  'Our employees and interns work together, bringing diverse perspectives, skills and ideas to every project.',
    bg:           '#FFF0F3',
    badgeBg:      '#FFE0EA',
    badgeColor:   '#F06292',
    illustration: <IllustrationCollaborativeTeam />,
  },
  {
    number:       '03',
    title:        'Client-Centric Approach',
    description:  "We understand our clients' goals and create tailored solutions that deliver real value.",
    bg:           '#FFFBEB',
    badgeBg:      '#FFF3CC',
    badgeColor:   '#F9A825',
    illustration: <IllustrationClientCentric />,
  },
  {
    number:       '04',
    title:        'Innovation & Growth',
    description:  'We continuously explore new technologies while creating an environment where our team can learn and grow',
    bg:           '#EDF5FF',
    badgeBg:      '#D6EAFF',
    badgeColor:   '#1976D2',
    illustration: <IllustrationInnovationGrowth />,
  },
]

function ReadMoreArrow() {
  return (
    <span className={styles.arrowBtn} aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" className={styles.arrowIcon}>
        <circle cx="12" cy="12" r="11" stroke="#4F6EF7" strokeWidth="1.5"/>
        <path d="M8 12 H16 M13 9 L16 12 L13 15" stroke="#4F6EF7" strokeWidth="1.5"
              strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </span>
  )
}

export default function HomePage() {
  return (
    <div className={styles.page}>
      <div className={styles.leftBrainWrap} aria-hidden="true">
        <img
          src={brainSymbol}
          alt=""
          className={styles.leftBrainImg}
        />
      </div>

      <section className={styles.hero} aria-label="Hero — Why Choose Us">
        <div className={`container ${styles.heroInner}`}>

          <div className={styles.heroContent}>
            <p className={styles.heroEyebrow}>WHY CHOOSE US?</p>
            <h1 className={styles.heroHeadline}>
              More than a company.<br />
              A team that builds, learns and grows together.
            </h1>
            <p className={styles.heroSub}>
              We combine people, ideas and technology to create meaningful solutions
              for our clients while providing a space for continuous learning and growth.
            </p>
          </div>

          <div className={styles.heroImageWrap}>
            <img
              src={teamCollaboration}
              alt="BrainMint team collaborating at a laptop, with People and Growth labels"
              className={styles.heroImage}
              loading="eager"
            />
          </div>
        </div>
      </section>

      <section className={styles.cardsSection} aria-label="Why choose BrainMint">
        <div className={`container ${styles.cardsContainer}`}>
          {FEATURE_CARDS.map((card) => (
            <article
              key={card.number}
              className={styles.card}
              style={{ background: card.bg } as React.CSSProperties}
            >
              <div
                className={styles.cardBadge}
                style={{
                  background: card.badgeBg,
                  color: card.badgeColor,
                } as React.CSSProperties}
              >
                {card.number}
              </div>

              <div className={styles.cardIllustrationWrap}>
                {card.illustration}
              </div>

              <h3 className={styles.cardTitle}>{card.title}</h3>

              <p className={styles.cardDesc}>{card.description}</p>

              <div className={styles.cardFooter}>
                <Link
                  to="/services"
                  className={styles.cardReadMore}
                  aria-label={`Read more about ${card.title}`}
                >
                  Read more
                </Link>
                <ReadMoreArrow />
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
