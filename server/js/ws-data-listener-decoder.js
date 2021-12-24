// Web socket stuff
var WebSocketStateEnum = {CONNECTING: 0, OPEN: 1, CLOSED: 2};
var wsSocket = null;
var msgQueue = [];
var wsChannel;
var wsChannelState = WebSocketStateEnum.CLOSED;

// Media transfer state
var SongTransferStateEnum = {WAITING: 0, IN_PROGRESS: 1};
var currentSongTransferState = SongTransferStateEnum.WAITING;
var currentSongFrequency = -1;
var currentSongChannelCount = -1;
var currentSongDurationMs = -1;
var currentSongBytesTransferred = -1;

self.addEventListener('message', function(e) 
{
	var data = e.data;

	switch (data.cmd) {
		case 'init':
			wsInit(data.host, data.port);
			break;
		default:
            // TODO?
			// self.postMessage('Unknown command: ' + data.msg);
		};
}, false);

function wsInit(host, port) 
{
    var connectionAddr = `ws://${host}:${port}`;
    wsSocket = new WebSocket(connectionAddr);
    wsSocket.onmessage = function(event) 
    {
        var MSG_ID_HEADER = 0x1000FA01;
        var MSG_ID_CHUNK  = 0x1000FA02;

        event.data.arrayBuffer().then(data => {
            if (data.length < 4)
            {
                // Need at least four bytes for the message ID.
                return;
            }
            console.log(data.byteLength)

            const intMessageIdView = new Int32Array(data.slice(0, 4));

            // First four bytes ought to be the message ID.
            message_id = intMessageIdView[0];
            if (message_id == MSG_ID_HEADER)
            {
                console.log('HEADER')
                if (currentSongTransferState != SongTransferStateEnum.WAITING)
                {
                    // This is weird and shouldn't happen.
                    return;
                }

                const intHeaderView = new Int32Array(data.slice(0, 16));
                currentSongFrequency = intHeaderView[1];
                currentSongChannelCount = intHeaderView[2];
                currentSongDurationMs = intHeaderView[3];
                currentSongBytesTransferred = 0;

                currentSongTransferState = SongTransferStateEnum.IN_PROGRESS;
            }
            else if (message_id == MSG_ID_CHUNK)
            {
                console.log('CHUNK')
                if (currentSongTransferState != SongTransferStateEnum.IN_PROGRESS)
                {
                    // This is also weird and shouldn't happen.
                    return;
                }

                const intChunkView = new Int32Array(data.slice(0, 8));
                var chunkSize = intChunkView[1];
                chunkDataArray = new Uint8Array(data.slice(8));

                // This transfers ownership... right?
                const bytesPerSample = 4; // Single-precision floats
                var samplesTransferred = 
                    currentSongBytesTransferred / bytesPerSample / currentSongChannelCount;

                self.postMessage({
                    'chunk_time_ms' : samplesTransferred * currentSongFrequency,
                    'chunk_data' : chunkDataArray });
                currentSongBytesTransferred += chunkSize;
                console.log(
                    'Transferred chunk of ' + chunkSize + 
                    ' bytes! (' + chunkDataArray.byteLength + ')');
                console.log(currentSongBytesTransferred + ' bytes in total.');

                // TODO: Need to check when transfer is done and set the song transfer state.
            }
            else
            {
                // Bad.
                console.log('Nope message ID: 0x' + message_id.toString(16))
            }
        });
    };

    wsSocket.onopen = function(event) 
    {
        wsChannelState = WebSocketStateEnum.OPEN;

        get_song_msg = { 'cmd' : 'send_song', 'song_name' : 'paradox' };
        send(JSON.stringify(get_song_msg));
    };

    wsSocket.onclose = function(event) 
    {
        wsChannelState = WebSocketStateEnum.CLOSED;
    };

    function send(message) 
    {
        if (wsChannelState != WebSocketStateEnum.OPEN)
        {
            msgQueue.push(message);
        }
        else
        {
            send_queued();
            wsSocket.send(message);
        }
    }

    function send_queued()
    {
        // Send everything that was queued up while we were waiting to open the socket.
        while(msgQueue.length > 0)
        {
            queuedMessage = msgQueue.shift();
            wsSocket.send(queuedMessage)
        }
    }
}
