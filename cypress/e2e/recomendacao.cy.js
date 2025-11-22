describe('Recomendação de Animes', () => {
  const timestamp = Date.now();
  const testUsername = `testuser${timestamp}`;
  const testEmail = `test${timestamp}@example.com`;
  const testPassword = 'TestPassword123!';

  beforeEach(() => {
    cy.on('uncaught:exception', (err, runnable) => {
      return false;
    });
  });

  it('deve cadastrar, logar, recomendar anime e verificar recomendação', () => {
    cy.visit('/users/signup/');
    cy.get('#username').type(testUsername);
    cy.get('#email').type(testEmail);
    cy.get('#password').type(testPassword);
    cy.get('#password_confirm').type(testPassword);
    cy.get('.submit-btn').click();
    
    cy.url().should('include', '/users/login/');
    
    cy.get('#username').type(testUsername);
    cy.get('#password').type(testPassword);
    cy.get('.submit-btn').click();
    
    cy.url().should('include', '/');
    
    cy.visit('/animes/animes/1/', { failOnStatusCode: false });
    cy.wait(2000);
    
    cy.get('#animeSearchInput').type('Naruto');
    cy.wait(2000);
    
    cy.get('.search-result-item').first().click();
    cy.wait(500);
    
    cy.get('#submitRecommendation').click();
    cy.wait(2000);
    
    cy.get('.recommendation-card').should('exist');
    cy.get('.community-recommendations').should('contain', 'Naruto');
  });
});