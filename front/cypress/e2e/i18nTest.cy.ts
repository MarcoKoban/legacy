import 'cypress-axe';

describe('Internationalization (i18n) Tests', () => {
  beforeEach(() => {
    cy.visit('http://localhost:2316/');
  });

  it('should display the title in English by default', () => {
    cy.contains('Management and creation').should('be.visible');
  });

  it('should change the title when switching language to French', () => {
    // Clique sur le lien "Français"
    cy.get('a').contains('Français').click();

    // Vérifie que le texte a changé
    cy.contains('Gestion et création').should('be.visible');
  });

  it('should change the title when switching language to German', () => {
    cy.get('a').contains('Deutsch').click();
    cy.contains('Verwaltung und Erstellung').should('be.visible');
  });
});
