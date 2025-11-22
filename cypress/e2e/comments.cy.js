describe('Comentários de Animes', () => {
  const timestamp = Date.now();
  const testUsername = `testuser${timestamp}`;
  const testEmail = `test${timestamp}@example.com`;
  const testPassword = 'TestPassword123!';
  const testComment = `Anime incrível! ${timestamp}`;

  beforeEach(() => {
    cy.on('uncaught:exception', (err, runnable) => {
      return false;
    });
  });

  it('deve cadastrar, logar, comentar e verificar comentário', () => {
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
    
    cy.get('#commentContent').type(testComment);
    cy.get('.btn-comment').click();
    cy.wait(2000);
    
    cy.get('.comment-card').should('exist');
    cy.get('.comment-content').should('contain', testComment);
    cy.get('.comment-card').first().should('contain', testUsername);
    
    cy.get('.comment-card').first().then($card => {
      const hasLikeButton = $card.find('.btn-like, .like-button, [class*="like"]').length > 0;
      if (hasLikeButton) {
        cy.wrap($card).find('.btn-like, .like-button, [class*="like"]').first().click();
        cy.wait(1000);
      } else {
        cy.log('Sistema de curtidas não implementado');
      }
    });
  });
});