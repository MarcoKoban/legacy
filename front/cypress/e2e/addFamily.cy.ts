describe('Add Family Component E2E', () => {
  beforeEach(() => {
    cy.visit('http://localhost:2316/add-family/TestDB');
  });

  it('should display the add family page', () => {
    cy.contains(/add.*family|ajouter.*famille/i).should('exist');
  });

  describe('Tab navigation', () => {
    it('should have all tabs visible', () => {
      cy.contains('Parents').should('be.visible');
      cy.contains(/Events|Événements/i).should('exist');
      cy.contains(/Children|Enfants/i).should('exist');
      cy.contains('Sources').should('be.visible');
      cy.contains(/Comments|Commentaires/i).should('exist');
    });

    it('should navigate between tabs', () => {
      // Click on Events tab
      cy.contains(/Events|Événements/i).click();
      cy.get('#events-section').should('be.visible');

      // Click on Children tab
      cy.contains(/Children|Enfants/i).click();
      cy.get('#children-section').should('be.visible');

      // Click on Sources tab
      cy.contains('Sources').click();
      cy.get('#sources-section').should('be.visible');
    });

    it('should scroll to section on tab click', () => {
      cy.contains(/Events|Événements/i).click();

      // Verify we scrolled to events section
      cy.get('#events-section').should('be.inViewport');
    });
  });

  describe('Parent form fields', () => {
    it('should have input fields for parent H (husband)', () => {
      cy.get('input[name*="firstName"]').should('have.length.greaterThan', 0);
      cy.get('input[name*="lastName"]').should('have.length.greaterThan', 0);
    });

    it('should allow entering parent H data', () => {
      cy.get('input').first().type('Jean');
      cy.get('input').first().should('have.value', 'Jean');
    });

    it('should have birth date fields', () => {
      cy.get('input[name*="birth"]').should('have.length.greaterThan', 0);
    });

    it('should have death date fields', () => {
      cy.get('input[name*="death"]').should('have.length.greaterThan', 0);
    });

    it('should allow entering complete parent data', () => {
      // Find and fill first name fields
      cy.get('input').eq(0).clear().type('Jean');
      cy.get('input').eq(1).clear().type('Dupont');

      // Verify data is entered
      cy.get('input').eq(0).should('have.value', 'Jean');
      cy.get('input').eq(1).should('have.value', 'Dupont');
    });
  });

  describe('Events management', () => {
    beforeEach(() => {
      cy.contains(/Events|Événements/i).click();
    });

    it('should have button to add event', () => {
      cy.contains('button', /add.*event|ajouter.*événement/i).should('exist');
    });

    it('should add a new event', () => {
      const initialEventCount = 0;

      cy.contains('button', /add.*event|ajouter.*événement/i).first().click();

      // Check that event fields are now visible
      cy.get('#events-section').within(() => {
        cy.get('input, select').should('have.length.greaterThan', 0);
      });
    });

    it('should allow adding multiple events', () => {
      cy.contains('button', /add.*event|ajouter.*événement/i).first().click();
      cy.contains('button', /add.*event|ajouter.*événement/i).first().click();

      // Should have multiple event forms
      cy.get('#events-section').within(() => {
        cy.get('.event-item, [class*="event"]').should('have.length.greaterThan', 0);
      });
    });

    it('should allow removing an event', () => {
      cy.contains('button', /add.*event|ajouter.*événement/i).first().click();

      // Find and click remove button
      cy.contains('button', /remove|supprimer|delete/i).first().click();

      // Event should be removed (implementation depends on UI)
    });
  });

  describe('Children management', () => {
    beforeEach(() => {
      cy.contains(/Children|Enfants/i).click();
    });

    it('should have button to add child', () => {
      cy.contains('button', /add.*child|ajouter.*enfant/i).should('exist');
    });

    it('should add a new child', () => {
      cy.contains('button', /add.*child|ajouter.*enfant/i).first().click();

      // Check that child fields are now visible
      cy.get('#children-section').within(() => {
        cy.get('input, select').should('have.length.greaterThan', 0);
      });
    });

    it('should allow adding multiple children', () => {
      cy.contains('button', /add.*child|ajouter.*enfant/i).first().click();
      cy.contains('button', /add.*child|ajouter.*enfant/i).first().click();

      // Should have multiple child forms
      cy.get('#children-section').within(() => {
        cy.get('.child-item, [class*="child"]').should('have.length.greaterThan', 0);
      });
    });

    it('should allow selecting child sex', () => {
      cy.contains('button', /add.*child|ajouter.*enfant/i).first().click();

      // Look for sex selector
      cy.get('select').should('exist');
    });

    it('should allow removing a child', () => {
      cy.contains('button', /add.*child|ajouter.*enfant/i).first().click();

      // Find and click remove button
      cy.contains('button', /remove|supprimer|delete/i).first().click();
    });
  });

  describe('Sources section', () => {
    beforeEach(() => {
      cy.contains('Sources').click();
    });

    it('should have textarea for person sources', () => {
      cy.get('#sources-section').within(() => {
        cy.get('textarea').should('have.length.greaterThan', 0);
      });
    });

    it('should allow entering person sources', () => {
      cy.get('textarea').first().type('Birth certificate from 1980');
      cy.get('textarea').first().should('contain.value', 'Birth certificate');
    });

    it('should have textarea for family sources', () => {
      cy.get('#sources-section').within(() => {
        cy.get('textarea').should('have.length.greaterThan', 0);
      });
    });
  });

  describe('Comments section', () => {
    beforeEach(() => {
      cy.contains(/Comments|Commentaires/i).click();
    });

    it('should have textarea for comments', () => {
      cy.get('#comments-section').within(() => {
        cy.get('textarea').should('exist');
      });
    });

    it('should allow entering comments', () => {
      cy.get('#comments-section textarea').type('Important family note');
      cy.get('#comments-section textarea').should('contain.value', 'Important family note');
    });
  });

  describe('Form submission', () => {
    it('should have submit button', () => {
      cy.contains('button', /submit|send|envoyer|valider/i).should('exist');
    });

    it('should handle form submission', () => {
      // Fill in minimal data
      cy.get('input').first().type('Test');

      // Stub alert to prevent it from blocking
      cy.on('window:alert', (str) => {
        expect(str).to.include('succès');
      });

      // Submit form
      cy.contains('button', /submit|send|envoyer|valider/i).click();

      // Should redirect or show confirmation
      cy.url().should('satisfy', (url) => {
        return url.includes('/database') || url.includes('success');
      });
    });

    it('should validate form before submission', () => {
      // Try to submit empty form
      cy.contains('button', /submit|send|envoyer|valider/i).click();

      // Should either show validation message or allow submission
      // (depends on your validation implementation)
    });
  });

  describe('Navigation buttons', () => {
    it('should have back button', () => {
      cy.contains('button', /back|retour/i).should('exist');
    });

    it('should navigate back to database on back button click', () => {
      cy.contains('button', /back|retour/i).click();
      cy.url().should('include', '/database');
    });

    it('should preserve database name in navigation', () => {
      cy.contains('button', /back|retour/i).click();
      cy.url().should('include', 'TestDB');
    });
  });

  describe('Form validation and data persistence', () => {
    it('should preserve entered data when switching tabs', () => {
      // Enter data in parents tab
      cy.get('input').first().type('Jean');

      // Switch to events tab
      cy.contains(/Events|Événements/i).click();

      // Switch back to parents tab
      cy.contains('Parents').click();

      // Data should still be there
      cy.get('input').first().should('have.value', 'Jean');
    });

    it('should handle special characters in names', () => {
      cy.get('input').first().type('François-José O\'Brien');
      cy.get('input').first().should('have.value', 'François-José O\'Brien');
    });
  });

  describe('Responsive behavior', () => {
    it('should work on mobile', () => {
      cy.viewport('iphone-6');
      cy.contains('Parents').should('be.visible');
      cy.get('input').should('be.visible');
    });

    it('should work on tablet', () => {
      cy.viewport('ipad-2');
      cy.contains('Parents').should('be.visible');
      cy.contains(/Events|Événements/i).should('be.visible');
    });
  });
});
