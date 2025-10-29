describe('HomeComponent E2E', () => {
  beforeEach(() => {
    // Lancer l’app Angular avant chaque test
    cy.visit('http://localhost:2316/');
  });

  it('should display the main title', () => {
    cy.get('h1').invoke('text').should('match', /Management|Gestion/);
  });

  it('should have working internal navigation links', () => {
    // Vérifie le lien "list"
    cy.contains('list').click();
    cy.url().should('include', '/list');
    cy.go('back');

    // Vérifie le lien "errors"
    cy.contains('errors').click();
    cy.url().should('include', '/traces');
    cy.go('back');

    // Vérifie le lien "ged2gwb"
    cy.contains('ged2gwb').click();
    cy.url().should('include', '/ged2Gwb');
  });

  it('should open external documentation link in new tab', () => {
    cy.contains('doc')
      .should('have.attr', 'href', '#')
      .and('be.visible');

    // simulate click and check that window.open is called
    cy.window().then((win) => {
      cy.stub(win, 'open').as('open');
    });
    cy.contains('doc').click();
    cy.get('@open').should('have.been.calledWith', 'http://geneweb.tuxfamily.org/wiki/manual');
  });

  it('should display all main sections', () => {
    cy.contains('Consult').should('be.visible');
    cy.contains('Save').should('be.visible');
    cy.contains('Create Family').should('be.visible');
    cy.contains('Advanced Options').should('be.visible');
    cy.contains('Configure').should('be.visible');
  });

  it('should have a footer logo that links to GitHub', () => {
    cy.get('footer img')
      .should('be.visible')
      .click({ force: true });

    cy.window().then((win) => {
      expect(win.open).to.have.been.calledWith('https://github.com/geneweb/geneweb/');
    });
  });
});
