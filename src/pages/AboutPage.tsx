import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import brainSymbol from '../assets/contact/image 12.png'
import styles from './AboutPage.module.css'

type ContactForm = {
  name: string
  email: string
  phone: string
  service: string
  subject: string
  requirements: string
}

const INITIAL_FORM: ContactForm = {
  name: '',
  email: '',
  phone: '',
  service: '',
  subject: '',
  requirements: '',
}

export default function AboutPage() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [submitted, setSubmitted] = useState(false)

  function updateField(field: keyof ContactForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitted(true)
  }

  return (
    <div className={styles.page}>
      <div className={styles.brainDecoration} aria-hidden="true">
        <img src={brainSymbol} alt="" />
      </div>

      <main className={styles.main}>
        <Link to="/" className={styles.backButton} aria-label="Back to home">
          <span aria-hidden="true">←</span>
        </Link>

        <section className={styles.intro} aria-labelledby="about-title">
          <h1 id="about-title">Get In Touch With Us</h1>
          <p>Have an idea or question? Let&apos;s talk.</p>
          <p>Reach out to BrainMint and take the first step toward turning your ideas into opportunities.</p>
        </section>

        <section className={styles.formSection} aria-labelledby="contact-form-title">
          <h2 id="contact-form-title">Contact Form</h2>
          {submitted ? (
            <p className={styles.confirmation}>
              Your Requirements have been sent our team will process and get back to you.
            </p>
          ) : (
            <form className={styles.form} onSubmit={handleSubmit}>
              <div className={styles.formGrid}>
                <input
                  aria-label="Name"
                  name="name"
                  placeholder="Name"
                  required
                  value={form.name}
                  onChange={(event) => updateField('name', event.target.value)}
                />
                <input
                  aria-label="Email Id"
                  type="email"
                  name="email"
                  placeholder="Email Id"
                  required
                  value={form.email}
                  onChange={(event) => updateField('email', event.target.value)}
                />
                <input
                  aria-label="Phone"
                  name="phone"
                  placeholder="Phone"
                  value={form.phone}
                  onChange={(event) => updateField('phone', event.target.value)}
                />
                <input
                  aria-label="Required Service"
                  name="service"
                  placeholder="Required Service"
                  required
                  value={form.service}
                  onChange={(event) => updateField('service', event.target.value)}
                />
              </div>
              <input
                aria-label="Subject"
                name="subject"
                placeholder="Subject"
                required
                value={form.subject}
                onChange={(event) => updateField('subject', event.target.value)}
              />
              <textarea
                aria-label="Project Requirements"
                name="requirements"
                placeholder="Project Requirements"
                required
                rows={4}
                value={form.requirements}
                onChange={(event) => updateField('requirements', event.target.value)}
              />
              <button type="submit" className={styles.submitButton}>Send Message</button>
            </form>
          )}
        </section>

        {submitted && (
          <section className={styles.thanks} aria-live="polite">
            <h2>THANK YOU FOR CHOOSING BRAINMINT!</h2>
            <button type="button" className={styles.exploreButton} onClick={() => setSubmitted(false)}>
              Explore more
            </button>
          </section>
        )}
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
