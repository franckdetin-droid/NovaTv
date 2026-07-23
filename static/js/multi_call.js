const socket = io();

const room = "room_multi";

let localStream;
let peers = {}; // {socketId: RTCPeerConnection}

const config = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" }
    ]
};

// rejoindre
socket.emit("join_room", { room: room });

// récupérer utilisateurs présents
socket.on("all_users", (users) => {
    users.forEach(id => {
        createPeer(id, true);
    });
});

// nouvel utilisateur
socket.on("user_joined", (id) => {
    createPeer(id, false);
});

// recevoir offre
socket.on("offer", async ({ from, offer }) => {
    const peer = createPeer(from, false);

    await peer.setRemoteDescription(offer);

    const answer = await peer.createAnswer();
    await peer.setLocalDescription(answer);

    socket.emit("answer", {
        to: from,
        answer: answer
    });
});

// recevoir réponse
socket.on("answer", async ({ from, answer }) => {
    await peers[from].setRemoteDescription(answer);
});

// ICE
socket.on("ice_candidate", async ({ from, candidate }) => {
    if (peers[from]) {
        await peers[from].addIceCandidate(candidate);
    }
});


// démarrer
async function startCall() {
    localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
    });

    document.getElementById("localVideo").srcObject = localStream;
}


// créer peer
function createPeer(id, initiator) {

    const peer = new RTCPeerConnection(config);

    peers[id] = peer;

    // envoyer flux
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });

    // recevoir flux
    peer.ontrack = (event) => {
        let video = document.getElementById(id);

        if (!video) {
            video = document.createElement("video");
            video.id = id;
            video.autoplay = true;
            video.playsInline = true;
            document.getElementById("videos").appendChild(video);
        }

        video.srcObject = event.streams[0];
    };

    // ICE
    peer.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit("ice_candidate", {
                to: id,
                candidate: event.candidate
            });
        }
    };

    // si initiateur → envoyer offre
    if (initiator) {
        peer.onnegotiationneeded = async () => {
            const offer = await peer.createOffer();
            await peer.setLocalDescription(offer);

            socket.emit("offer", {
                to: id,
                offer: offer
            });
        };
    }

    return peer;
}
