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
      document.getElementById('postModalEmail').innerHTML = content['email_post'];
      document.getElementById('postModalContent').innerHTML = content['file_path'];
      document.getElementById('postModalName').innerHTML = content['item_name'];
      document.getElementById('postModalDate').innerHTML = content['post_time'];
      $('#postModal').modal('show');
    });
  });
});

groups = document.getElementsByClassName('users-card');

Array.from(groups).forEach(function(element) {
  element.addEventListener('click', function(e) {
    e.preventDefault();
    fetch('http://localhost:5000/group/get', {
      method: 'POST',
      body: JSON.stringify({fg_name: this.getElementsByClassName('users-user')[0].innerHTML,
                            owner_email: this.getElementsByClassName('users-tag')[0].innerHTML}),
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(function(response) {
      return response.json();
    })
    .then(function(content) {
      document.getElementById('groupFriendName').innerHTML = content['fg_name'];
      document.getElementById('groupFriendOwner').innerHTML = content['owner_email'];
      document.getElementById('groupFriendDesc').innerHTML = content['description'];
      document.getElementById('groupFriendNameInput').value = content['fg_name'];
      document.getElementById('groupFriendOwnerInput').value = content['owner_email'];
      $('#groupModal').modal('show');
    });

    fetch('http://localhost:5000/group/members', {
      method: 'POST',
      body: JSON.stringify({fg_name: this.getElementsByClassName('users-user')[0].innerHTML,
                            owner_email: this.getElementsByClassName('users-tag')[0].innerHTML}),
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(function(response) {
      return response.json();
    })
    .then(function(content) {
      if (content.length > 0) {
        document.getElementById('groupFriendMembers').innerHTML = ''
        for (member in content) {
          document.getElementById('groupFriendMembers').innerHTML += '<li>' + content['email'] + '</li>'
        }
      }
      document.getElementById('groupFriendMembers').innerHTML = '<li>No members 😥</li>';
    });
  });
});
