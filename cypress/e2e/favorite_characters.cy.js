describe('Adicionar Personagem aos Favoritos', () => {
  const timestamp = Date.now();
  const testUsername = `testuser${timestamp}`;
  const testEmail = `test${timestamp}@example.com`;
  const testPassword = 'TestPassword123!';

  beforeEach(() => {
    cy.on('uncaught:exception', (err, runnable) => {
      return false;
    });
  });

  it('deve criar conta, pesquisar personagem, adicionar e remover dos favoritos', () => {
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
    
    cy.visit('/lists/personagens/');
    cy.wait(1000);
    
    cy.contains('button', 'Adicionar Personagens').click();
    cy.wait(500);
    
    cy.get('#character-search-input').should('be.visible').type('Shinobu Oshino');
    cy.contains('button', 'Buscar').click();
    
    cy.wait(3000);
    
    cy.get('#results .char-card', { timeout: 10000 }).should('exist');
    cy.get('#results').contains('.char-card h3', 'Shinobu Oshino').should('be.visible');
    cy.get('#results').contains('.char-card', 'Shinobu Oshino').find('.btn-add').click();
    
    cy.wait(2000);
    
    cy.get('#favorites .char-card').contains('h3', 'Shinobu Oshino').should('be.visible');
    
    cy.on('window:confirm', () => true);
    cy.get('#favorites').contains('.char-card', 'Shinobu Oshino').find('.btn-remove').click();
    
    cy.wait(1000);
    
    cy.get('#favorites').should('not.contain', 'Shinobu Oshino');
    cy.get('.empty-list-message').should('be.visible');
  });
});