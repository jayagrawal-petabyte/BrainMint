import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import brainSymbol from '../assets/brand/brainmint-symbol.png'
import websiteImage from '../assets/services/website.png'
import applicationImage from '../assets/services/application.png'
import aiAgentImage from '../assets/services/ai-agent.png'
import offshoreImage from '../assets/services/offshore.png'
import './ServicesPage.css'

// All four descriptions are transcribed from the Figma detail panels.
// `detailTitle` is used only where the panel heading differs from the tile label (Offshore).
const SERVICES = [
  {
    id: 'website-development',
    title: 'Website Development',
    description:
      "We offer comprehensive website development services tailored to meet your business goals and requirements. Our process begins with understanding your company's objectives, target audience, and the services you wish to showcase. We plan the website structure, including essential pages such as Home, About Us, Services, Projects, and Contact Us. Our team focuses on creating visually appealing, user-friendly, and responsive designs that provide a seamless experience across devices. We select suitable technologies, frameworks, databases, and APIs based on your project's needs. We also ensure website security, optimal performance, accessibility, and search engine optimisation (SEO). From UI/UX design and frontend and backend development to testing, domain setup, hosting, and deployment, we provide end-to-end solutions, along with ongoing maintenance and technical support to ensure your website remains reliable and up to date.",
    image: websiteImage,
  },
  {
    id: 'application-development',
    title: 'Application Development',
    description:
      "We offer comprehensive application development services tailored to meet your business goals and user requirements. Our process begins with understanding your company's objectives, target audience, and the purpose of the application. We identify essential features, functionalities, and user workflows to create an efficient and engaging experience. Our team focuses on intuitive UI/UX design, seamless navigation, and responsive interfaces across supported devices. We select suitable technologies, frameworks, databases, APIs, and development platforms based on your project's needs. We also prioritise application security, performance, scalability, and data protection. From planning and prototyping to frontend and backend development, database integration, testing, and deployment, we provide end-to-end solutions for mobile, web, and cross-platform applications, along with ongoing maintenance, updates, and technical support to ensure reliability and a smooth user experience.",
    image: applicationImage,
  },
  {
    id: 'ai-agent-development',
    title: 'AI Agent Development',
    description:
      "We offer comprehensive AI agent development services tailored to automate business processes, enhance productivity, and improve user experiences. Our process begins with understanding your company's objectives, operational challenges, and specific automation requirements. We identify suitable AI capabilities, workflows, and functionalities to develop intelligent agents that can understand queries, analyse information, make decisions, and perform tasks with minimal human intervention. Our team focuses on designing efficient, user-friendly interfaces and integrating AI agents seamlessly into existing systems. We select appropriate AI models, frameworks, APIs, databases, and automation tools based on your project's needs. We also prioritise data security, accuracy, scalability, and responsible AI implementation. From planning and model integration to agent development, testing, deployment, and optimisation, we provide end-to-end solutions, along with ongoing maintenance, monitoring, and technical support.",
    image: aiAgentImage,
  },
  {
    id: 'offshore-development',
    title: 'Offshore Development Team',
    detailTitle: 'Offshore Development',
    description:
      "We offer dedicated offshore development team services to help businesses expand their technical capabilities, optimise development costs, and accelerate project delivery. Our process begins with understanding your business objectives, project requirements, timelines, and desired skill sets. We provide skilled professionals across frontend and backend development, application development, UI/UX design, AI integration, software testing, and project management. Our teams collaborate closely with your in-house staff to ensure smooth communication, efficient coordination, and consistent progress throughout the development lifecycle. We adapt to your preferred workflows, tools, and technologies while maintaining high standards of code quality, security, and productivity. From team selection and onboarding to development, testing, deployment, and ongoing support, we provide flexible offshore development solutions tailored to your business needs, helping you scale operations and achieve long-term growth.",
    image: offshoreImage,
  },
]

// Minimal typing for the View Transitions API (not present in every TypeScript lib.dom version).
type ViewTransitionDocument = Document & {
  startViewTransition?: (update: () => void | Promise<void>) => { finished: Promise<void> }
}

export default function ServicesPage() {
  const navigate = useNavigate()
  // The selected service lives in the URL (?service=<id>) so the browser Back button and the
  // page's back arrow return from the detail view to the tiles, and links can deep-link to one.
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedService = SERVICES.find((s) => s.id === searchParams.get('service')) ?? null
  const openedFromTiles = useRef(false)
  const detailTitleRef = useRef<HTMLHeadingElement>(null)
  // 'morph' = the clicked tile is being animated into the detail panel (View Transitions API);
  // 'fade'  = fallback entrance (deep link, browser Back from /contact, unsupported browser).
  const [enterMode, setEnterMode] = useState<'fade' | 'morph'>('fade')
  const resolveRendered = useRef<(() => void) | null>(null)

  const prefersReducedMotion = () =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const selectService = (id: string, tile: HTMLButtonElement) => {
    openedFromTiles.current = true
    const doc = document as ViewTransitionDocument

    // Fallback (no View Transitions API, or reduced motion): swap the view and scroll to top.
    if (typeof doc.startViewTransition !== 'function' || prefersReducedMotion()) {
      setEnterMode('fade')
      setSearchParams({ service: id })
      window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'auto' : 'smooth' })
      return
    }

    // Shared-element transition (as in the reference video): the clicked tile and its illustration
    // are given the same view-transition names as the detail panel and its illustration, so the
    // browser animates tile -> panel and small illustration -> large illustration. The other
    // tiles, the intro text and the rest of the page cross-fade out via the root snapshot.
    const art = tile.querySelector<HTMLElement>('.services-page__tile-illustration')
    tile.style.setProperty('view-transition-name', 'services-card')
    art?.style.setProperty('view-transition-name', 'services-art')

    const transition = doc.startViewTransition(
      () =>
        new Promise<void>((resolve) => {
          resolveRendered.current = resolve
          window.setTimeout(resolve, 1000) // safety net so the transition can never hang
          setEnterMode('morph')
          setSearchParams({ service: id })
        }),
    )
    const cleanup = () => {
      tile.style.removeProperty('view-transition-name')
      art?.style.removeProperty('view-transition-name')
    }
    transition.finished.then(cleanup, cleanup)
  }

  const handleBack = () => {
    if (!selectedService) {
      navigate(-1)
    } else if (openedFromTiles.current) {
      openedFromTiles.current = false
      navigate(-1)
    } else {
      setSearchParams({}, { replace: true })
    }
  }

  // Once the detail view is committed: jump to the top (the video shows the detail view starting
  // at the top of the page) and tell the pending view transition that the new DOM is ready.
  useLayoutEffect(() => {
    if (selectedService && resolveRendered.current) {
      window.scrollTo({ top: 0, behavior: 'auto' })
      resolveRendered.current()
      resolveRendered.current = null
    }
  }, [selectedService])

  // Returning to the tiles resets the entrance mode (the next arrival decides again).
  useEffect(() => {
    if (!selectedService) setEnterMode('fade')
  }, [selectedService])

  // Move keyboard/screen-reader focus to the new detail title when the view changes.
  useEffect(() => {
    if (selectedService) detailTitleRef.current?.focus({ preventScroll: true })
  }, [selectedService])

  return (
    <div className="services-page">
      <div className="services-page__brain-wrap" aria-hidden="true">
        <img src={brainSymbol} alt="" className="services-page__brain-img" />
      </div>

      <div className="container services-page__content">
        <button
          type="button"
          className="services-page__back"
          aria-label={selectedService ? 'Back to all services' : 'Go back'}
          onClick={handleBack}
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

        {selectedService ? (
          /* Detail view (Figma): intro hidden, heading left-aligned, panel below, CTA under the card.
             Keyed by service id so every selection replays the entrance animation. */
          <section key={selectedService.id} className={`services-page__detail-view${
              enterMode === 'morph' ? ' services-page__detail-view--morph' : ''
            }`}
          >
            <header className="services-page__detail-header">
              <p className="services-page__eyebrow">Our Services</p>
              <h1 className="services-page__heading">What We Can Do For You</h1>
            </header>

            <article
              id="service-detail"
              className="services-page__detail"
              aria-labelledby="service-detail-title"
            >
              <div className="services-page__detail-illustration">
                <img src={selectedService.image} alt="" />
              </div>
              <h2
                id="service-detail-title"
                ref={detailTitleRef}
                tabIndex={-1}
                className="services-page__detail-title"
              >
                {selectedService.detailTitle ?? selectedService.title}
              </h2>
              <p className="services-page__detail-description">{selectedService.description}</p>
            </article>

            <div className="services-page__detail-footer">
              <Link to="/contact" className="services-page__request-button">
                Request a Service
              </Link>
            </div>
          </section>
        ) : (
          <>
            <p className="services-page__intro">
              BrainMint is a dynamic and rapidly growing organization focused on empowering
              individuals and transforming futures through technology, education, and innovative
              solutions. The company brings together learning, technology, and professional
              development to create opportunities for students, professionals, and organizations.
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
                      onClick={(e) => selectService(service.id, e.currentTarget)}
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
          </>
        )}
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