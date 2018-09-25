var totalFileLength, totalFileUploaded, fileCount, filesUploaded;

// To log everything on console
function debug(s) {
    var debug = document.getElementById('debug');
    if (debug) {
        debug.innerHTML = debug.innerHTML + '<br/>' + s;
    }
}

// Will be called when upload is completed
function onUploadComplete(e) {
    totalFileUploaded += document.getElementById('files').files[filesUploaded].size;
    filesUploaded++;
    debug('complete ' + filesUploaded + " of " + fileCount);
    debug('totalFileUploaded: ' + totalFileUploaded);
    if (filesUploaded < fileCount) {
        uploadNext();
    } else {
        var bar = document.getElementById('bar');
        bar.style.width = '100%';
        bar.innerHTML = '100 % complete';
        bootbox.alert('Finished uploading details to Database');
    }
}

// Will be called when user select the files in file control
function onFileSelect(e) {
    var files = e.target.files;
    var output = [];
    fileCount = files.length;
    totalFileLength = 0;
    for (var i = 0; i < fileCount; i++) {
        var file = files[i];
        output.push(file.name, ' (', file.size, ' bytes, ',
            file.lastModifiedDate.toLocaleDateString(), ')');
        output.push('<br/>');
        debug('add ' + file.size);
        totalFileLength += file.size;
    }
    document.getElementById('selectedFiles').innerHTML = output.join('');
}

// This will continuously update the progress bar based on the percentage of image uploaded
function onUploadProgress(e) {
    if (e.lengthComputable) {
        var percentComplete = parseInt((e.loaded + totalFileUploaded) * 100 / totalFileLength);

        if (percentComplete > 100)
            percentComplete = 100;
        showProgressBar();
        var bar = document.getElementById('bar');

        bar.style.width = percentComplete + '%';
        bar.innerHTML = percentComplete + ' % complete';
    } else {
        debug('unable to compute');
    }
}

// Any other errors in uploading files will be handled here.
function onUploadFailed(e) {
    bootbox.alert("Error uploading file");
}

// Pick the next file in queue and upload it to remote server
function uploadNext() {
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    var file = document.getElementById('files').files[filesUploaded];
    var routeName = document.getElementById('routeName').value;
    console.log("routename", routeName);
    // console.log("file", file);
    fd.append("multipartFile", file);
    fd.append("routeName", routeName);
    console.log("fd", fd.entries());
    xhr.upload.addEventListener("progress", onUploadProgress, false);
    xhr.addEventListener("load", onUploadComplete, false);
    xhr.addEventListener("error", onUploadFailed, false);

    var hiddenPedestrian = document.getElementById("hiddenPedestrian");
    console.log("hidden pedestrian,", hiddenPedestrian);
    var postApi = '';
    if (document.contains(hiddenPedestrian)) {
        postApi = "/split-crossing";
    } else {
        postApi = "/video-split";
    }
    xhr.open("POST", postApi);
    xhr.send(fd);
}

function nullValidation() {
    var file = document.getElementById("files").files;
    var length = file.length;

    if (length <= 0) {

        return false;
    }
    else {
        return true;
    }
}

//Validate each file type before uploading
function validateFileFormat() {
    var files = document.getElementById("files").files;
    var val = true;
    for (let i = 0; i < files.length; i++) {
        var fileInput = files[i];
        var fileType = fileInput.name;
        var allowedExtensions = /(\.mp4|\.mov)$/i;
        if (!allowedExtensions.exec(fileType)) {
            val = false;
            break;
        }
    }
    return val;
}

// Let's begin the upload process
function startUpload() {
    if (!nullValidation()) {
        bootbox.alert("Please select a video to upload!");
    }
    else {
        if (!validateFileFormat()) {
            bootbox.alert("Please select only video files!");
        } else {
            totalFileUploaded = filesUploaded = 0;
            uploadNext();
        }
    }
}

function resetAll() {
    document.getElementById("imageUpload").reset();
    document.getElementById("selectedFiles").value = " ";
    var bar = document.getElementById('bar');
    bar.style.width = 0;
    bar.innerHTML = " ";

}

//------------------------------------------------------------------------------------------------------- //
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
        };

        reader.readAsDataURL(input.files[0]);
    }
}

function onSendComplete() {
    console.log("done sending");
}

function getInfo(e) {
    let xhr = new XMLHttpRequest();
    let fd = new FormData();
    let file = document.getElementById('imageFile').files[0].name;
    let my_url = "http://localhost:5000/check/" + file;

    fd.append("multipartFile", file);
    // xhr.upload.addEventListener("progress", onUploadProgress, false);
    xhr.addEventListener("load", showTable, false);
    xhr.addEventListener("error", onUploadFailed, false);

    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let resp_text = JSON.parse(this.responseText);
            console.log('resp_text', resp_text);
            document.getElementById('table').rows[0].cells[1].innerHTML = resp_text.lat;
            document.getElementById('table').rows[1].cells[1].innerHTML = resp_text.long;
            document.getElementById('table').rows[2].cells[1].innerHTML = resp_text.sign_name;
            document.getElementById('table').rows[3].cells[1].innerHTML = resp_text.accuracy;
            $('#selectedImageOut').attr('src', resp_text.file_path).width(350).height(250);
        }
    };

    xhr.open("POST", my_url);
    xhr.send(file);

}

function showTable(resp) {
    console.log("done sending", resp);
    if (document.getElementById('table')) {
        document.getElementById('table').style.visibility = "visible";
    }
}


function hideTable() {
    if (document.getElementById('table')) {
        // alert('hidden');
        document.getElementById('table').style.visibility = "hidden";
    }
}

function hideProgressBar() {
    if (document.getElementById('bar')) {
        // alert('hidden');
        document.getElementById('bar').style.visibility = "hidden";
    }
}

function showProgressBar() {
    console.log("done sending");
    if (document.getElementById('bar')) {
        document.getElementById('bar').style.visibility = "visible";
    }
}

//-------------------------------------------------------------------------------------------------------------------------//
// Event listeners for button clicks
window.onload = function () {
    hideTable()
    hideProgressBar()
    if (document.getElementById('files'))
        document.getElementById('files').addEventListener('change', onFileSelect, false);

    if (document.getElementById('splitButton'))
        document.getElementById('splitButton').addEventListener('click', startUpload, false);

    if (document.getElementById('resetButton'))
        document.getElementById('resetButton').addEventListener('click', resetAll, false);
    // document.getElementById('load_img').addEventListener('click', getInfo, false);

    if (document.getElementById('load_img'))
        document.getElementById('load_img').addEventListener('click', getInfo, false);

    // if (document.getElementById('reset_btn'))
    //     document.getElementById('reset_btn').addEventListener('click', showTable, false);
};

