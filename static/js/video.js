const socket = io();


// ==========================
// VARIABLES
// ==========================

const room = "appel_video_1";

let localStream = null;

let peers = {};


// ==========================
// ELEMENTS
// ==========================

const videos = document.getElementById("videos");


// ==========================
// CAMERA + MICRO
// ==========================

async function startCall(){


    try{


        localStream =
        await navigator.mediaDevices.getUserMedia({

            video:true,

            audio:true

        });



        addVideo(
            socket.id,
            localStream,
            true
        );



        socket.emit(
            "join_room",
            {
                room:room
            }
        );



        console.log(
            "Salle rejointe"
        );



    }

    catch(error){

        console.log(
            "Erreur caméra :",
            error
        );

    }


}



// ==========================
// CREER VIDEO
// ==========================

function addVideo(id,stream,muted=false){


    let video =
    document.getElementById(
        "video_"+id
    );


    if(video)
        return;



    video =
    document.createElement(
        "video"
    );


    video.id =
    "video_"+id;


    video.autoplay = true;

    video.playsInline = true;

    video.muted = muted;


    video.width = 300;


    video.srcObject = stream;



    videos.appendChild(
        video
    );

}



// ==========================
// CREER PEER
// ==========================

function createPeer(userId){



    const peer =
    new RTCPeerConnection({

        iceServers:[

            {
                urls:
                "stun:stun.l.google.com:19302"
            }

        ]

    });



    peers[userId] = peer;



    if(localStream){


        localStream
        .getTracks()
        .forEach(track=>{


            peer.addTrack(
                track,
                localStream
            );


        });


    }



    peer.ontrack =
    event =>{


        addVideo(

            userId,

            event.streams[0],

            false

        );


    };




    peer.onicecandidate =
    event =>{


        if(event.candidate){


            socket.emit(

                "ice_candidate",

                {

                    target:userId,

                    candidate:
                    event.candidate

                }

            );


        }


    };



    return peer;

}




// ==========================
// NOUVEAUX UTILISATEURS
// ==========================


socket.on(
"all_users",
async(users)=>{


    console.log(
        "Utilisateurs présents",
        users
    );



    for(let user of users){


        await createOffer(
            user
        );


    }



});




// ==========================
// NOUVEAU ARRIVANT
// ==========================


socket.on(
"user_joined",
async(data)=>{


    console.log(
        "Nouvel utilisateur",
        data.id
    );


});





// ==========================
// CREER OFFER
// ==========================


async function createOffer(userId){


    const peer =
    createPeer(
        userId
    );



    const offer =
    await peer.createOffer();



    await peer.setLocalDescription(
        offer
    );



    socket.emit(

        "offer",

        {

            target:userId,

            offer:offer

        }

    );


}



// ==========================
// RECEVOIR OFFER
// ==========================


socket.on(
"offer",
async(data)=>{


    const userId =
    data.from;



    const peer =
    createPeer(
        userId
    );



    await peer.setRemoteDescription(

        new RTCSessionDescription(
            data.offer
        )

    );



    const answer =
    await peer.createAnswer();



    await peer.setLocalDescription(
        answer
    );



    socket.emit(

        "answer",

        {

            target:userId,

            answer:answer

        }

    );



});




// ==========================
// RECEVOIR ANSWER
// ==========================


socket.on(
"answer",
async(data)=>{


    const peer =
    peers[data.from];



    if(peer){


        await peer.setRemoteDescription(

            new RTCSessionDescription(
                data.answer
            )

        );


    }


});




// ==========================
// ICE
// ==========================


socket.on(
"ice_candidate",
async(data)=>{


    const peer =
    peers[data.from];



    if(peer){


        try{


            await peer.addIceCandidate(

                new RTCIceCandidate(
                    data.candidate
                )

            );


        }

        catch(error){

            console.log(error);

        }


    }


});




// ==========================
// UTILISATEUR PARTI
// ==========================


socket.on(
"user_left",
(data)=>{


    const id =
    data.id;



    if(peers[id]){


        peers[id].close();

        delete peers[id];


    }



    const video =
    document.getElementById(
        "video_"+id
    );



    if(video){

        video.remove();

    }


});
