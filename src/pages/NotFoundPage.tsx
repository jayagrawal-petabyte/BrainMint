import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <section className="section">
      <div className="container text-center">
        <h1 style={{ fontSize: 'var(--text-6xl)', color: 'var(--color-primary)' }}>404</h1>
        <h2>Page Not Found</h2>
        <p className="text-muted" style={{ marginBlock: '1rem' }}>
          The page you are looking for does not exist.
        </p>
        <Link to="/" className="btn btn-primary">
          Back to Home
        </Link>
      </div>
    </section>
  )
}
