describe('Pesquisa de Animes no Otakuverse', () => {
  beforeEach(() => {
    cy.visit('/animes/buscar/')
  })

  it('deve exibir a página de busca vazia', () => {
    cy.get('input#q').should('be.visible')
    cy.get('input#q').should('have.value', '')
    cy.contains('Filtros de Busca').should('be.visible')
  })

  it('deve pesquisar anime pelo nome e exibir resultados', () => {
    cy.get('input#q').type('Naruto')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', '?q=Naruto')
    cy.get('.anime-card').should('exist')
    cy.contains('Animes Encontrados').should('be.visible')
    cy.contains('Naruto').should('be.visible')
  })

  it('deve exibir mensagem quando não encontrar resultados', () => {
    cy.get('input#q').type('AnimeQueNaoExiste123XYZ')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.error-banner').should('be.visible')
    cy.contains('Nenhum anime encontrado').should('be.visible')
  })

  it('deve aplicar filtro de classificação (rating)', () => {
    cy.get('input#q').type('anime')
    cy.get('select#rating').select('pg13')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'rating=pg13')
  })

  it('deve aplicar filtro de tipo (TV, Movie, OVA)', () => {
    cy.get('input#q').type('One Piece')
    cy.get('select#type').select('tv')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'type=tv')
  })

  it('deve aplicar filtro de status (Airing, Complete)', () => {
    cy.get('input#q').type('Attack on Titan')
    cy.get('select#status').select('complete')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'status=complete')
  })

  it('deve aplicar filtro de ordenação', () => {
    cy.get('input#q').type('anime')
    cy.get('select#order_by').select('score')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'order_by=score')
  })

  it('deve aplicar filtro de ano', () => {
    cy.get('input#q').type('anime')
    cy.get('input#year').type('2023')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'year=2023')
  })

  it('deve combinar múltiplos filtros simultaneamente', () => {
    cy.get('input#q').type('Sword Art Online')
    cy.get('select#type').select('tv')
    cy.get('select#status').select('complete')
    cy.get('select#rating').select('pg13')
    cy.get('select#order_by').select('score')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.url().should('include', 'q=Sword')
    cy.url().should('include', 'type=tv')
    cy.url().should('include', 'status=complete')
    cy.url().should('include', 'rating=pg13')
    cy.url().should('include', 'order_by=score')
  })

  it('deve limpar todos os filtros ao clicar em "Limpar Filtros"', () => {
    cy.get('input#q').type('Naruto')
    cy.get('select#type').select('tv')
    cy.get('select#status').select('complete')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.contains('Limpar Filtros').click()
    cy.url().should('not.include', '?')
    cy.get('input#q').should('have.value', '')
  })

  it('deve exibir informações do anime no card (título, score, tipo)', () => {
    cy.get('input#q').type('Demon Slayer')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').first().within(() => {
      cy.get('.anime-title').should('be.visible')
      cy.get('.anime-poster img').should('be.visible')
      cy.get('.anime-type').should('be.visible')
    })
  })

  it('deve clicar em um card e navegar para página de detalhes', () => {
    cy.get('input#q').type('Naruto')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').should('exist')
    cy.get('.anime-card').first().find('a').click()
    cy.url().should('include', '/animes/')
  })

  it('deve manter os filtros ao voltar da página de detalhes', () => {
    cy.get('input#q').type('One Piece')
    cy.get('select#type').select('tv')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').first().find('a').click()
    cy.go('back')
    cy.url().should('include', 'q=One')
    cy.url().should('include', 'type=tv')
    cy.get('input#q').should('have.value', 'One Piece')
    cy.get('select#type').should('have.value', 'tv')
  })

  it('deve exibir score do anime quando disponível', () => {
    cy.get('input#q').type('Fullmetal Alchemist')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').first().within(() => {
      cy.get('.anime-score').should('exist')
    })
  })

  it('deve exibir ano de lançamento quando disponível', () => {
    cy.get('input#q').type('Steins Gate')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').first().within(() => {
      cy.get('.anime-year').should('exist')
    })
  })

  it('deve exibir número de episódios quando disponível', () => {
    cy.get('input#q').type('Death Note')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-episodes').should('exist')
  })

  it('deve carregar imagens dos animes com lazy loading', () => {
    cy.get('input#q').type('Hunter x Hunter')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-poster img').first().should('have.attr', 'loading', 'lazy')
  })

  it('deve exibir overlay com informações ao passar o mouse no card', () => {
    cy.get('input#q').type('My Hero Academia')
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').first().trigger('mouseover')
    cy.get('.anime-overlay').should('exist')
  })

  it('deve filtrar conteúdo adulto por padrão (rating padrão)', () => {
    cy.get('input#q').type('anime')
    cy.contains('button', 'Aplicar Filtros').click()
    cy.get('body').should('not.contain', 'Hentai')
  })

  it('deve validar campo de ano com valores mínimo e máximo', () => {
    cy.get('input#year').should('have.attr', 'min', '1960')
    cy.get('input#year').should('have.attr', 'max', '2025')
  })

  it('deve pesquisar sem preencher o campo de busca', () => {
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('.anime-card').should('not.exist')
  })

  it('deve preservar valor do campo de busca após aplicar filtros', () => {
    const searchTerm = 'Cowboy Bebop'
    cy.get('input#q').type(searchTerm)
    cy.get('button[type="submit"]').contains('Aplicar Filtros').click()
    cy.get('input#q').should('have.value', searchTerm)
  })
})