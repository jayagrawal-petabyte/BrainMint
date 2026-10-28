import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import brainArt from '../assets/contact/image 12.png';
import './ContactUs.css';

type ContactForm = {
  name: string;
  email: string;
  phone: string;
  requiredService: string;
  subject: string;
  requirements: string;
};

type ApiResponse = {
  success?: boolean;
  message?: string;
  data?: {
    enquiry_id?: number | string;
    email_status?: string;
  };
  error?: {
    code?: string;
    message?: string;
    details?: Array<{
      field?: string;
      message?: string;
    }>;
  };
};

const initialForm: ContactForm = {
  name: '',
  email: '',
  phone: '',
  requiredService: '',
  subject: '',
  requirements: '',
};

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  'https://brainmint-b9xj.onrender.com/api/v1'
).replace(/\/+$/, '');

const DEFAULT_SUCCESS_MESSAGE =
  'Your requirements have been received. Our team will process them and get back to you.';

export default function ContactPage() {
  const [form, setForm] = useState<ContactForm>(initialForm);
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [successMessage, setSuccessMessage] = useState(
    DEFAULT_SUCCESS_MESSAGE
  );

  const updateField = (field: keyof ContactForm, value: string) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (isSubmitting) return;

    setSubmitError('');

    const formElement = event.currentTarget;
    const emailInput = formElement.elements.namedItem(
      'email'
    ) as HTMLInputElement;

    const email = form.email.trim();
    const name = form.name.trim();
    const phone = form.phone.trim();
    const requiredService = form.requiredService.trim();
    const subject = form.subject.trim();
    const requirements = form.requirements.trim();

    const emailPattern =
      /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$/;

    emailInput.setCustomValidity('');

    if (!emailPattern.test(email)) {
      emailInput.setCustomValidity(
        'Please enter a complete email address, e.g. name@example.com.'
      );
      emailInput.reportValidity();
      return;
    }

    if (!formElement.checkValidity()) {
      formElement.reportValidity();
      return;
    }

    if (name.length < 2) {
      setSubmitError('Please enter your name using at least 2 characters.');
      return;
    }

    if (!/^\d{10}$/.test(phone)) {
      setSubmitError('Please enter a valid 10-digit phone number.');
      return;
    }

    const message = [
      `Subject: ${subject}`,
      `Required Service: ${requiredService}`,
      '',
      'Project Requirements:',
      requirements,
    ].join('\n');

    if (message.length < 10 || message.length > 3000) {
      setSubmitError(
        'Please keep the combined subject, service, and project requirements within 3,000 characters.'
      );
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/contact`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name,
    email,
    phone,
    message,
    honeypot: '',
  }),
});

      const result = (await response
        .json()
        .catch(() => null)) as ApiResponse | null;

      if (!response.ok || result?.success !== true) {
        const fieldErrors = result?.error?.details
          ?.map((detail) => {
            const field = detail.field
              ? `${detail.field}: `
              : '';

            return `${field}${detail.message || ''}`.trim();
          })
          .filter(Boolean)
          .join(' ');

        if (response.status === 422) {
          throw new Error(
            fieldErrors ||
              result?.error?.message ||
              result?.message ||
              'The server rejected the submitted information. Please check your entries and try again.'
          );
        }

        if (response.status === 429) {
          throw new Error(
            'Too many submissions. Please wait a minute before trying again.'
          );
        }

        throw new Error(
          fieldErrors ||
            result?.error?.message ||
            result?.message ||
            `We couldn't submit your message (HTTP ${response.status}). Please try again.`
        );
      }

      setSuccessMessage(
        result.message || DEFAULT_SUCCESS_MESSAGE
      );
      setSubmitted(true);
    } catch (error) {
      setSubmitError(
        error instanceof TypeError
          ? 'We could not reach the contact service. Check your internet connection and try again.'
          : error instanceof Error
            ? error.message
            : 'Something went wrong while sending your message. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setForm(initialForm);
    setSubmitted(false);
    setSubmitError('');
    setSuccessMessage(DEFAULT_SUCCESS_MESSAGE);
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <div className="contact-page">
      <Link
        to="/"
        className="contact-back"
        aria-label="Go back home"
      >
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

      <section className="contact-intro">
        <h1>Get In Touch With Us</h1>
        <p>Have an idea or question? Let’s talk.</p>
        <p>
          Reach out to BrainMint and take the first step toward
          turning your ideas into opportunities.
        </p>
      </section>

      <div className="contact-content">
        <div className="contact-art" aria-hidden="true">
          <img src={brainArt} alt="" />
        </div>

        <div className="contact-form-area">
          {!submitted ? (
            <form onSubmit={handleSubmit} noValidate>
              <div className="contact-card">
                <h2>Contact Form</h2>

                <div className="contact-fields">
                  <input
                    aria-label="Name"
                    name="name"
                    type="text"
                    placeholder="Name"
                    value={form.name}
                    onChange={(e) =>
                      updateField('name', e.target.value)
                    }
                    minLength={2}
                    maxLength={150}
                    required
                  />

                  <input
                    aria-label="Email Id"
                    name="email"
                    type="email"
                    placeholder="Email Id"
                    value={form.email}
                    onChange={(e) => {
                      e.target.setCustomValidity('');
                      updateField('email', e.target.value);
                    }}
                    title="Enter a complete email address, e.g. name@example.com"
                    required
                  />

                  <input
                    aria-label="Phone"
                    name="phone"
                    type="tel"
                    placeholder="Phone"
                    value={form.phone}
                    onChange={(e) =>
                      updateField(
                        'phone',
                        e.target.value.replace(/\D/g, '').slice(0, 10)
                      )
                    }
                    inputMode="numeric"
                    pattern="[0-9]{10}"
                    maxLength={10}
                    title="Enter a valid 10-digit phone number"
                    required
                  />

                  <input
                    aria-label="Required Service"
                    name="requiredService"
                    type="text"
                    placeholder="Required Service"
                    value={form.requiredService}
                    onChange={(e) =>
                      updateField('requiredService', e.target.value)
                    }
                    maxLength={150}
                    required
                  />

                  <input
                    className="field-full"
                    aria-label="Subject"
                    name="subject"
                    type="text"
                    placeholder="Subject"
                    value={form.subject}
                    onChange={(e) =>
                      updateField('subject', e.target.value)
                    }
                    maxLength={250}
                    required
                  />

                  <textarea
                    className="field-full requirements-field"
                    aria-label="Project Requirements"
                    name="requirements"
                    placeholder="Project Requirements"
                    value={form.requirements}
                    onChange={(e) =>
                      updateField('requirements', e.target.value)
                    }
                    maxLength={2700}
                    required
                  />
                </div>

                {/* Hidden honeypot spam trap; not a CAPTCHA. */}
                <input
                  className="contact-honeypot"
                  type="text"
                  name="honeypot"
                  tabIndex={-1}
                  autoComplete="off"
                  aria-hidden="true"
                />

                {submitError && (
                  <p className="contact-api-error" role="alert">
                    {submitError}
                  </p>
                )}
              </div>

              <button
                className="contact-submit"
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          ) : (
            <div>
              <div className="contact-card">
                <h2>Contact Form</h2>
                <p className="contact-submitted-text">
                  {successMessage}
                </p>
              </div>

              <div className="thank-you-area" aria-live="polite">
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