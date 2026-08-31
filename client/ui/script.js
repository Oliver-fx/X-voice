/// <reference types="toastify-js" />
let timer = null

function registerButton() {
    let name = document.getElementById("name_input").value;
    let button = document.getElementById("r_button");
    button.disabled = true;

    eel.user_input("r", name)();

}

function displayRegistrationResult(status) {
    let button = document.getElementById("r_button");
    let name_input_box= document.getElementById("name_input")
    let container3 = document.getElementById('container-3')
    if (status == "ok") {
        name_input_box.disabled = true
        try {
            Toastify({
                text: "you have successfully registered on server",
                close: "true",
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {

        }
        //alert("you have successfully registered on server");
        container3.innerHTML = `<div id="chatting-box"></div>
                    <form id="chat-form">
                        <input id="gtxt-input" type="text" placeholder="Type a message..." autocomplete="off">
                        <button id="gtxt-send" onclick="handleSubmitEvent()" type="submit">Send</button>
                    </form>`
        
    } else {
        try {
            Toastify({
                text: status,
                close: "true",
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {

        }
        //alert(status);
        button.disabled = false;
    }
}

function callingButton() {
    let name = document.getElementById("name_to_call").value
    let button = document.getElementById("c_button")
    let name_input_box = document.getElementById("name_to_call")

    // disable name input box and button
    button.disabled = true
    name_input_box.disabled = true

    eel.user_input("c", name)

}

function displayConnectionResult(status) {
    let button = document.getElementById("c_button")
    let box = document.getElementById("connection_notification")
    let name_input_box = document.getElementById("name_to_call")

    if (status == "user is not registered to server") {
        try {
            Toastify({
                text: "The user you are connecting to is not registered on server",
                close: "true",
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {

        }
        //alert("The user you are connecting to is not registered on server")
        button.disabled = false
        name_input_box.value = ""
        name_input_box.disabled = false
    } else if (status.includes("calling from")) {
        //TODO tell the html to show up a button for user to answer the call
        let timeLeft = 30
        // disable name input box and button
        button.disabled = true
        name_input_box.disabled = true
        box.style.display = 'block';
        box.innerHTML = `<b id="calling_from_other_title" >${status}</b>
        <button id="answer_button" onclick="answerButton()"> answer </button>
        <button id="cancel_button" onclick="cancelButton()"> cancel </button>
        <b id="recv_countdown">30s</b>
        `
        let countdown = document.getElementById('recv_countdown')
        timer = setInterval(() => {
            timeLeft--;
            countdown.textContent = `${timeLeft}s`
            if (timeLeft == 0) {
                clearInterval(timer);
                box.style.display = 'none'
                eel.user_input("ac", "no_answer")
            }
            
        }, 1000);

    } else if (status.includes("waiting for")) {
        //TODO let html show a count down on the screen, the count down
        // !!!!should be = 30s
        box.style.display = 'block';
        box.innerHTML = `<b id="calling_other_title">Calling...</b>
        <span id="countdown">30s remaining: 30s</span>
        `
        let countdown = document.getElementById('countdown')
        let timeLeft = 30

        timer = setInterval(() => {
            timeLeft--;
            countdown.textContent = `30s remaining: ${timeLeft}s`

            if (timeLeft == 0) {
                clearInterval(timer)
                box.style.display = 'none'
            }

        }, 1000);
    } else if (status == "you can't call yourself") {
        try {
            Toastify({
                text: "you can't call yourself",
                close: "true",
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {
            
        }
        //alert("you can't call yourself")
        button.disabled = false
        name_input_box.value = ""
        name_input_box.disabled = false
    }
}

function answerButton() {
    let answer_button = document.getElementById("answer_button")
    let cancel_button = document.getElementById("cancel_button")
    let box = document.getElementById("connection_notification")

    clearInterval(timer)
    answer_button.disabled = true
    cancel_button.disabled = true

    box.style.display = "none"
    eel.user_input("ac", "call_accept")
}

function cancelButton() {
    let answer_button = document.getElementById("answer_button")
    let cancel_button = document.getElementById("cancel_button")
    let box = document.getElementById("connection_notification")

    clearInterval(timer)
    answer_button.disabled = true
    cancel_button.disabled = true

    box.style.display = "none"
    // CHANGE THIS IF NEEDED
    eel.user_input("ac", "call_accept")
}

function endCallButton() {
    let end_button = document.getElementById("end_call_button")
    end_button.disabled = true

    eel.user_input("ac", "disconnect")
}

// flag indicates the u2 which sends the call accpeted signal to server and uses server socket 2
if (typeof window.callFlag === 'undefined') {
    window.callFlag = 0; 
}
window.isCallLocked = false

function displayCallingStatus(status) {
    let div = document.getElementById("connection_status")
    let button = document.getElementById("c_button")
    let name_input_box = document.getElementById("name_to_call")
    let box = document.getElementById("connection_notification")

    if (window.isCallLocked && status != "disconnected") {
        return;
    }

    div.style.display = 'block'
    
    if (status == "call not answered") {
        button.disabled = false
        name_input_box.disabled = false
        name_input_box.value = ""
        div.innerHTML = `<b id="call_no_answer">${status}</b>`
    } else if (status == `you missed a call`) {
        button.disabled = false
        name_input_box.disabled = false
        name_input_box.value = ""
        // reset the button
        let answer_button = document.getElementById("answer_button")
        let cancel_button = document.getElementById("cancel_button")
        answer_button.disabled = false
        cancel_button.disabled = false 
        div.innerHTML = `<b id="you_miss_call">${status}</b>`
        
    } else if (status == "call accepted") {
        box.style.display = "none"
        name_input_box.value = "⌐■_■ ysb is sharing his secrets"
        button.disabled = true
        name_input_box.disabled = true
        window.callFlag = 1

        div.innerHTML = `<b id="call_accepted">${status}</b>`
    } else if (status == "connecting") {
        name_input_box.value = "⌐■_■ ysb is sharing his secrets"
        button.disabled = true
        name_input_box.disabled = true
        div.innerHTML = `<b id="call_accepted">${status}</b>`
    } else if (status == "key") {
        div.innerHTML = `<b id="call_accepted">recieving master key...</b>`
        // future impprovements: send confirmatin for key recieving 
    } else if (status == "addr") {
        div.innerHTML = `<b id="call_accepted">recieving udp server addr...</b>`
    } else if (status == "spawn") {
        div.innerHTML = `<b id="call_accepted">final establishment</b>`
    } else if (status == "connected") {
        window.isCallLocked = true
        div.innerHTML = `<b id="call_accepted">connected</b>
        <button id="end_call_button" onclick="endCallButton()"> End </button>`
    } else if (status == "disconnected") {
        window.isCallLocked = false
        button.disabled = false
        name_input_box.disabled = false
        name_input_box.value = ""
        div.innerHTML = `<b>Call Ended</b>`
        // forgot to recieve call flag here !!!!
        window.callFlag = 0
    }
    
    setTimeout(() => {
        if (status == "call accepted") {
            eel.user_input("ac", "request_to_connect")
        } else if (status == "connecting" && window.callFlag == 1) {
            eel.user_input("ac", "get_key")
        } else if (status == "key" && window.callFlag == 1) {
            eel.user_input("ac", "get_addr")
        } else if (status == "addr" && window.callFlag == 1) {
            eel.user_input("ac", "spawn_udp_program")
        }
        if (window.isCallLocked == false) {
            div.style.display = 'none'
            div.innerHTML = '';
        }

    }, 1000);
}

function handleSubmitEvent() {
    const chatForm = document.getElementById('chat-form')
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault()
        handleGlobalTextSending()
    })
}

function handleGlobalTextSending() {
    const inputElement = document.getElementById("gtxt-input")
    let text = inputElement.value
    if (text == '') {
        return
    }

    if (text.length > 200) {
        Toastify({
            text: "maximum text length 200 characters",
            close: false,
            duration: 3000,
            gravity: "bottom",
            position: "right",
            style: {
                background: "#32533c",
                borderRadius: "8px",
            }
        }).showToast()
        return
    }

    eel.user_input("gtxt", text)

    inputElement.value = ''

}

function displayGlobalText(text, timestamp) {
    let displayWindow = document.getElementById("chatting-box")
    const msgDiv = document.createElement('div')
    const timestampDiv = document.createElement('div')

    msgDiv.classList.add('chat-message')
    msgDiv.textContent = text
    displayWindow.appendChild(msgDiv)

    timestampDiv.classList.add('timestamp-message')
    timestampDiv.textContent = timestamp
    displayWindow.appendChild(timestampDiv)

    // add snap chat feature

    displayWindow.scrollTop = displayWindow.scrollHeight
}


eel.expose(displayCallingStatus)
eel.expose(displayRegistrationResult)
eel.expose(displayConnectionResult)
eel.expose(displayGlobalText)

// starting page js    ///////////////////////////////////////////////////////////////////// !!!!!!!!!!!!!!! /////
window.connectionFlag = 0
async function handleConnect() {
    const ipAddrInput = document.getElementById('ip-input');
    const connectButton = document.getElementById('connect-button');
    
    if (!ipAddrInput.value) {
        try {
            Toastify({
                text: "please enter a valid ip addr",
                close: false,
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {
            console.log("can not laod toastify")
        }
        return
    }

    ipAddrInput.disabled = true
    connectButton.disabled = true

    let status = await eel.starting_page(ipAddrInput.value)()
    
    if (status == true) {
        console.log("success")
        try{
            Toastify({
                text: "Server Connected!",
                close: false,
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
            Toastify({
                text: "Click Xvoice to start!",
                close: false,
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()

        } catch (e) {
            console.log("can not load toastify")
        }

        connectionFlag = 1
    } else {
        ipAddrInput.disabled = false
        connectButton.disabled =false
        ipAddrInput.value = ""
        try {
            Toastify({
                text: "please enter a valid ip addr",
                close: false,
                duration: 3000,
                gravity: "bottom",
                position: "right",
                style: {
                    background: "#32533c",
                    borderRadius: "8px",
                }
            }).showToast()
        } catch (e) {
            console.log("can not load toastify")
        }
    }
}

function XvoiceButton() {
    //const XvoiceButtion = document.getElementById('dynamic-button')
    if (window.connectionFlag == 1) {
        window.location.href = "index.html"
    }
}
