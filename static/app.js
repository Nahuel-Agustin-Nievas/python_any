var buttons = document.querySelectorAll(".delete-final");

for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function (event) {
        var post_id = this.getAttribute("data-post-id");

        if (confirm("¿Está seguro de que quiere eliminar este post?")) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/delete_final", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                    window.location.href = "/all_posts";
                }
            };
            xhr.send("post_id=" + post_id);
        }

        else {
            event.preventDefault();
        }
    });
}


if (document.getElementById("add-file-button")) {
    document.getElementById("add-file-button").addEventListener("click", function () {
        var file_input = document.createElement("input");
        file_input.setAttribute("type", "file");
        file_input.setAttribute("name", "ourfile[]");
        file_input.setAttribute("multiple", false);
        file_input.setAttribute("accept", ".pdf, .txt, .doc, .jpg, .jpeg, .png");
        var file_input_container = document.createElement("div");
        var remove_button = document.createElement("button");
        remove_button.id = "remove-button";
        remove_button.innerHTML = "Eliminar";
        remove_button.addEventListener("click", function(){
            file_input_container.remove();
        });
        file_input_container.appendChild(file_input);
        file_input_container.appendChild(remove_button);
        document.getElementById("file-inputs").appendChild(file_input_container);
    })
};
    





document.querySelector("form").addEventListener("submit", function(event) {
    var fileInputs = document.querySelectorAll("input[type='file']");
    for (var i = 0; i < fileInputs.length; i++) {
        if (!fileInputs[i].files[0]) {
            fileInputs[i].parentNode.remove();
        }
    }
});



document.getElementById("form_id").addEventListener("submit", function(event) {
    var fileInputs = document.querySelectorAll("input[type=file]");
    for (var i = 0; i < fileInputs.length; i++) {
        if (fileInputs[i].files.length === 0) {
            fileInputs[i].parentNode.removeChild(fileInputs[i]);
        }
    }
});





// document.querySelector('.dropdown-toggle').addEventListener('click', function(e) {
//     e.preventDefault();
// });


document.getElementById("form_id").addEventListener("submit", function(event) {
    var titulo = document.getElementsByName("titulo")[0].value;
    if (titulo === "") {
      event.preventDefault();
      document.getElementById("error-message").innerHTML = "Por favor, ingrese un título.";
    }
  });



