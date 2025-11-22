Cypress.on('uncaught:exception', (err, runnable) => {
  return false
})

Cypress.Commands.add('login', (username, password) => {
  cy.session([username, password], () => {
    cy.visit('/users/login/')
    cy.get('#username').type(username)
    cy.get('#password').type(password)
    cy.get('button[type="submit"]').click()
    cy.url().should('not.include', '/users/login/')
  })
  cy.visit('/')
})

Cypress.Commands.add('createUser', (username, email, password) => {
  cy.visit('/users/signup/')
  cy.get('#username').clear().type(username)
  cy.get('#email').clear().type(email)
  cy.get('#password').clear().type(password)
  cy.get('#password_confirm').clear().type(password)
  cy.get('button[type="submit"]').click()
  cy.wait(1000)
})

describe('Testes de Lista de Animes', () => {
  const testUser = {
    username: 'testlist',
    email: 'list@test.com',
    password: 'senha12345'
  }

  before(() => {
    cy.createUser(testUser.username, testUser.email, testUser.password)
  })

  beforeEach(() => {
    cy.login(testUser.username, testUser.password)
  })

  it('Deve adicionar anime com status Assistindo', () => {
    cy.visit('/animes/animes/1/', { failOnStatusCode: false })
    cy.wait(3000)
    
    cy.get('body').then($body => {
      if ($body.find('form.add-to-list-form').length > 0) {
        cy.get('form.add-to-list-form select[name="status"]').select('watching')
        cy.get('form.add-to-list-form button[type="submit"]').first().click()
        cy.wait(2000)
      } else {
        cy.log('Anime já está na lista')
      }
    })
    
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('table tbody tr').should('not.contain', 'Nenhum anime encontrado')
  })

  it('Deve adicionar anime com status Completo', () => {
    cy.visit('/animes/animes/20/', { failOnStatusCode: false })
    cy.wait(3000)
    
    cy.get('body').then($body => {
      if ($body.find('form.add-to-list-form').length > 0) {
        cy.get('form.add-to-list-form select[name="status"]').select('completed')
        cy.get('form.add-to-list-form button[type="submit"]').first().click()
        cy.wait(2000)
      } else {
        cy.log('Anime já está na lista')
      }
    })
    
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('.status-label.status-completed').should('be.visible')
  })

  it('Deve adicionar anime com status Planejo Assistir', () => {
    cy.visit('/animes/animes/21/', { failOnStatusCode: false })
    cy.wait(3000)
    
    cy.get('body').then($body => {
      if ($body.find('form.add-to-list-form').length > 0) {
        cy.get('form.add-to-list-form select[name="status"]').select('ptw')
        cy.get('form.add-to-list-form button[type="submit"]').first().click()
        cy.wait(2000)
      } else {
        cy.log('Anime já está na lista')
      }
    })
    
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('.status-label.status-ptw').should('be.visible')
  })

  it('Deve mostrar anime na lista do usuário', () => {
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('table tbody tr').should('not.contain', 'Nenhum anime encontrado')
    cy.get('.anime-title').should('have.length.at.least', 3)
  })

  it('Deve filtrar por status Assistindo', () => {
    cy.visit(`/lists/${testUser.username}/?status=watching`)
    cy.wait(500)
    cy.get('table tbody tr').should('not.contain', 'Nenhum anime encontrado')
    cy.get('.status-label.status-watching').should('be.visible')
  })

  it('Deve filtrar por status Completo', () => {
    cy.visit(`/lists/${testUser.username}/?status=completed`)
    cy.wait(500)
    cy.get('table tbody tr').should('not.contain', 'Nenhum anime encontrado')
    cy.get('.status-label.status-completed').should('be.visible')
  })

  it('Deve remover anime da lista', () => {
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('a.delete-btn').first().click()
    cy.url().should('include', '/remove')
    cy.get('form button[type="submit"]').first().click()
  })

  it('Deve adicionar múltiplos animes', () => {
    const animeIds = [5, 6, 7]
    
    animeIds.forEach(id => {
      cy.visit(`/animes/animes/${id}/`, { failOnStatusCode: false })
      cy.wait(3000)
      
      cy.get('body').then($body => {
        if ($body.find('form.add-to-list-form').length > 0) {
          cy.get('form.add-to-list-form select[name="status"]').select('watching')
          cy.get('form.add-to-list-form button[type="submit"]').click()
          cy.wait(2000)
        }
      })
    })
    
    cy.visit(`/lists/${testUser.username}/`)
    cy.get('table tbody tr').should('not.contain', 'Nenhum anime encontrado')
    cy.get('.anime-title').should('have.length.at.least', 5)
  })
})