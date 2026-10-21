import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import brainArt from '../assets/contact/image 12.png';
import './ContactUs.css';

type ContactForm = {
  name: string;
  email: string;
  phone: string;
  service: string;
  subject: string;
  requirements: string;
};

const initialForm: ContactForm = {
  name: '',
  email: '',
  phone: '',
  service: '',
  subject: '',
  requirements: '',
};

export default function ContactPage() {
  const [form, setForm] = useState<ContactForm>(initialForm);
  const [submitted, setSubmitted] = useState(false);

  const updateField = (field: keyof ContactForm, value: string) => {
    setForm((previous) => ({ ...previous, [field]: value }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
  };

  const handleReset = () => {
    setForm(initialForm);
    setSubmitted(false);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="contact-page">
      {/* Pink Circular Back Button */}
      <Link to="/" className="contact-back" aria-label="Go back home">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m12 19-7-7 7-7" />
          <path d="M19 12H5" />
        </svg>
      </Link>

      {/* Intro Header */}
      <section className="contact-intro">
        <h1>Get In Touch With Us</h1>
        <p>Have an idea or question? Let’s talk.</p>
        <p>
          Reach out to BrainMint and take the first step toward turning
          your ideas into opportunities.
        </p>
      </section>

      <div className="contact-content">
        {/* Left Origami Graphic */}
        <div className="contact-art" aria-hidden="true">
          <img src={brainArt} alt="BrainMint Origami Art" />
        </div>

        {/* Form / Submitted Section */}
        <div className="contact-form-area">
          {!submitted ? (
            <form onSubmit={handleSubmit}>
              <div className="contact-card">
                <h2>Contact Form</h2>

                <div className="contact-fields">
                  <input
                    aria-label="Name"
                    placeholder="Name"
                    value={form.name}
                    onChange={(e) => updateField('name', e.target.value)}
                    required
                  />

                  <input
                    aria-label="Email Id"
                    type="email"
                    placeholder="Email Id"
                    value={form.email}
                    onChange={(e) => updateField('email', e.target.value)}
                    required
                  />

                  <input
                    aria-label="Phone"
                    type="tel"
                    placeholder="Phone"
                    value={form.phone}
                    onChange={(e) => updateField('phone', e.target.value)}
                    required
                  />

                  <select
                    aria-label="Required Service"
                    value={form.service}
                    onChange={(e) => updateField('service', e.target.value)}
                    required
                  >
                    <option value="" disabled>
                      Required Service
                    </option>
                    <option value="Web Development">Web Development</option>
                    <option value="App Development">App Development</option>
                    <option value="UI/UX Design">UI/UX Design</option>
                    <option value="Digital Marketing">Digital Marketing</option>
                    <option value="Other">Other</option>
                  </select>

                  <input
                    className="field-full"
                    aria-label="Subject"
                    placeholder="Subject"
                    value={form.subject}
                    onChange={(e) => updateField('subject', e.target.value)}
                    required
                  />

                  <textarea
                    className="field-full requirements-field"
                    aria-label="Project Requirements"
                    placeholder="Project Requirements"
                    value={form.requirements}
                    onChange={(e) => updateField('requirements', e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Send Message Button (Outside below card) */}
              <button className="contact-submit" type="submit">
                Send Message
              </button>
            </form>
          ) : (
            <div>
              <div className="contact-card">
                <h2>Contact Form</h2>
                <p className="contact-submitted-text">
                  Your Requirements have been sent our team will process and get
                  back to you.
                </p>
              </div>

              {/* Thank You Section (Outside below card) */}
              <div className="thank-you-area">
                <h2 className="thank-you-title">
                  THANK YOU FOR CHOOSING BRAINMINT!
                </h2>
                <button
                  type="button"
                  className="explore-more-btn"
                  onClick={handleReset}
                >
                  Explore more
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Floating Orange Scroll-To-Top Button */}
      <button
        className="contact-scroll-top"
        type="button"
        onClick={scrollToTop}
        aria-label="Scroll to top"
      >
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m18 15-6-6-6 6" />
        </svg>
      </button>
    </div>
  );
}
