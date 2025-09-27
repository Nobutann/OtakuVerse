document.addEventListener('DOMContentLoaded', function() {
    const removeButton = document.querySelector('button[type="submit"]');
    
    if (removeButton) {
        removeButton.addEventListener('click', function(e) {
            const confirmed = confirm('ÚLTIMA CONFIRMAÇÃO \n\nVocê está prestes a remover "{{ entry.anime.title }}" permanentemente da sua lista.\n\nTodos os seus dados (nota, progresso, datas, anotações) serão perdidos para sempre.\n\nDeseja realmente continuar?');
            
            if (!confirmed) {
                e.preventDefault();
                return false;
            }
        });
    }
});