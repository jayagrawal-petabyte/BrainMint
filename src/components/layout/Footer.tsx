import { Link } from 'react-router-dom'
import logoImg from '../../assets/brand/brainmint-full-logo.png'
import facebookSvg from '../../assets/icons/facebook.svg'
import twitterSvg from '../../assets/icons/twitter.svg'
import linkedinSvg from '../../assets/icons/linkedin.svg'
import styles from './Footer.module.css'

const NAV_LINKS = [
  { label: 'Home',       to: '/' },
  { label: 'About',      to: '/about' },
  { label: 'Services',   to: '/services' },
  { label: 'Projects',   to: '/projects' },
  { label: 'Contact Us', to: '/contact' },
]

const SERVICE_LINKS = [
  { label: 'Web Development',   to: '/services' },
  { label: 'Mobile Development', to: '/services' },
  { label: 'UI/UX Design',       to: '/services' },
  { label: 'Consulting',         to: '/services' },
]

const SOCIAL_LINKS = [
  { label: 'Facebook', href: '#', icon: facebookSvg },
  { label: 'Twitter',  href: '#', icon: twitterSvg },
  { label: 'LinkedIn', href: '#', icon: linkedinSvg },
]

const CURRENT_YEAR = new Date().getFullYear()

export default function Footer() {
  return (
    <footer className={styles.footer} aria-label="Site footer">
      <div className={`container ${styles.inner}`}>

        <div className={styles.brand}>
          <Link to="/" aria-label="BrainMint home">
            <img src={logoImg} alt="BrainMint — Guiding You to a World of Education" className={styles.logoImg} />
          </Link>
          <p className={styles.description}>
            BrainMint is a software consultancy that combines people, ideas and
            technology to create meaningful solutions for clients while fostering
            continuous learning and growth.
          </p>
          <div className={styles.socials} aria-label="Social media">
            {SOCIAL_LINKS.map((s) => (
              <a
                key={s.label}
                href={s.href}
                aria-label={`BrainMint on ${s.label}`}
                className={styles.socialBtn}
                target="_blank"
                rel="noopener noreferrer"
              >
                <img src={s.icon} alt="" className={styles.socialIcon} />
              </a>
            ))}
          </div>
        </div>

        <nav aria-label="Footer navigation" className={styles.linkGroup}>
          <h3 className={styles.groupTitle}>Navigation</h3>
          <ul role="list">
            {NAV_LINKS.map((link) => (
              <li key={link.to}>
                <Link to={link.to} className={styles.footerLink}>
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <nav aria-label="Footer services" className={styles.linkGroup}>
          <h3 className={styles.groupTitle}>Services</h3>
          <ul role="list">
            {SERVICE_LINKS.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className={styles.footerLink}>
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className={styles.linkGroup}>
          <h3 className={styles.groupTitle}>Contact</h3>
          <address className={styles.contactList}>
            <p className={styles.contactItem}>
              <span className={styles.contactLabel}>Email:</span>
              <a href="mailto:hello@brainmint.in" className={styles.footerLink}>
                hello@brainmint.in
              </a>
            </p>
            <p className={styles.contactItem}>
              <span className={styles.contactLabel}>Location:</span>
              <span className={styles.footerLink}>India</span>
            </p>
          </address>
        </div>
      </div>

      <div className={styles.bottomBar}>
        <div className="container">
          <p className={styles.copyright}>
            &copy; {CURRENT_YEAR} BrainMint Software Consultancy. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
