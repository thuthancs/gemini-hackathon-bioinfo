/** Component for displaying multi-dimensional validation results. */
import { useState } from 'react';
import type { FinalValidationResult } from '../types';
import './ValidationDetails.css';

interface ValidationDetailsProps {
  validation: FinalValidationResult;
}

export default function ValidationDetails({ validation }: ValidationDetailsProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getVerdictColor = (verdict: string) => {
    const v = verdict.toLowerCase();
    if (v.includes('positive') || v.includes('maintained') || v === 'no_risk') return 'good';
    if (v.includes('neutral') || v.includes('partial') || v === 'low') return 'medium';
    return 'poor';
  };

  const getRiskColor = (score?: number) => {
    if (!score) return 'medium';
    if (score <= 3) return 'low';
    if (score <= 6) return 'medium';
    return 'high';
  };

  // Check if we have any validation data to display
  const hasValidationData = 
    validation.overall_verdict ||
    validation.structural_restoration ||
    validation.aggregation_risk ||
    validation.functional_preservation ||
    validation.amyloid_risk ||
    (validation.recommendations && validation.recommendations.length > 0) ||
    (validation.warnings && validation.warnings.length > 0);

  if (!hasValidationData) {
    return (
      <div className="validation-details">
        <h3>Multi-Dimensional Validation Analysis</h3>
        <div className="no-validation-data">
          <p>
            Multi-dimensional validation analysis was not performed because no candidates 
            passed the ESM-1v evolutionary validation step.
          </p>
          <p className="validation-hint">
            This analysis requires candidates that have been validated by ESM-1v before 
            proceeding to structural and functional assessment.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="validation-details">
      <h3>Multi-Dimensional Validation Analysis</h3>

      {validation.overall_verdict && (
        <div className="overall-verdict-section">
          <div className="verdict-display">
            <span className="verdict-label">Overall Verdict:</span>
            <span className={`verdict-badge verdict-${validation.overall_verdict.toLowerCase().replace('_', '-')}`}>
              {validation.overall_verdict.replace('_', ' ')}
            </span>
          </div>
          {validation.risk_score !== undefined && (
            <div className="risk-display">
              <span className="risk-label">Risk Score:</span>
              <span className={`risk-badge risk-${getRiskColor(validation.risk_score)}`}>
                {validation.risk_score.toFixed(1)}/10
              </span>
            </div>
          )}
        </div>
      )}

      <div className="dimensions-grid">
        {validation.structural_restoration && (
          <div className="dimension-card">
            <div
              className="dimension-header"
              onClick={() => toggleSection('structural')}
            >
              <h4>Structural Restoration</h4>
              <span className="toggle-icon">
                {expandedSections.has('structural') ? '▼' : '▶'}
              </span>
            </div>
            <div className={`dimension-content ${expandedSections.has('structural') ? 'expanded' : ''}`}>
              <div className="dimension-verdict">
                <span className={`verdict-badge-small verdict-${getVerdictColor(validation.structural_restoration.verdict)}`}>
                  {validation.structural_restoration.verdict}
                </span>
                <span className="confidence-score">
                  Confidence: {(validation.structural_restoration.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="dimension-reasoning">{validation.structural_restoration.reasoning}</p>
            </div>
          </div>
        )}

        {validation.aggregation_risk && (
          <div className="dimension-card">
            <div
              className="dimension-header"
              onClick={() => toggleSection('aggregation')}
            >
              <h4>Aggregation Risk</h4>
              <span className="toggle-icon">
                {expandedSections.has('aggregation') ? '▼' : '▶'}
              </span>
            </div>
            <div className={`dimension-content ${expandedSections.has('aggregation') ? 'expanded' : ''}`}>
              <div className="dimension-verdict">
                <span className={`verdict-badge-small verdict-${getVerdictColor(validation.aggregation_risk.verdict)}`}>
                  {validation.aggregation_risk.verdict.replace('_', ' ')}
                </span>
                <span className="confidence-score">
                  Confidence: {(validation.aggregation_risk.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="dimension-reasoning">{validation.aggregation_risk.reasoning}</p>
            </div>
          </div>
        )}

        {validation.functional_preservation && (
          <div className="dimension-card">
            <div
              className="dimension-header"
              onClick={() => toggleSection('functional')}
            >
              <h4>Functional Preservation</h4>
              <span className="toggle-icon">
                {expandedSections.has('functional') ? '▼' : '▶'}
              </span>
            </div>
            <div className={`dimension-content ${expandedSections.has('functional') ? 'expanded' : ''}`}>
              <div className="dimension-verdict">
                <span className={`verdict-badge-small verdict-${getVerdictColor(validation.functional_preservation.verdict)}`}>
                  {validation.functional_preservation.verdict}
                </span>
                <span className="confidence-score">
                  Confidence: {(validation.functional_preservation.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="dimension-reasoning">{validation.functional_preservation.reasoning}</p>
            </div>
          </div>
        )}

        {validation.amyloid_risk && (
          <div className="dimension-card">
            <div
              className="dimension-header"
              onClick={() => toggleSection('amyloid')}
            >
              <h4>Amyloid Risk</h4>
              <span className="toggle-icon">
                {expandedSections.has('amyloid') ? '▼' : '▶'}
              </span>
            </div>
            <div className={`dimension-content ${expandedSections.has('amyloid') ? 'expanded' : ''}`}>
              <div className="dimension-verdict">
                <span className={`verdict-badge-small verdict-${getVerdictColor(validation.amyloid_risk.verdict)}`}>
                  {validation.amyloid_risk.verdict.replace('_', ' ')}
                </span>
                <span className="confidence-score">
                  Confidence: {(validation.amyloid_risk.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="dimension-reasoning">{validation.amyloid_risk.reasoning}</p>
            </div>
          </div>
        )}
      </div>

      {validation.recommendations && validation.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h4>Recommendations</h4>
          <ul>
            {validation.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {validation.warnings && validation.warnings.length > 0 && (
        <div className="warnings-section">
          <h4>Warnings</h4>
          <ul>
            {validation.warnings.map((warning, idx) => (
              <li key={idx}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

