import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import brainSymbol from '../assets/brand/brainmint-symbol.png'
import websiteImage from '../assets/services/website.png'
import applicationImage from '../assets/services/application.png'
import aiAgentImage from '../assets/services/ai-agent.png'
import offshoreImage from '../assets/services/offshore.png'
import './ServicesPage.css'

const SERVICES = [
  {
    id: 'website-development',
    title: 'Website Development',
    description:
      'We design and build fast, responsive websites that present your business clearly and work well on every device. From planning and design through to launch, we focus on clean code, accessibility and a smooth experience for your visitors.',
    image: websiteImage,
  },
  {
    id: 'application-development',
    title: 'Application Development',
    description:
      'We build web and mobile applications around your users and your workflows. Our team handles the full cycle, from requirements and interface design to development, testing and release, so your product is reliable and ready to grow.',
    image: applicationImage,
  },
  {
    id: 'ai-agent-development',
    title: 'AI Agent Development',
    description:
      'We create AI agents that take on repetitive tasks, answer questions and support decisions inside the tools you already use. Each agent is scoped to your goals and tested carefully, so it is useful, predictable and easy for your team to oversee.',
    image: aiAgentImage,
  },
  {
    id: 'offshore-development',
    title: 'Offshore Development Team',
    description:
      'Extend your team with a dedicated BrainMint developer team who work to your processes and schedule. With clear communication and regular progress updates, you can scale delivery without the overhead of hiring.',
    image: offshoreImage,
  },
]

export default function ServicesPage() {
  const [selectedService, setSelectedService] = useState(SERVICES[0])
  const navigate = useNavigate()

  return (
    <div className="services-page">
      <div className="services-page__brain-wrap" aria-hidden="true">
        <img src={brainSymbol} alt="" className="services-page__brain-img" />
      </div>

      <div className="container services-page__content">
        <button
          type="button"
          className="services-page__back"
          aria-label="Go back"
          onClick={() => navigate(-1)}
        >
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className="services-page__back-icon">
            <path
              d="M19 12H5M11 6L5 12L11 18"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <p className="services-page__intro">
          BrainMint is a dynamic and rapidly growing organization focused on empowering individuals
          and transforming futures through technology, education, and innovative solutions. The
          company brings together learning, technology, and professional development to create
          opportunities for students, professionals, and organizations.
        </p>

        <div className="services-page__showcase">
          <header className="services-page__title">
            <p className="services-page__eyebrow">Our Services</p>
            <h1 className="services-page__heading">What We Can Do For You</h1>
          </header>

          <ul className="services-page__tiles">
            {SERVICES.map((service) => (
              <li key={service.id}>
                <button
                  type="button"
                  className="services-page__tile"
                  aria-pressed={service.id === selectedService.id}
                  aria-controls="service-detail"
                  onClick={() => setSelectedService(service)}
                >
                  <span className="services-page__tile-illustration">
                    <img src={service.image} alt="" />
                  </span>
                  <span className="services-page__tile-title">{service.title}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <article
          id="service-detail"
          className="services-page__detail"
          aria-labelledby="service-detail-title"
          aria-live="polite"
        >
          <div className="services-page__detail-illustration">
            <img src={selectedService.image} alt="" />
          </div>
          <h2 id="service-detail-title" className="services-page__detail-title">{selectedService.title}</h2>
          <p className="services-page__detail-description">{selectedService.description}</p>
          <div className="services-page__detail-footer">
            <Link to="/contact" className="services-page__request-button">
              Request a Service
            </Link>
          </div>
        </article>
      </div>

      <button
        type="button"
        className="services-page__scroll-top"
        aria-label="Scroll to top of page"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className="services-page__scroll-top-icon">
          <path
            d="M6 14L12 8L18 14"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  )
}