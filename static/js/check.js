var totalImageFileLength, imageFileCount;

//Null validation of file input
function nullImageValidation() {
    var file = document.getElementById("imageFile").files;
    var length = file.length;

    if (length <= 0) {

        return false;
    }
    else {
        return true;
    }
}

//Validate each file type before uploading
function validateImageFileFormat() {
    var files = document.getElementById("imageFile").files;
    var val = true;
    for (let i = 0; i < files.length; i++) {
        var fileInput = files[i];
        var fileType = fileInput.name;
        var allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif|\.bmp)$/i;
        if (!allowedExtensions.exec(fileType)) {
            val = false;
            break;
        }
    }
    return val;
}

// function onImageFileSelect(e) {
//     var files = e.target.files;
//     var output = [];
//     imageFileCount = files.length;
//     totalImageFileLength = 0;
//     for (var i = 0; i < imageFileCount; i++) {
//         var file = files[i];
//         output.push(file.name, ' (', file.size, ' bytes, ',
//             file.lastModifiedDate.toLocaleDateString(), ')');
//         output.push('<br/>');
//
//         console.log(file.name);
//         debug('add ' + file.size);
//         totalImageFileLength += file.size;
//     }
//     bootbox.alert(file.path.toString(), file.name.toString());
//     document.getElementById('selectedImages').innerHTML = output.join('');
// }

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        // console.log("reader", reader);
        // console.log("input", input);

        reader.onload = function (e) {
            $('#selectedImageSrc')
                .attr('src', e.target.result)
                .width(350)
                .height(250);
            // onImageFileSelect(e);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

function onSendComplete() {
    alert("done sending");
}

function getInfo(e) {
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    var file = document.getElementById('imageFile').files[0].name;
    fd.append("multipartFile", file);
    console.log("filename", file);
    // xhr.upload.addEventListener("progress", onUploadProgress, false);
    xhr.addEventListener("load", onSendComplete, false);
    xhr.addEventListener("error", onUploadFailed, false);
    xhr.open("GET", "/check/" + file);
    xhr.send(file);

}

function showTable() {
    alert('went in');
    document.getElementById('table').style.visibility = "visible";
}

function hideTable() {
    alert('hidden');
    document.getElementById('table').style.visibility = "hidden";
}

// Event listeners for button clicks
// window.onload = function () {
//     console.log("loaded script");
//     // document.getElementById('imageFile').addEventListener('change', onImageFileSelect, false);
//     // document.getElementById('imageFile').addEventListener('change', readURL, false);
//     document.getElementById('load').addEventListener('click', getInfo, false);
//     // document.getElementById('reset').addEventListener('click', resetAllElements, false);
// };
// console.log("asddasdasdasdasdas");
// document.getElementById('load_img').addEventListener('click', getInfo, false);
// document.getElementById('reset_btn').addEventListener('click', showTable, false);
