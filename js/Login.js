
window.onload = function(){
    var PlayerLogin = document.getElementById("PlayerLogin");
    var PlayerName = document.getElementById("PlayerName");

    PlayerLogin.onclick = function(){
        if(PlayerName.value == ""){
            alert("Please Input PlayerName");
            return;
        }

        $.cookie("uuuname", PlayerName.value);

        console.log('username: ', PlayerName.value);
        window.location.href = "home.html";
    };
};

