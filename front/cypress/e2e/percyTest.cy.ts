describe('Visual Regression - HomeComponent', () => {
  it('should match previous snapshot', () => {
    cy.visit('http://localhost:2316');
    cy.percySnapshot('Home Page');
  });
});
