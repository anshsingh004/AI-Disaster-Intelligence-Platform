import React, { useState } from "react";
import "./Legal.css";

const SECTIONS = [
  {
    id: "terms",
    icon: "gavel",
    title: "Terms & Conditions",
    content: [
      {
        heading: "1. Scope of Service",
        body: (
          <p className="legal-section-text">
            Terra-Aura Intelligence provides decision-support intelligence tools and disaster monitoring capabilities.
            This platform is designed for trained professionals and authorized personnel only.
          </p>
        )
      },
      {
        heading: "2. Disclaimer of Official Authority",
        body: (
          <p className="legal-section-text">
            This platform provides decision-support intelligence, not official emergency orders. Users should verify
            critical decisions with government, weather, and emergency response authorities before taking action.
          </p>
        )
      },
      {
        heading: "3. Data Accuracy",
        body: (
          <p className="legal-section-text">
            While Terra-Aura employs advanced AI models with high predictive scoring, all predictions and risk assessments
            are probabilistic in nature. No guarantee of absolute accuracy is made.
          </p>
        )
      },
      {
        heading: "4. Authorized Use Only",
        body: (
          <p className="legal-section-text">
            Access to this platform is restricted to personnel with appropriate clearance levels. Unauthorized use,
            sharing of credentials, or data exfiltration is strictly prohibited.
          </p>
        )
      },
      {
        heading: "5. Modifications",
        body: (
          <p className="legal-section-text">
            Terra-Aura reserves the right to update these terms at any time. Continued use of the platform constitutes
            acceptance of updated terms.
          </p>
        )
      }
    ]
  },
  {
    id: "privacy",
    icon: "privacy_tip",
    title: "Privacy Policy",
    content: [
      {
        heading: "Data We Collect",
        body: (
          <p className="legal-section-text">
            We collect account credentials, contact details, incident telemetry, and operational audit logs necessary
            to deliver alerts, threat assessments, and security compliance.
          </p>
        )
      },
      {
        heading: "How We Use Data",
        body: (
          <p className="legal-section-text">
            Collected data is used solely to power the platform, improve inference accuracy, and deliver real-time
            intelligence to authorized responders. Personal information is never sold to third parties.
          </p>
        )
      },
      {
        heading: "Data Retention",
        body: (
          <p className="legal-section-text">
            Incident records are retained for 5 years for audit and crisis research. Operational user logs are retained
            for the duration of active clearance and purged within 90 days of account deactivation.
          </p>
        )
      },
      {
        heading: "Your Rights",
        body: (
          <p className="legal-section-text">
            Authorized users may request export or deletion of their personal telemetry at any time by contacting{" "}
            <a href="mailto:privacy@terra-aura.org" className="legal-link">privacy@terra-aura.org</a>. Requests are processed within 30 days.
          </p>
        )
      }
    ]
  },
  {
    id: "contact",
    icon: "contact_support",
    title: "Contact & Support",
    content: [
      {
        heading: "Emergency Operations Desk",
        body: (
          <p className="legal-section-text">
            Available 24/7 for critical incident escalation and system failures. Phone:{" "}
            <a href="tel:+18005550199" className="legal-link">+1 (800) 555-0199</a>
          </p>
        )
      },
      {
        heading: "General Platform Support",
        body: (
          <p className="legal-section-text">
            For platform issues, telemetry calibration, and deployment questions:{" "}
            <a href="mailto:support@terra-aura.org" className="legal-link">support@terra-aura.org</a>
          </p>
        )
      },
      {
        heading: "Tactical Field Operations",
        body: (
          <p className="legal-section-text">
            For deployment coordination and field team dispatch protocols:{" "}
            <a href="mailto:operations@terra-aura.org" className="legal-link">operations@terra-aura.org</a>
          </p>
        )
      },
      {
        heading: "Privacy & Compliance Office",
        body: (
          <p className="legal-section-text">
            Data export, deletion, or privacy verification requests:{" "}
            <a href="mailto:privacy@terra-aura.org" className="legal-link">privacy@terra-aura.org</a>
          </p>
        )
      },
      {
        heading: "Registered Operations Center",
        body: (
          <p className="legal-section-text">
            Terra-Aura Intelligence Platform, Emergency Response Command Hub, Sector 4, New Delhi — 110001
          </p>
        )
      }
    ]
  }
];

export default function Legal() {
  const [activeSection, setActiveSection] = useState("terms");
  const current = SECTIONS.find(s => s.id === activeSection);

  return (
    <div className="legal-root fade-in">
      <header className="legal-header">
        <div>
          <h1 className="legal-title">Legal & Support</h1>
          <p className="legal-sub">Platform policies, compliance standards, and verified contact channels.</p>
        </div>
        <span className="legal-version-chip">v1.0.0 · Production</span>
      </header>

      <div className="legal-layout">
        <nav className="legal-nav">
          {SECTIONS.map(s => (
            <button
              key={s.id}
              id={`btn-legal-${s.id}`}
              className={`legal-nav-item${activeSection === s.id ? " active" : ""}`}
              onClick={() => setActiveSection(s.id)}
            >
              <span className="material-symbols-outlined">{s.icon}</span>
              {s.title}
            </button>
          ))}
        </nav>

        <div className="legal-content card-lift slide-in" key={activeSection}>
          <div className="legal-content-header">
            <div className="legal-content-icon">
              <span className="material-symbols-outlined">{current.icon}</span>
            </div>
            <h2 className="legal-content-title">{current.title}</h2>
          </div>

          <div className="legal-sections">
            {current.content.map((section, i) => (
              <div key={i} className="legal-section-item">
                <h3 className="legal-section-heading">{section.heading}</h3>
                {section.body}
              </div>
            ))}
          </div>

          <div className="legal-footer">
            <p className="legal-last-updated">Status: Active & Verified</p>
          </div>
        </div>
      </div>
    </div>
  );
}
