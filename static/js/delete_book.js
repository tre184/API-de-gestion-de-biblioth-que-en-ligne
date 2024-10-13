function deleteBook(bookId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce livre ?')) {
        fetch(`/delete_book/${bookId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();  // Recharger la page après la suppression
            } else {
                alert('Erreur lors de la suppression du livre');
            }
        });
    }
    return false;  // Empêche le rechargement de la page
}