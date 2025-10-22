describe('Pesquisa de Usuários', () => {
  const timestamp = Date.now();
  const testUsername = `testuser${timestamp}`;
  const testEmail = `test${timestamp}@example.com`;
  const testPassword = 'TestPassword123!';

  beforeEach(() => {
    cy.on('uncaught:exception', (err, runnable) => {
      return false;
    });
  });

  it('deve criar um usuário, pesquisá-lo e acessar seu perfil', () => {
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

    cy.get('#searchInput').type(testUsername);
    cy.get('input[name="search_type"][value="user"]').check();
    cy.get('.search-btn').click();

    cy.url().should('include', '/search/users/');
    cy.contains(testUsername).should('be.visible');

    cy.contains('.user-card', testUsername).click();

    cy.url().should('include', `/users/${testUsername}/`);
    cy.get('.username').should('contain', testUsername);
  });
});