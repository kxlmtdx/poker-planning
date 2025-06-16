function toggleVotes(issueId) {
    const el = document.getElementById('votes-' + issueId);
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}