window.onload = init;

function init() {
  getServerInfo();
}

var info = [];
var ws = null;
var listGen = false;
var refresh = false;

// Start/reset websocket and create listeners
async function getServerInfo() {
  $('#error').hide(250);
  $('.button-enable').html('<span class="material-icons">power_settings_new</span>')
  if (ws) { ws.close() };
  ws = new WebSocket('ws://98.238.221.173:8765')  // 98.238.221.173
  ws.onopen = function() {
    ws.send(JSON.stringify('Connected'));
  };
  ws.onmessage = function(event) {
    packet = JSON.parse(event.data);
    createList(packet)
    console.log(packet)
    updateInterface(packet);
  };
  ws.onclose = function() {
    if (refresh == false) { $('#error').show(250) };
    refresh = false;
  };
};

// Create server cards
async function createList(packet) {
  if (listGen == false) {
    for (const info of packet) {
      if (typeof info === 'object' && packet.indexOf(info) < packet.length - 2) {
        serverCard = `<li class="serverCard">
                        <div class="card-info">
                          <p class="card-title">${info['name']}<span class="ping">0ms</span></p>
                          <p class="card-status">${info['active'] ? 'Active' : 'Inactive'} • ${info['online']}/${info['max']} Playing</p>
                          <p class="card-motd">${info['motd']}</p>
                        </div>
                        <div class="card-control">
                          <button type="button" class="button-enable"><span class="material-icons">power_settings_new</span></button>
                          <form class="verify">
                            <label for="pass">Pass:</label>
                            <input type="password" class="pass">
                          </form>
                        </div>
                      </li>`

        $('#loading').before(serverCard);
      };
    };

    $('.verify, #error, #loading').hide();

    listGen = true;
    handleButtons();

  };
}

// Update elements with new information
async function updateInterface(packet) {
  $('.widget .serverCard').not('.statCard, #loading').each(function(i) {
    var info = packet[i]

    $('.card-title', this).html(info['name'] + `<span class="ping">${info['ping']}ms</span>`)

    $('.card-status', this).html(`${info['active'] ? 'Active' : 'Inactive'} • ${info['online']}/${info['max']} Playing`)
      .prop('title', info['names'].join(', '));

    $('.card-motd', this).html(info['motd']);

    info['active'] ? $(this).css('filter', 'hue-rotate(280deg)')
      : $(this).css('filter', 'hue-rotate(100deg)');
  });

  var specs = packet[packet.length - 2]
  var cpu = specs['cpu'];
  var ram = specs['ram'];
  var disc = specs['disc'];

  $('#cpu p').html(`CPU: ${cpu}%`);
  $('#ram p').html(`RAM: ${ram}%`);
  $('#disc p').html(`Disc: ${disc}%`);

  cpu < 60 ? $('#cpu').css('filter', 'hue-rotate(280deg)') : cpu < 80 ? $('#cpu').css('filter', 'hue-rotate(170deg)') : $('#cpu').css('filter', 'hue-rotate(100deg)');
  ram < 70 ? $('#ram').css('filter', 'hue-rotate(280deg)') : cpu < 90 ? $('#ram').css('filter', 'hue-rotate(170deg)') : $('#ram').css('filter', 'hue-rotate(100deg)');
};

// Button listeners and logic
async function handleButtons() {
  $('.button-enable').on('click', function() {
    $(this).html('<span class="material-icons spin">autorenew</span>')
    setTimeout(function() {
      refresh = true;
      getServerInfo();
    }, 6000);
    index = $(this).parents('.serverCard').index() - 1
    if (packet[index]['active']) {
      $(this).siblings('.verify').toggle(250)

        .unbind().submit(function(event) {
          event.preventDefault();
          var value = $(this).children('.pass').val();
          if (value == packet[packet.length - 1]) {
            serverSwitch(index, false);
            $(this).siblings('.verify').hide(250);
          }
        });
    }

    else {
      $(this).siblings('.verify').hide(250);
      serverSwitch(index, true);
    };
  });
  $('#retry').on('click', function() {
    getServerInfo();
  });
}

// Send
async function serverSwitch(index, state) {
  await ws.send(JSON.stringify([index, state]));
}
