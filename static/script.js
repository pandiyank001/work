document.getElementById('wfh-form').addEventListener('submit', function(event) {
    event.preventDefault();

    let userId = document.getElementById('user_id').value.trim();
    let fromDate = document.getElementById('from-date').value;
    let toDate = document.getElementById('to-date').value;
    let reason = document.getElementById('reason').value.trim();

    if (!userId || !fromDate || !toDate || !reason) {
        alert('All fields must be filled out');
        return;
    }

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            user_id: userId,
            from_date: fromDate,
            to_date: toDate,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            document.getElementById('errorMessage').innerText = data.message;
            var modal = document.getElementById("errorModal");
            var span = document.getElementsByClassName("close")[0];

            modal.style.display = "block";

            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        } else {
            alert(data.message);
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
});
