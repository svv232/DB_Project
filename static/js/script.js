$(function () {
  $('[data-toggle="popover"]').popover({ trigger: "hover" });
})

posts = document.getElementsByClassName('post');

Array.from(posts).forEach(function(element) {
  element.addEventListener('click', function(e) {
    e.preventDefault();
    fetch('http://localhost:5000/get_post', {
      method: 'POST',
      body: JSON.stringify({item_id: this.getAttribute('post-id')}),
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(function(response) {
      return response.json();
    })
    .then(function(content) {
      document.getElementById('postModalEmail').innerHTML = content['email_post']
      document.getElementById('postModalContent').innerHTML = content['file_path']
      document.getElementById('postModalName').innerHTML = content['item_name']
      document.getElementById('postModalDate').innerHTML = content['post_time']
      $('#postModal').modal('show')
    });
  });
});

fetch('http://localhost:5000/group/get', {
  method: 'POST',
  body: JSON.stringify({item_id: this.getAttribute('post-id')}),
  headers:{
    'Content-Type': 'application/json'
  }
}).then(function(response) {
  return response.json();
})
.then(function(content) {
  document.getElementById('postModalEmail').innerHTML = content['email_post']
  document.getElementById('postModalContent').innerHTML = content['file_path']
  document.getElementById('postModalName').innerHTML = content['item_name']
  document.getElementById('postModalDate').innerHTML = content['post_time']
  $('#postModal').modal('show')
});
