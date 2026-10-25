import instagramIcon from '../../assets/contact/akar-icons_instagram-fill.png'
import linkedinIcon from '../../assets/contact/akar-icons_linkedin-box-fill.png'
import twitterXIcon from '../../assets/contact/bi_twitter-x.png'
import facebookIcon from '../../assets/contact/Link - Facebook.png'
import mailIcon from '../../assets/contact/ci_mail-open (1).png'
import phoneIcon from '../../assets/contact/bx_phone-call.png'
import addressIcon from '../../assets/contact/Group 2.png'
import styles from './Footer.module.css'

const ADDRESS = '21/18, 1st Cross St, Vengeeswarar Nagar, Vadapalani, Chennai - 600026'

const SOCIAL_LINKS = [
  { label: 'Instagram', href: '#', icon: instagramIcon },
  { label: 'X', href: '#', icon: twitterXIcon },
  { label: 'Facebook', href: '#', icon: facebookIcon },
  { label: 'LinkedIn', href: '#', icon: linkedinIcon },
]

export default function Footer() {
  return (
    <footer className={styles.footer} aria-label="Site footer">
      <div className={`container ${styles.inner}`}>
        <section className={styles.column} aria-labelledby="locations-title">
          <h2 id="locations-title" className={styles.title}>Locations</h2>
          <div className={styles.detail}>
            <img src={addressIcon} alt="" className={styles.detailIcon} />
            <a href="https://maps.app.goo.gl/TkkXJ2Cirnf75bNPA" target="_blank" rel="noreferrer">
              {ADDRESS}
            </a>
          </div>
        </section>

        <section className={styles.column} aria-labelledby="contact-title">
          <h2 id="contact-title" className={styles.title}>Contact</h2>
          <div className={styles.detail}>
            <img src={mailIcon} alt="" className={styles.detailIcon} />
            <a href="mailto:brainmintacademy@gmail.com">brainmintacademy@gmail.com</a>
          </div>
          <div className={styles.detail}>
            <img src={phoneIcon} alt="" className={styles.detailIcon} />
            <a href="tel:+91 97892 50201git switch frontend
git status
git pull --rebase origin frontend">+91 97892 50201</a>
          </div>
        </section>

        <section className={styles.column} aria-labelledby="socials-title">
          <h2 id="socials-title" className={styles.title}>Socials</h2>
          <div className={styles.socials}>
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social.label}
                href={social.href}
                aria-label={`BrainMint on ${social.label}`}
                className={styles.socialLink}
              >
                <img src={social.icon} alt="" />
              </a>
            ))}
          </div>
        </section>
      </div>
    </footer>
  )
}
