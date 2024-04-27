function fetch_passwords() {
    var out = document.getElementById("list-out").innerHTML = ""
    out.innerHTML = ""
    fetch('/passwords', {
        method: 'POST',
        headers: {
            "Content-Type" : "Application/Json"
        }
    })
    .then(response => response.json())
    .then(data => {
        data.passwords.forEach(function(item) {
            console.log(item)
            var site = item[0]
            var username = item[1]
            var email = item[2]
            var password = item[3]

            var limain = document.createElement("li");
            var textmain = document.createTextNode("Site: " + site);
            limain.appendChild(textmain);

            var ulnested = document.createElement("ul");

            var liuser = document.createElement("li");
            var liusertext = document.createTextNode("User: " + username)
            liuser.appendChild(liusertext)
            ulnested.appendChild(liuser)

            var liemail = document.createElement("li");
            var liemailtext = document.createTextNode("Email: " + email)
            liemail.appendChild(liemailtext)
            ulnested.appendChild(liemail)

            var lipass = document.createElement("li");
            var lipasstext = document.createTextNode("Pass: " + password);
            lipass.appendChild(lipasstext)
            ulnested.appendChild(lipass)

            limain.appendChild(ulnested)

            document.getElementById("list-out").appendChild(limain)
        })
    })
}