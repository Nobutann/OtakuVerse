describe('Ranking de Animes - Top Animes', () => {
  beforeEach(() => {
    cy.visit('/animes/ranking/animes/');
  });

  describe('Verificações da Página', () => {
    it('deve carregar a página de ranking corretamente', () => {
      cy.get('.ranking-hero').should('be.visible');
      cy.get('.ranking-title .highlight').should('contain', 'Top Animes');
      cy.get('.ranking-subtitle')
        .should('contain', 'Os animes mais bem avaliados pelos otakus do mundo');
    });

    it('deve exibir a grid de animes', () => {
      cy.get('.anime-grid').should('be.visible');
      cy.get('.anime-card').should('have.length.at.least', 1);
    });
  });

  describe('Cards de Anime', () => {
    it('deve exibir todos os elementos do card', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.rank-badge .rank-number').should('be.visible');
        cy.get('.poster-image')
          .should('be.visible')
          .and('have.attr', 'src')
          .and('not.be.empty');
        cy.get('.anime-title').should('be.visible').and('not.be.empty');
        cy.get('.anime-meta').should('be.visible');
      });
    });

    it('deve exibir o número do ranking corretamente', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.rank-number').should('contain', '#1');
      });
      
      cy.get('.anime-card').eq(1).within(() => {
        cy.get('.rank-number').should('contain', '#2');
      });
    });

    it('deve exibir score do anime', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-score')
          .should('exist')
          .and('contain', '⭐');
      });
    });

    it('deve exibir tipo e episódios do anime', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-type').should('be.visible');
        cy.get('.anime-episodes').should('exist');
      });
    });
  });

  describe('Navegação e Links', () => {
    it('deve ter links funcionais para detalhes do anime', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-link')
          .should('have.attr', 'href')
          .and('match', /\/animes\/animes\/\d+\//);
      });
    });

    it('deve navegar para página de detalhes ao clicar no card', () => {
      cy.get('.anime-card').first().find('.anime-link').click();
      cy.url().should('match', /\/animes\/animes\/\d+\//);
    });
  });

  describe('Paginação', () => {
    it('deve exibir controles de paginação quando existirem múltiplas páginas', () => {
      cy.get('.pagination-nav').then($nav => {
        if ($nav.length > 0) {
          cy.get('.pagination-nav').should('be.visible');
          cy.get('.pagination').should('exist');
          cy.get('.current-page').should('be.visible');
        }
      });
    });

    it('deve exibir informação da página atual', () => {
      cy.get('.current-page').then($page => {
        if ($page.length > 0) {
          cy.get('.current-page')
            .should('contain', 'Página')
            .and('contain', 'de');
        }
      });
    });

    it('deve navegar para próxima página', () => {
      cy.get('a[aria-label="Próxima página"]').then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.url().should('include', 'page=2');
          cy.get('.anime-card').should('have.length.at.least', 1);
        }
      });
    });

    it('deve navegar para página anterior', () => {
      cy.visit('/animes/ranking/animes/?page=2');
      cy.get('a[aria-label="Página anterior"]').then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.url().should('include', 'page=1');
        }
      });
    });

    it('deve navegar para primeira página', () => {
      cy.visit('/animes/ranking/animes/?page=2');
      cy.get('a[aria-label="Primeira página"]').then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.url().should('include', 'page=1');
        }
      });
    });

    it('deve navegar para última página', () => {
      cy.get('a[aria-label="Última página"]').then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.url().should('match', /page=\d+/);
          cy.get('.anime-card').should('have.length.at.least', 1);
        }
      });
    });
  });

  describe('Imagens', () => {
    it('deve carregar as imagens dos animes corretamente', () => {
      cy.get('.poster-image').first()
        .should('be.visible')
        .and('have.attr', 'src')
        .and('include', 'https://');
    });

    it('deve ter atributo alt nas imagens', () => {
      cy.get('.poster-image').first()
        .should('have.attr', 'alt')
        .and('not.be.empty');
    });

    it('deve ter lazy loading nas imagens', () => {
      cy.get('.poster-image').first()
        .should('have.attr', 'loading', 'lazy');
    });
  });

  describe('Overlay e Hover', () => {
    it('deve conter elementos do overlay', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-overlay').should('exist');
        cy.get('.anime-info').should('exist');
        cy.get('.anime-score').should('exist');
      });
    });

    it('deve exibir ano do anime no overlay quando disponível', () => {
      cy.get('.anime-card').first().then($card => {
        const yearEl = $card.find('.anime-year');
        if (yearEl.length > 0) {
          cy.wrap($card).within(() => {
            cy.get('.anime-year').should('exist');
          });
        }
      });
    });
  });

  describe('Ordenação e Ranking', () => {
    it('deve exibir 20 animes por página', () => {
      cy.get('.anime-card').should('have.length', 20);
    });

    it('deve manter ordem sequencial do ranking', () => {
      cy.get('.rank-number').then($ranks => {
        const ranks = [...$ranks].map(el => parseInt(el.textContent.replace('#', '')));
        for (let i = 1; i < ranks.length; i++) {
          expect(ranks[i]).to.equal(ranks[i - 1] + 1);
        }
      });
    });
  });

  describe('Navegação pelo Header', () => {
    it('deve ter link para Top Animes no header', () => {
      cy.get('.nav-menu').within(() => {
        cy.contains('Top Animes')
          .should('have.attr', 'href')
          .and('include', '/animes/ranking/animes/');
      });
    });

    it('deve poder voltar para homepage', () => {
      cy.get('.logo').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve exibir mensagem quando não houver animes', () => {
      cy.intercept('GET', '**/v4/top/anime*', {
        statusCode: 200,
        body: { data: [] }
      }).as('emptyResponse');

      cy.visit('/animes/ranking/animes/');
      cy.wait('@emptyResponse');

      cy.get('.no-results').then($result => {
        if ($result.length > 0) {
          cy.get('.no-results-text')
            .should('contain', 'Nenhum anime encontrado no momento');
        }
      });
    });
  });
});