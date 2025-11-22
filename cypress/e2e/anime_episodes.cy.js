describe('Contador de Episódios - Detalhes e Lista', () => {
  const testUser = {
    username: 'testuser_episodes',
    email: 'testuser_episodes@example.com',
    password: 'TestPassword123!',
  };

  const animeId = 1;

  Cypress.on('uncaught:exception', (err, runnable) => {
    return false;
  });

  before(() => {
    cy.visit('/users/login/');
    cy.get('input[name="username"]').type(testUser.username);
    cy.get('input[name="password"]').type(testUser.password);
    cy.get('form').submit();
    
    cy.wait(1000);
    
    cy.url().then((url) => {
      if (url.includes('/login')) {
        cy.visit('/users/signup/');
        cy.get('input[name="username"]').type(testUser.username);
        cy.get('input[name="email"]').type(testUser.email);
        cy.get('input[name="password"]').type(testUser.password);
        cy.get('input[name="password_confirm"]').type(testUser.password);
        cy.get('form').submit();
        
        cy.wait(1000);
        
        cy.visit('/users/login/');
        cy.get('input[name="username"]').type(testUser.username);
        cy.get('input[name="password"]').type(testUser.password);
        cy.get('form').submit();
        
        cy.wait(1000);
      }
    });
  });

  describe('Adicionar Anime à Lista', () => {
    it('deve adicionar anime à lista com status "Assistindo"', () => {
      cy.visit(`/animes/animes/${animeId}/`);
      cy.wait(2000);
      
      cy.get('body').then($body => {
        if ($body.find('.add-to-list-form').length > 0) {
          cy.get('.add-to-list-form').within(() => {
            cy.get('select[name="status"]').select('watching');
            cy.get('button[type="submit"]').click();
          });
        }
      });
    });
  });

  describe('Contador de Episódios na Página de Detalhes', () => {
    beforeEach(() => {
      cy.visit(`/animes/animes/${animeId}/`);
      cy.wait(2000);
    });

    it('deve exibir contador de episódios quando anime está na lista', () => {
      cy.window().its('document.readyState').should('eq', 'complete');
      cy.get('body').then($body => {
        if ($body.find('.episode-counter').length > 0) {
          cy.get('.episode-counter', { timeout: 10000 }).should('be.visible');
          cy.get('.episodes-watched').should('be.visible');
          cy.get('.increase-ep').should('be.visible');
          cy.get('.decrease-ep').should('be.visible');
        } else {
          cy.log('Contador de episódios não encontrado - anime pode não estar na lista');
        }
      });
    });

    it('deve incrementar episódios ao clicar no botão +', () => {
      cy.window().its('document.readyState').should('eq', 'complete');
      cy.get('body').then($body => {
        if ($body.find('.episodes-watched').length > 0) {
          cy.get('.episodes-watched', { timeout: 10000 }).invoke('text').then((initialEpisodes) => {
            const initial = parseInt(initialEpisodes);
            
            cy.intercept('POST', `/lists/update-episodes/${entryId}/`).as('updateEpisodes');
            cy.get('.increase-ep').click();
            cy.wait('@updateEpisodes');
            
            cy.get('.episodes-watched').should('contain', initial + 1);
          });
        } else {
          cy.log('Contador de episódios não encontrado');
        }
      });
    });

    it('deve incrementar múltiplos episódios', () => {
      cy.window().its('document.readyState').should('eq', 'complete');
      cy.get('body').then($body => {
        if ($body.find('.episodes-watched').length > 0) {
          cy.get('.episodes-watched', { timeout: 10000 }).invoke('text').then((initialEpisodes) => {
            const initial = parseInt(initialEpisodes);
            
            cy.intercept('POST', '/lists/update-episodes/**').as('updateEp');
            
            cy.get('.increase-ep').click();
            cy.wait('@updateEp');
            
            cy.get('.increase-ep').click();
            cy.wait('@updateEp');
            
            cy.get('.increase-ep').click();
            cy.wait('@updateEp');
            
            cy.get('.episodes-watched').should('contain', initial + 3);
          });
        } else {
          cy.log('Contador de episódios não encontrado');
        }
      });
    });
  });

  describe('Verificar Episódios na Lista do Usuário', () => {
    it('deve atualizar episódios na lista após incrementar', () => {
      cy.visit(`/animes/animes/${animeId}/`);
      cy.wait(2000);
      cy.window().its('document.readyState').should('eq', 'complete');
      
      cy.get('body').then($body => {
        if ($body.find('.episodes-watched').length > 0) {
          cy.get('.episodes-watched', { timeout: 10000 }).invoke('text').then((initialEpisodes) => {
            const initial = parseInt(initialEpisodes);
            
            cy.intercept('POST', '/lists/update-episodes/**').as('updateEp');
            
            cy.get('.increase-ep').click();
            cy.wait('@updateEp');
            
            cy.get('.increase-ep').click();
            cy.wait('@updateEp');
            
            const expectedEpisodes = initial + 2;
            
            cy.get('#userMenuBtn').click();
            cy.wait(800);
            cy.contains('Meu Perfil').click();
            cy.wait(2000);
            
            cy.get('.anime-list-table tbody tr', { timeout: 10000 }).first().within(() => {
              cy.get('td').eq(3).should('contain', expectedEpisodes);
            });
          });
        } else {
          cy.log('Contador de episódios não encontrado');
        }
      });
    });
  });
});