document.getElementById('updateBookForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        title: formData.get('title'),
        author: formData.get('author'),
        kind: formData.get('kind'),
        publication_date: formData.get('publication_date')
    };

    const bookId = event.target.getAttribute('book_id'); // Récupère l'ID du livre depuis un attribut du formulaire

    const response = await fetch(`/update_book/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    if (response.ok) {
        window.location.href = "/gestion_des_livres";  // Redirection après succès
    } else {
        console.error('Erreur lors de la mise à jour du livre');
    }
});
