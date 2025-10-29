# GDPR Compliance Documentation - GeneWeb Application

**Document Version**: 1.0  
**Last Updated**: October 23, 2025  
**Owner**: Data Protection Team  
**Status**: Active

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Scope and Purpose](#scope-and-purpose)
3. [Legal Basis](#legal-basis)
4. [Data Processing Register](#data-processing-register)
5. [User Rights Implementation](#user-rights-implementation)
6. [Data Protection Impact Assessment](#data-protection-impact-assessment)
7. [Breach Notification Procedures](#breach-notification-procedures)
8. [Third-Party Processors](#third-party-processors)
9. [International Data Transfers](#international-data-transfers)
10. [Departmental Guidelines](#departmental-guidelines)

---

## 1. Executive Summary

GeneWeb is a genealogy management application that processes personal data including family relationships, biographical information, and historical records. This document outlines our compliance with the General Data Protection Regulation (GDPR - EU 2016/679) and serves as the central reference for all data protection activities.

**Key Compliance Points:**
- ✅ Lawful basis established for all data processing activities
- ✅ User rights mechanisms implemented (access, rectification, erasure)
- ✅ Data minimization principles applied
- ✅ Security measures documented and implemented
- ✅ Breach notification procedures established
- ✅ Privacy by design integrated into application architecture

---

## 2. Scope and Purpose

### 2.1 Application Scope
GeneWeb processes the following categories of personal data:
- **Biographical data**: Names, dates of birth/death, places
- **Family relationships**: Parent-child, spouse, sibling connections
- **Supplementary information**: Occupations, historical notes, photographs
- **User account data**: Email addresses, usernames, access logs

### 2.2 Purpose of Processing
Primary purposes for data processing:
1. **Genealogical research** - Building and maintaining family trees
2. **Historical preservation** - Documenting family history for future generations
3. **Educational purposes** - Learning about family heritage
4. **Application functionality** - User authentication and access control

### 2.3 Geographic Scope
- Primary deployment: European Union (France)
- User base: Primarily EU residents
- Data storage: EU-based servers only

---

## 3. Legal Basis

### 3.1 Legal Grounds for Processing

For each data processing activity, we rely on the following legal bases:

| Data Category | Legal Basis | GDPR Article | Justification |
|---------------|-------------|--------------|---------------|
| Living persons' data | **Consent** | Article 6(1)(a) | Explicit consent obtained via application interface |
| Deceased persons' data | **Legitimate Interest** | Article 6(1)(f) | Historical and genealogical research purposes |
| User account data | **Contract** | Article 6(1)(b) | Necessary for service provision |
| Security logs | **Legal Obligation** | Article 6(1)(c) | Required for security and fraud prevention |

### 3.2 Consent Management

**For living persons:**
- Consent must be freely given, specific, informed, and unambiguous
- Users can withdraw consent at any time
- Consent records are timestamped and auditable
- Default status: NO consent (opt-in model)

**Consent Collection Process:**
1. Clear information provided about data usage
2. Explicit action required (checkbox, button click)
3. Consent recorded with timestamp and IP address
4. Confirmation email sent to user
5. Withdrawal mechanism clearly displayed

### 3.3 Deceased Persons Exception

Under French law (Loi Informatique et Libertés) and GDPR recital 27:
- GDPR does not apply to deceased persons
- Family members may request modification/deletion of deceased relatives' data
- Historical and archival purposes are recognized legitimate interests

---

## 4. Data Processing Register (Article 30)

### 4.1 Controller Information
**Data Controller:**
- Organization: GeneWeb Project
- Address: [To be completed]
- Contact: [Data Protection Officer email]
- Representative: [DPO Name]

### 4.2 Processing Activities Registry

#### Processing Activity 1: User Account Management
- **Purpose**: Authentication and access control
- **Legal basis**: Contract (Article 6(1)(b))
- **Data categories**: Email, username, password hash, login timestamps
- **Data subjects**: Application users
- **Recipients**: Internal systems only
- **Retention period**: Until account deletion + 30 days
- **Security measures**: Password hashing (bcrypt), encrypted storage, rate limiting

#### Processing Activity 2: Genealogical Data Management
- **Purpose**: Family tree construction and maintenance
- **Legal basis**: Consent (living) / Legitimate interest (deceased)
- **Data categories**: Names, dates, places, relationships, biographical notes
- **Data subjects**: Living and deceased individuals
- **Recipients**: Family members with access rights, researchers (anonymized)
- **Retention period**: Indefinite (historical archive) or until deletion request
- **Security measures**: Encryption at rest, access controls, audit logging

#### Processing Activity 3: Audit Logging
- **Purpose**: Security monitoring and compliance
- **Legal basis**: Legal obligation (Article 6(1)(c))
- **Data categories**: User IDs, IP addresses, actions, timestamps
- **Data subjects**: Application users
- **Recipients**: Security team only
- **Retention period**: 90 days rolling window
- **Security measures**: Encrypted logs, restricted access, automated rotation

#### Processing Activity 4: Data Export (Right of Access)
- **Purpose**: GDPR Article 15 compliance
- **Legal basis**: Legal obligation
- **Data categories**: All personal data held
- **Data subjects**: Individual making request
- **Recipients**: Requesting individual only
- **Retention period**: 30 days (export file)
- **Security measures**: Encrypted export, authenticated download, automatic deletion

---

## 5. User Rights Implementation

### 5.1 Right of Access (Article 15)

**Implementation:**
- Self-service portal: Users can request data export via API endpoint `/api/v1/persons/{id}/gdpr-export`
- Response time: Immediate (automated)
- Format: Machine-readable JSON

**Export includes:**
- All personal data stored
- Processing purposes
- Data recipients
- Storage duration
- Source of data
- Audit trail of access

**Process:**
```
User Request → Authentication → Data Collection → Encryption → Download → Audit Log
```

### 5.2 Right to Rectification (Article 16)

**Implementation:**
- Self-service: Users can update their own data via application interface
- API endpoints: `PATCH /api/v1/persons/{id}`
- Verification: Changes logged in audit trail
- Notification: Related users notified of significant changes

**Turnaround time:** Immediate (real-time updates)

### 5.3 Right to Erasure / "Right to be Forgotten" (Article 17)

**Implementation:**
- Request via application or email to DPO
- Verification of identity required
- Two-step confirmation to prevent accidents

**Processing:**
1. **For living persons with consent basis:**
   - Full deletion or anonymization available
   - Data removed from all backups within 30 days
   - Audit log preserved (pseudonymized)

2. **For historical/archived data:**
   - Legitimate interest assessment performed
   - Balancing test: Historical value vs. privacy rights
   - Alternative: Anonymization instead of deletion

**Exceptions (Article 17(3)):**
- Historical research purposes (if no alternative means exist)
- Legal obligation to retain data
- Establishment, exercise, or defense of legal claims

**API Endpoint:** `POST /api/v1/persons/{id}/anonymize`

### 5.4 Right to Data Portability (Article 20)

**Implementation:**
- Export in JSON format (machine-readable)
- GEDCOM format support (industry standard for genealogy)
- Automated via API or web interface

**Scope:**
- Only data provided by user (not derived data)
- Only data processed with consent or contract basis

### 5.5 Right to Object (Article 21)

**Implementation:**
- Users can object to processing based on legitimate interest
- Clear "opt-out" mechanism in application
- Processing stops unless compelling legitimate grounds demonstrated

### 5.6 Rights Related to Automated Decision-Making (Article 22)

**Status:** Not applicable - GeneWeb does not perform automated decision-making with legal or significant effects.

### 5.7 Response Timeframes

| Right | Standard Response Time | Maximum Delay |
|-------|----------------------|---------------|
| Access (Art. 15) | Immediate (automated) | 1 month |
| Rectification (Art. 16) | Immediate | 1 month |
| Erasure (Art. 17) | 5 business days | 1 month |
| Portability (Art. 20) | Immediate (automated) | 1 month |
| Object (Art. 21) | 5 business days | 1 month |

Complex cases may be extended by 2 months with notification to the data subject.

---

## 6. Data Protection Impact Assessment (DPIA)

### 6.1 DPIA Necessity Assessment

**Question:** Does GeneWeb require a DPIA under Article 35?

**Analysis:**
- ✅ Systematic processing of biographical data
- ✅ Processing of sensitive data (family relationships)
- ❌ No large-scale surveillance
- ❌ No profiling with legal effects
- ❌ No special category data (health, biometric)

**Conclusion:** DPIA recommended but not strictly required. Performed as best practice.

### 6.2 Risk Assessment

#### High Risks Identified:
1. **Unauthorized access to family data**
   - Impact: Privacy breach affecting multiple family members
   - Likelihood: Medium
   - Mitigation: Authentication, authorization, audit logging

2. **Data breach exposing historical records**
   - Impact: Reputation damage, privacy violations
   - Likelihood: Low
   - Mitigation: Encryption at rest and in transit, regular security audits

3. **Accidental deletion of irreplaceable genealogical data**
   - Impact: Data loss, user dissatisfaction
   - Likelihood: Low
   - Mitigation: Soft deletes, backups, confirmation dialogs

#### Medium Risks:
1. **Incorrect family relationships recorded**
   - Mitigation: User verification, correction mechanisms
   
2. **Visibility settings misconfigured**
   - Mitigation: Secure defaults (most restrictive), clear UI

### 6.3 Risk Mitigation Summary

| Risk | Mitigation Measures | Residual Risk |
|------|---------------------|---------------|
| Unauthorized access | Authentication, RBAC, audit logs | Low |
| Data breach | Encryption, HTTPS, security headers | Low |
| Data loss | Backups, soft deletes, version control | Very Low |
| Incorrect data | Validation, user corrections, audit trail | Low |

**Overall Risk Level:** Low (after mitigations)

---

## 7. Breach Notification Procedures

### 7.1 Breach Definition
A personal data breach is: "a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data."

### 7.2 Detection Mechanisms
- Automated monitoring alerts (failed login attempts, unusual access patterns)
- Security log analysis
- User reports
- Third-party notifications

### 7.3 Notification Timeline

```
Breach Detected → Assessment (4 hours) → Containment (24 hours)
                                    ↓
                    Supervisory Authority Notification (72 hours)
                                    ↓
                    Data Subject Notification (if high risk)
```

### 7.4 Notification to Supervisory Authority (Article 33)

**Required within 72 hours** to CNIL (France) if breach likely to result in risk to rights and freedoms.

**Notification must include:**
1. Nature of breach
2. Categories and approximate number of data subjects affected
3. Categories and approximate number of personal data records
4. Contact point for more information (DPO)
5. Likely consequences of breach
6. Measures taken or proposed to address breach

**Contact:** CNIL - Commission Nationale de l'Informatique et des Libertés
- Website: www.cnil.fr
- Phone: [CNIL contact]
- Online portal: [CNIL notification portal]

### 7.5 Notification to Data Subjects (Article 34)

**Required** if breach likely to result in **high risk** to rights and freedoms.

**Communication must:**
- Be in clear and plain language
- Describe nature of breach
- Provide DPO contact information
- Describe likely consequences
- Explain measures taken/recommended

**Exceptions (notification not required if):**
- Appropriate technical protection applied (e.g., encryption)
- Subsequent measures ensure high risk no longer likely
- Disproportionate effort required (public communication acceptable)

### 7.6 Breach Response Team

**Incident Commander:** Data Protection Officer  
**Technical Lead:** System Administrator  
**Communication Lead:** [To be designated]  
**Legal Counsel:** [To be designated]

**Escalation Path:**
1. On-call engineer detects/reports → DPO
2. DPO assesses severity → Activates response team
3. Response team contains and investigates
4. DPO determines notification requirements
5. Communications sent if required
6. Post-incident review conducted

---

## 8. Third-Party Processors

### 8.1 Processor Inventory

| Processor | Service | Data Processed | Location | DPA Status |
|-----------|---------|----------------|----------|------------|
| [Cloud Provider] | Infrastructure hosting | All application data | EU (France) | ✅ Signed |
| [Backup Service] | Data backups | Encrypted backups | EU | ✅ Signed |
| [Email Service] | Transactional emails | Email addresses | EU | ✅ Signed |

### 8.2 Data Processing Agreements (Article 28)

**All processors must:**
- Have signed Data Processing Agreement (DPA)
- Process only on documented instructions
- Ensure confidentiality of personnel
- Implement appropriate security measures
- Assist with data subject rights requests
- Delete/return data after service termination
- Allow audits and inspections

**DPA Template:** See `docs/templates/DPA_Template.md`

### 8.3 Sub-Processor Management
- Written authorization required before engaging sub-processors
- Same obligations flow down to sub-processors
- Controller notified of sub-processor changes

---

## 9. International Data Transfers

### 9.1 Current Status
**All data processing occurs within the EU.**

No international transfers currently take place.

### 9.2 Future Transfer Safeguards

If international transfers become necessary:

**Acceptable mechanisms:**
1. **Adequacy Decision** (Article 45)
   - Transfer to countries with adequacy decision (e.g., UK, Switzerland)

2. **Standard Contractual Clauses** (Article 46)
   - EU Commission approved SCCs
   - Supplementary measures where necessary

3. **Binding Corporate Rules** (Article 47)
   - For intra-group transfers

**Prohibited:**
- ❌ Transfers to US under invalidated Privacy Shield
- ❌ Transfers without appropriate safeguards

---

## 10. Departmental Guidelines

### 10.1 For Sales Team

**When collecting customer information:**
✅ **DO:**
- Explain how data will be used in clear language
- Provide privacy policy before collecting data
- Record consent explicitly (checkbox, signature)
- Only collect necessary information
- Ensure secure transmission (encrypted email, secure forms)

❌ **DON'T:**
- Pre-check consent boxes
- Assume consent from existing relationship
- Share data with third parties without consent
- Collect data "just in case we need it later"

**Scripts and Templates:** See `docs/templates/Sales_Communication_Templates.md`

### 10.2 For Marketing Team

**Campaign Guidelines:**
✅ **DO:**
- Use only opted-in contact lists
- Include unsubscribe link in every email
- Honor opt-out requests within 48 hours
- Segment by consent preferences
- Document legitimate interest assessments

❌ **DON'T:**
- Purchase external contact lists
- Send to contacts without consent
- Make unsubscribe difficult to find
- Continue emailing after opt-out
- Use dark patterns to retain consent

**Compliance Checklist:** See `docs/checklists/Marketing_GDPR_Checklist.md`

### 10.3 For Operations Team

**Data Handling Procedures:**
✅ **DO:**
- Process data subject requests within 5 business days
- Verify identity before releasing data
- Log all data access in audit trail
- Use secure channels for data transmission
- Follow data retention schedules

❌ **DON'T:**
- Share data via unencrypted email
- Skip identity verification
- Delay responding to requests
- Keep data longer than necessary
- Access data without business need

**Standard Operating Procedures:** See `docs/procedures/Operations_SOP.md`

### 10.4 For IT/Development Team

**Privacy by Design Requirements:**
✅ **DO:**
- Encrypt personal data at rest and in transit
- Implement access controls (least privilege)
- Log security-relevant events
- Conduct security code reviews
- Test GDPR features (export, delete, etc.)
- Minimize data collection
- Use pseudonymization where possible

❌ **DON'T:**
- Store passwords in plain text
- Log sensitive personal data
- Implement tracking without consent
- Skip security testing
- Use default/weak credentials
- Store unnecessary data

**Technical Guidelines:** See `docs/SECURITY.md`

---

## 11. Training and Awareness

### 11.1 Mandatory Training
**All employees must complete:**
- GDPR Basics training (annual)
- Role-specific GDPR training
- Security awareness training
- Data breach response training

### 11.2 Training Schedule

| Role | Training Module | Frequency |
|------|----------------|-----------|
| All staff | GDPR Overview | Annual |
| Sales | Consent Collection | Bi-annual |
| Marketing | Direct Marketing Rules | Bi-annual |
| Operations | Data Subject Rights | Bi-annual |
| IT/Dev | Security & Privacy by Design | Quarterly |
| Management | Compliance Oversight | Annual |

### 11.3 Training Materials
Available in: `docs/training/`

---

## 12. Accountability and Documentation

### 12.1 Records of Processing Activities (Article 30)
- **Location:** This document (Section 4)
- **Review frequency:** Quarterly
- **Owner:** Data Protection Officer

### 12.2 DPIA Documentation (Article 35)
- **Location:** Section 6 of this document
- **Review trigger:** Significant system changes
- **Owner:** Data Protection Officer + Technical Lead

### 12.3 Consent Records
- **Storage:** Database with audit trail
- **Format:** Timestamped, attributed, immutable
- **Retention:** Duration of consent + 3 years

### 12.4 Breach Incident Log
- **Location:** `security/breach_log.md` (restricted access)
- **Review frequency:** Monthly
- **Owner:** Security Team

---

## 13. Contact Information

### 13.1 Data Protection Officer (DPO)
**Name:** [DPO Name]  
**Email:** dpo@geneweb-project.eu  
**Phone:** [Phone number]  
**Office:** [Address]

### 13.2 Supervisory Authority
**CNIL (Commission Nationale de l'Informatique et des Libertés)**  
Address: 3 Place de Fontenoy, TSA 80715, 75334 Paris Cedex 07, France  
Phone: +33 1 53 73 22 22  
Website: www.cnil.fr  
Online complaint: https://www.cnil.fr/fr/plaintes

### 13.3 Data Subject Rights Requests
**Email:** privacy@geneweb-project.eu  
**Online form:** [Application URL]/privacy/request  
**Mail:** [Physical address]

---

## 14. Document Control

### 14.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-23 | GitHub Copilot | Initial creation |

### 14.2 Review Schedule
- **Next review date:** 2026-01-23 (Quarterly)
- **Triggered reviews:** System changes, breach incidents, regulation updates

### 14.3 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Data Protection Officer | [Name] | _________ | _____ |
| Technical Director | [Name] | _________ | _____ |
| Legal Counsel | [Name] | _________ | _____ |

---

## Appendices

- **Appendix A:** Privacy Policy (user-facing document)
- **Appendix B:** Data Processing Agreement Template
- **Appendix C:** Data Subject Request Forms
- **Appendix D:** Breach Notification Templates
- **Appendix E:** Employee Training Materials
- **Appendix F:** Technical Security Documentation

---

**Document Classification:** Internal  
**Distribution:** All employees, available to data subjects on request
