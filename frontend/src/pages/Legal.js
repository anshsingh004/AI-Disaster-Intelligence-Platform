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
        text: "Terra-Aura Intelligence provides decision-support intelligence tools and disaster monitoring capabilities. This platform is designed for trained professionals and authorized personnel only."
      },
      {
        heading: "2. Disclaimer of Official Authority",
        text: "This platform provides decision-support intelligence, not official emergency orders. Users should verify critical decisions with government, weather, and emergency response authorities before taking action."
      },
      {
        heading: "3. Data Accuracy",
        text: "While Terra-Aura employs advanced AI models with up to 94% accuracy, all predictions and risk assessments are probabilistic in nature. No guarantee of absolute accuracy is made."
      },
      {
        heading: "4. Authorized Use Only",
        text: "Access to this platform is restricted to personnel with appropriate clearance levels. Unauthorized use, sharing of credentials, or data exfiltration is strictly prohibited."
      },
      {
        heading: "5. Modifications",
        text: "Terra-Aura reserves the right to update these terms at any time. Continued use of the platform constitutes acceptance of updated terms."
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
        text: "We collect account information, contact details, disaster report submissions, and operational telemetry necessary to provide alerts, predictions, and platform support."
      },
      {
        heading: "How We Use Data",
        text: "Collected data is used solely to power the platform, improve AI models, and deliver real-time intelligence to authorized users. Personal information is never sold to third parties."
      },
      {
        heading: "Data Retention",
        text: "Incident data is retained for 5 years for audit and research purposes. Personal account data is retained for the duration of active clearance and deleted within 90 days of deactivation."
      },
      {
        heading: "Your Rights",
        text: "Authorized users may request export or deletion of their personal data at any time by contacting privacy@terra-aura.dev. Requests are processed within 30 days."
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
        text: "Available 24/7 for critical incident escalation and system failures. Phone: +91 90000 00000"
      },
      {
        heading: "General Support",
        text: "For platform issues, data corrections, and deployment questions: support@terra-aura.dev"
      },
      {
        heading: "Operations",
        text: "For deployment coordination and field operations: operations@terra-aura.dev"
      },
      {
        heading: "Privacy Requests",
        text: "Data export, deletion, or privacy concern requests: privacy@terra-aura.dev"
      },
      {
        heading: "Registered Office",
        text: "Terra-Aura Intelligence Platform, Sector 4 Operations Hub, New Delhi — 110001, India"
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
          <p className="legal-sub">Platform policies and contact information — Aegis AI compliance framework.</p>
        </div>
        <span className="legal-version-chip">v2.4.1 · Oct 2024</span>
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
                <p className="legal-section-text">{section.text}</p>
              </div>
            ))}
          </div>

          <div className="legal-footer">
            <p className="legal-last-updated">Last updated: October 2024</p>
            <button className="btn-tonal">
              <span className="material-symbols-outlined">download</span>
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
