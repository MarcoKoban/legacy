import 'cypress-axe';

describe('Accessibility check - TracesComponent', () => {
  beforeEach(() => {
    cy.visit('http://localhost:2316/traces');
    cy.injectAxe();
  });

  it('should have no accessibility violations', () => {
  cy.checkA11y(
    null,
    {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa'],
      },
    },
    (violations) => {
      if (violations.length) {
        cy.log(`${violations.length} accessibility violation(s) detected`);
        violations.forEach(v => {
          cy.log(`Violation: ${v.id} on ${v.nodes.map(n => n.target).join(', ')}`);
        });
      }
    }
  );
});
});
