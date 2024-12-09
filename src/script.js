document.querySelectorAll('.category').forEach(category => {
    category.addEventListener('click', () => {
        alert(`Vous avez cliqué sur : ${category.querySelector('h3').textContent}`);
    });
});
