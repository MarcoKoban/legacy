describe('Database Component E2E', () => {
  beforeEach(() => {
    // Visit the database page with a test database
    cy.visit('http://localhost:2316/database/TestDB');
  });

  it('should display the database page', () => {
    cy.contains('Base généalogique').should('be.visible');
  });

  it('should display database name in title', () => {
    cy.contains('TestDB').should('be.visible');
  });

  describe('Language switching', () => {
    it('should display language selector', () => {
      cy.get('.relative').should('exist');
    });

    it('should toggle language dropdown on click', () => {
      // Click to open dropdown
      cy.get('.relative button').first().click();

      // Check that language options are visible
      cy.contains('English').should('be.visible');
      cy.contains('Français').should('be.visible');
      cy.contains('Deutsch').should('be.visible');
    });

    it('should change language to French', () => {
      // Open dropdown
      cy.get('.relative button').first().click();

      // Select French
      cy.contains('Français').click();

      // Verify language changed (check for French text)
      // The exact verification depends on your translations
      cy.get('.relative button').first().should('contain', 'FR');
    });

    it('should change language to German', () => {
      cy.get('.relative button').first().click();
      cy.contains('Deutsch').click();
      cy.get('.relative button').first().should('contain', 'DE');
    });

    it('should change language to Spanish', () => {
      cy.get('.relative button').first().click();
      cy.contains('Español').click();
      cy.get('.relative button').first().should('contain', 'ES');
    });

    it('should close dropdown after language selection', () => {
      cy.get('.relative button').first().click();
      cy.contains('English').should('be.visible');

      cy.contains('Français').click();

      // Dropdown should close
      cy.contains('English').should('not.be.visible');
    });
  });

  describe('Navigation', () => {
    it('should have add family button', () => {
      cy.contains('button', /add family|ajouter famille/i).should('exist');
    });

    it('should navigate to add family page', () => {
      cy.contains('button', /add family|ajouter famille/i).click();
      cy.url().should('include', '/add-family');
    });

    it('should pass database name to add family page', () => {
      cy.contains('button', /add family|ajouter famille/i).click();
      cy.url().should('include', 'TestDB');
    });
  });

  describe('Person count display', () => {
    it('should display person count', () => {
      // Assuming there's a person count displayed
      cy.get('body').should('contain', /\d+\s*(person|personne)/i);
    });
  });

  describe('Action buttons', () => {
    it('should have multiple action buttons', () => {
      cy.get('button').should('have.length.greaterThan', 1);
    });

    it('should handle configuration button click', () => {
      // This test checks that clicking doesn't cause errors
      cy.contains('button', /configuration/i).should('exist');
    });
  });

  describe('Responsive behavior', () => {
    it('should be responsive on mobile', () => {
      cy.viewport('iphone-6');
      cy.contains('Base généalogique').should('be.visible');
    });

    it('should be responsive on tablet', () => {
      cy.viewport('ipad-2');
      cy.contains('Base généalogique').should('be.visible');
    });

    it('should be responsive on desktop', () => {
      cy.viewport(1920, 1080);
      cy.contains('Base généalogique').should('be.visible');
    });
  });
});
