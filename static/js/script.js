$(function () {
  $('[data-toggle="popover"]').popover({ trigger: "hover" });
})

let posts = document.getElementsByClassName('post');

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
    .then(content => {
      document.getElementById('postModalEmail').innerHTML = content['email_post'];
      document.getElementById('postModalContent').innerHTML = content['file_path'];
      document.getElementById('postModalName').innerHTML = content['item_name'];
      document.getElementById('postModalDate').innerHTML = content['post_time'];
      document.getElementById('postTag').setAttribute('post-id', content['item_id']);
      document.getElementById('postRate').setAttribute('post-id', content['item_id']);
      document.getElementById('tagId').value = content['item_id'];
      document.getElementById('commentId').value = content['item_id'];
      fetch('http://localhost:5000/tag/get', {
        method: 'POST',
        body: JSON.stringify({item_id: this.getAttribute('post-id')}),
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function(response) {
        return response.json();
      })
      .then(content => {
        document.getElementById('postTag').innerHTML = content.length + '<span> Tags</span>';
        document.getElementById('taggedEmails').innerHTML = '';
        for (tagged in content) {
          document.getElementById('taggedEmails').innerHTML += '<li><span class="font-weight-bold">' + content[tagged]['email_tagger'] + '</span><span> tagged </span><span class="font-weight-bold">' + content[tagged]['email_tagged'] + '</li>'
        }
        fetch('http://localhost:5000/comment/get', {
          method: 'POST',
          body: JSON.stringify({item_id: this.getAttribute('post-id')}),
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(function(response) {
          return response.json();
        })
        .then(content => {
          document.getElementById('postComments').innerHTML = ''
          for (comment in content) {
            document.getElementById('postComments').innerHTML += "<li><div class='post-info'><span class='post-user'>" + content[comment]['commenter_email'] + "</span></div><p>" + content[comment]['comment'] + "</p><span class='post-time'>" + content[comment]['comment_time'] + "</span></li>"
          }
          fetch('http://localhost:5000/rate/get', {
            method: 'POST',
            body: JSON.stringify({item_id: this.getAttribute('post-id')}),
            headers: {
              'Content-Type': 'application/json'
            }
          }).then(function(response) {
            return response.json();
          })
          .then(function(content) {
            document.getElementById('postRate').innerHTML = content.length + '<span> Rate</span>';
            document.getElementById('rateList').innerHTML = '';
            for (rate in content) {
              document.getElementById('rateList').innerHTML += "<li><span class='font-weight-bold'>" + content[rate]['email'] + ": </span><span>" + content[rate]['emoji'] + "</span></li>"
            }
            $('#postModal').modal('show');
          });
        });
      });
    });
  });
});

let tags = document.getElementsByClassName('tag-item');

Array.from(tags).forEach(function(element) {
  element.addEventListener('click', function(e) {
    e.preventDefault();
    fetch('http://localhost:5000/get_post', {
      method: 'POST',
      body: JSON.stringify({item_id: this.innerHTML}),
      headers:{
        'Content-Type': 'application/json'
      }
    }).then(function(response) {
      return response.json();
    })
    .then(content => {
      document.getElementById('postModalEmail').innerHTML = content['email_post'];
      document.getElementById('postModalContent').innerHTML = content['file_path'];
      document.getElementById('postModalName').innerHTML = content['item_name'];
      document.getElementById('postModalDate').innerHTML = content['post_time'];
      document.getElementById('postTag').setAttribute('post-id', content['item_id']);
      document.getElementById('postRate').setAttribute('post-id', content['item_id']);
      document.getElementById('tagId').value = content['item_id'];
      fetch('http://localhost:5000/tag/get', {
        method: 'POST',
        body: JSON.stringify({item_id: this.getAttribute('post-id')}),
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function(response) {
        return response.json();
      })
      .then(content => {
        document.getElementById('postTag').innerHTML = content.length + '<span> Tags</span>';
        document.getElementById('taggedEmails').innerHTML = '';
        for (tagged in content) {
          document.getElementById('taggedEmails').innerHTML += '<li><span>' + content[tagged]['email_tagger'] + '</span><span>tagged</span><span>' + content[tagged]['email_tagged'] + '</li>'
        }
        fetch('http://localhost:5000/rate/get', {
          method: 'POST',
          body: JSON.stringify({item_id: this.getAttribute('post-id')}),
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(function(response) {
          return response.json();
        })
        .then(function(content) {
          console.log(content);
          $('#postModal').modal('show');
        });
      });
    });
  });
});


let groups = document.getElementsByClassName('users-info');

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
    .then(content => {
      document.getElementById('groupFriendName').innerHTML = content['fg_name'];
      document.getElementById('groupFriendOwner').innerHTML = content['owner_email'];
      document.getElementById('groupFriendDesc').innerHTML = content['description'];
      document.getElementById('groupFriendNameInput').value = content['fg_name'];
      document.getElementById('groupFriendOwnerInput').value = content['owner_email'];
      document.getElementById('leaveGroup').value = content['fg_name'];
      document.getElementById('leaveOwner').value = content['owner_email'];
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
            document.getElementById('groupFriendMembers').innerHTML += '<li>' + content[member]['email'] + '</li>'
          }
        } else {
          document.getElementById('groupFriendMembers').innerHTML = '<li>No members 😥</li>';
        }
        $('#groupModal').modal('show');
      });
    });
  });
});

document.getElementById('postTag').addEventListener('click', function(e) {
  e.preventDefault();
  $('#tagModal').modal('show');
});

document.getElementById('postRate').addEventListener('click', function(e) {
  e.preventDefault();
  $('#rateModal').modal('show');
});

document.getElementById('commentButton').addEventListener('click', function(e) {
  e.preventDefault();
  document.getElementById('postCommentForm').focus();
});

var modal_lv = 0;
$('.modal').on('shown.bs.modal', function (e) {
    $('.modal-backdrop:last').css('zIndex',1051 + modal_lv);
    $(e.currentTarget).css('zIndex',1052 + modal_lv);
    modal_lv++
});

$('.modal').on('hidden.bs.modal', function (e) {
    modal_lv--
});

document.getElementById('submissionPrivacy').addEventListener('click', function(e) {
  e.preventDefault();
  if (this.classList.contains("submission-on")) {
    this.classList.remove("submission-on");
    document.getElementById('submissionPrivacyForm').value = 'False';
    $('#privacyMenu').toggle();
  } else {
    this.classList.add("submission-on");
    document.getElementById('submissionPrivacyForm').value = 'True';
    $('#privacyMenu').toggle()
  }
});

let privacyGroups = document.getElementsByClassName('privacy-group')
var shareWith = []

Array.from(privacyGroups).forEach(function(element) {
  element.addEventListener('click', function(e) {
    e.preventDefault();
    if (this.classList.contains("privacy-on")) {
      this.classList.remove("privacy-on");
      fg_name = this.getElementsByClassName('privacy-group-name')[0].innerHTML;
      owner_email = this.getElementsByClassName('privacy-group-owner')[0].innerHTML;
      var index = shareWith.indexOf(fg_name + ':' + owner_email);
      if (index > -1) {
        shareWith.splice(index, 1);
      }
    } else {
      this.classList.add("privacy-on");
      fg_name = this.getElementsByClassName('privacy-group-name')[0].innerHTML;
      owner_email = this.getElementsByClassName('privacy-group-owner')[0].innerHTML;
      var index = shareWith.indexOf(fg_name + ':' + owner_email);
      if (index == -1) {
        shareWith.push(fg_name + ':' + owner_email);
      }
    }
    return false;
  });
});

let emojis = document.getElementsByClassName('emoji-link')
Array.from(emojis).forEach(function(element) {
  element.addEventListener('click', function(e) {
    e.preventDefault();
    var href = e.target.getAttribute('href');
    window.location.href = href + document.getElementById('tagId').value;
  });
});

document.getElementById('submit-form').addEventListener('submit', function(e) {
  e.preventDefault();
  var input = document.createElement('input');
  input.type = 'hidden';
  input.name = 'share';
  input.value = shareWith.join();
  this.appendChild(input);
  this.submit();
});
