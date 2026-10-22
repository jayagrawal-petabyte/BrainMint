import { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import brainSymbol from '../../assets/brand/brainmint-logo.png'
import facebookIcon from '../../assets/contact/Link - Facebook.png'
import twitterIcon from '../../assets/contact/Link - Twitter_margin.png'
import linkedinIcon from '../../assets/contact/LinkedIn_margin.png'
import styles from './Navbar.module.css'

const NAV_LINKS = [
  { label: 'Home',       to: '/',         hasDropdown: false },
  { label: 'About',      to: '/about',    hasDropdown: false },
  { label: 'Service',    to: '/services', hasDropdown: true  },
  { label: 'Project',    to: '/projects', hasDropdown: true  },
  { label: 'Contact Us', to: '/contact',  hasDropdown: false },
]

const SOCIAL_LINKS = [
  { label: 'Facebook', href: '#', icon: facebookIcon },
  { label: 'Twitter',  href: '#', icon: twitterIcon  },
  { label: 'LinkedIn', href: '#', icon: linkedinIcon },
]

function Chevron() {
  return (
    <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true" className={styles.chevron}>
      <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className={styles.navbar} role="banner">
      <nav
        className={`container ${styles.inner}`}
        aria-label="Main navigation"
      >
        <Link to="/" className={styles.logo} aria-label="BrainMint — go to home page">
          <img
            src={brainSymbol}
            alt=""
            className={styles.logoSymbol}
            aria-hidden="true"
          />
          
        </Link>

        <ul className={styles.navLinks} role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.label}>
              {link.to === '#' ? (
                <a href="#" className={styles.navLink}>
                  {link.label}
                  {link.hasDropdown && <Chevron />}
                </a>
              ) : (
                <NavLink
                  to={link.to}
                  className={({ isActive }) =>
                    [styles.navLink, isActive ? styles.active : ''].filter(Boolean).join(' ')
                  }
                  end={link.to === '/'}
                >
                  {link.label}
                  {link.hasDropdown && <Chevron />}
                </NavLink>
              )}
            </li>
          ))}
        </ul>

        <div className={styles.socials} aria-label="Social media links">
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

        <button
          className={styles.hamburger}
          type="button"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={menuOpen}
          aria-controls="mobile-nav"
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span className={[styles.bar, menuOpen ? styles.barTop    : ''].join(' ')} />
          <span className={[styles.bar, menuOpen ? styles.barMiddle : ''].join(' ')} />
          <span className={[styles.bar, menuOpen ? styles.barBottom : ''].join(' ')} />
        </button>
      </nav>

      <div
        id="mobile-nav"
        className={[styles.mobileMenu, menuOpen ? styles.mobileMenuOpen : ''].join(' ')}
        aria-hidden={!menuOpen}
      >
        <ul role="list" className={styles.mobileLinks}>
          {NAV_LINKS.map((link) => (
            <li key={link.label}>
              {link.to === '#' ? (
                <a href="#" className={styles.mobileLink}>
                  {link.label}
                  {link.hasDropdown && <Chevron />}
                </a>
              ) : (
                <NavLink
                  to={link.to}
                  className={({ isActive }) =>
                    [styles.mobileLink, isActive ? styles.mobileLinkActive : ''].filter(Boolean).join(' ')
                  }
                  end={link.to === '/'}
                  onClick={() => setMenuOpen(false)}
                >
                  {link.label}
                  {link.hasDropdown && <Chevron />}
                </NavLink>
              )}
            </li>
          ))}
        </ul>
        <div className={styles.mobileSocials}>
          {SOCIAL_LINKS.map((s) => (
            <a
              key={s.label}
              href={s.href}
              aria-label={`BrainMint on ${s.label}`}
              className={styles.socialBtn}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setMenuOpen(false)}
            >
              <img src={s.icon} alt="" className={styles.socialIcon} />
            </a>
          ))}
        </div>
      </div>
    </header>
  )
}
