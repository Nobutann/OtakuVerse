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

    cy.get('#searchInput').type('Shinobu Oshino');
    cy.get('input[name="search_type"][value="character"]').check();
    cy.get('.search-btn').click();

    cy.url().should('include', '/search/characters/');
    cy.get('.results-query').should('contain', 'Shinobu Oshino');
    cy.get('.char-card').should('exist');
    cy.contains('.char-card h3', 'Shinobu Oshino').should('be.visible');

    cy.contains('.char-card', 'Shinobu Oshino').find('.btn-add').click();

    cy.url().should('include', '/lists/personagens/');
    cy.contains('.char-card h3', 'Shinobu Oshino').should('be.visible');

    cy.on('window:confirm', () => true);

    cy.contains('.char-card', 'Shinobu Oshino').find('.btn-remove').click();

    cy.contains('.char-card h3', 'Shinobu Oshino').should('not.exist');
    cy.get('.empty-list-message').should('be.visible');
  });
});