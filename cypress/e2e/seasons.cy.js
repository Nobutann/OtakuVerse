describe('Animes Sazonais', () => {
  beforeEach(() => {
    cy.visit('/animes/sazonais/');
  });

  describe('Carregamento da Página', () => {
    it('deve carregar a página de sazonais corretamente', () => {
      cy.get('.season-hero').should('be.visible');
      cy.get('.season-title .highlight').should('contain', 'Animes da Temporada');
      cy.get('.season-subtitle').should('be.visible');
    });

    it('deve exibir o container de temporadas', () => {
      cy.get('.seasons-container').should('be.visible');
    });
  });

  describe('Blocos de Temporadas', () => {
    it('deve exibir pelo menos uma temporada', () => {
      cy.get('.season-block').should('have.length.at.least', 1);
    });

    it('deve exibir 4 temporadas', () => {
      cy.get('.season-block').should('have.length', 4);
    });

    it('deve exibir cabeçalho correto em cada temporada', () => {
      cy.get('.season-block').first().within(() => {
        cy.get('.season-block-header').should('be.visible');
        cy.get('.section-title').should('exist').and('not.be.empty');
        cy.get('.section-subtitle').should('exist').and('not.be.empty');
      });
    });
  });

  describe('Grid de Animes', () => {
    it('deve exibir grid de animes em cada temporada', () => {
      cy.get('.season-block').first().within(() => {
        cy.get('.anime-grid').should('exist');
      });
    });

    it('deve exibir cards de anime', () => {
      cy.get('.anime-grid').first().within(() => {
        cy.get('.anime-card').should('have.length.at.least', 1);
      });
    });

    it('deve exibir no máximo 10 animes por temporada', () => {
      cy.get('.anime-grid').first().within(() => {
        cy.get('.anime-card').should('have.length.lte', 10);
      });
    });
  });

  describe('Cards de Anime', () => {
    it('deve exibir elementos básicos do card', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-poster img').should('be.visible');
        cy.get('.anime-title').should('be.visible').and('not.be.empty');
        cy.get('.anime-link').should('have.attr', 'href');
      });
    });

    it('deve exibir imagem com src válido', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-poster img')
          .should('have.attr', 'src')
          .and('include', 'http');
      });
    });

    it('deve ter lazy loading nas imagens', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-poster img')
          .should('have.attr', 'loading', 'lazy');
      });
    });

    it('deve exibir overlay com informações', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-overlay').should('exist');
        cy.get('.anime-info').should('exist');
      });
    });

    it('deve exibir score quando disponível', () => {
      cy.get('.anime-card').first().then($card => {
        const scoreEl = $card.find('.anime-score');
        if (scoreEl.length > 0) {
          cy.wrap($card).within(() => {
            cy.get('.anime-score').should('contain', '⭐');
          });
        }
      });
    });

    it('deve exibir meta informações', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-meta').should('exist');
      });
    });

    it('deve exibir sinopse quando disponível', () => {
      cy.get('.anime-card').first().then($card => {
        const synopsisEl = $card.find('.anime-synopsis');
        if (synopsisEl.length > 0) {
          cy.wrap($card).within(() => {
            cy.get('.anime-synopsis').should('exist').and('not.be.empty');
          });
        }
      });
    });
  });

  describe('Navegação', () => {
    it('deve ter links válidos para detalhes', () => {
      cy.get('.anime-card').first().within(() => {
        cy.get('.anime-link')
          .should('have.attr', 'href')
          .and('match', /\/animes\/animes\/\d+\//);
      });
    });

    it('deve navegar para página de detalhes ao clicar', () => {
      cy.get('.anime-card').first().find('.anime-link').click();
      cy.url().should('match', /\/animes\/animes\/\d+\//);
    });

    it('deve ter link no header para sazonais', () => {
      cy.get('.nav-menu').within(() => {
        cy.contains('Sazonais')
          .should('have.attr', 'href')
          .and('include', '/animes/sazonais/');
      });
    });
  });

  describe('Ordem das Temporadas', () => {
    it('deve exibir temporadas em ordem decrescente', () => {
      cy.get('.section-title').then($titles => {
        const years = [...$titles].map(el => {
          const match = el.textContent.match(/\d{4}/);
          return match ? parseInt(match[0]) : 0;
        });

        for (let i = 1; i < years.length; i++) {
          expect(years[i]).to.be.lte(years[i - 1]);
        }
      });
    });

    it('deve começar com a temporada atual ou próxima', () => {
      const currentYear = new Date().getFullYear();
      cy.get('.section-title').first().should('contain', currentYear);
    });
  });

  describe('Temporadas Específicas', () => {
    const seasons = ['Inverno', 'Primavera', 'Verão', 'Outono'];

    it('deve exibir nomes de temporadas válidos', () => {
      cy.get('.section-title').each($title => {
        const text = $title.text();
        const hasSeason = seasons.some(season => text.includes(season));
        expect(hasSeason).to.be.true;
      });
    });

    it('deve ter classes CSS correspondentes às temporadas', () => {
      cy.get('.season-block-header').each($header => {
        const classList = Array.from($header[0].classList);
        const hasSeasonClass = classList.some(cls => 
          ['inverno', 'primavera', 'verão', 'outono'].includes(cls)
        );
        expect(hasSeasonClass).to.be.true;
      });
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve exibir mensagem de erro quando API falhar', () => {
      cy.intercept('GET', '**/v4/seasons/**', {
        statusCode: 500,
        body: { error: 'Internal Server Error' }
      }).as('apiError');

      cy.reload();

      cy.get('body').then($body => {
        if ($body.find('.error-banner').length > 0) {
          cy.get('.error-banner').should('be.visible');
        }
      });
    });

    it('deve exibir mensagem quando temporada não tem animes', () => {
      cy.get('body').then($body => {
        const noResults = $body.find('.no-results');
        if (noResults.length > 0) {
          cy.get('.no-results-text')
            .should('contain', 'Nenhum anime disponível nesta temporada');
        }
      });
    });
  });
});