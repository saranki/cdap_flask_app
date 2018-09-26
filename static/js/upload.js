var totalFileLength, totalFileUploaded, fileCount, filesUploaded;

// To log everything on console
function debug(s) {
    let debug = document.getElementById('debug');
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
        let bar = document.getElementById('bar');
        bar.style.width = '100%';
        bar.innerHTML = '100 % complete';
        bootbox.alert('Finished uploading details to Database');
    }
}

// Will be called when user select the files in file control
function onFileSelect(e) {
    let files = e.target.files;
    let output = [];
    fileCount = files.length;
    totalFileLength = 0;
    for (let i = 0; i < fileCount; i++) {
        let file = files[i];
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
        let percentComplete = parseInt((e.loaded + totalFileUploaded) * 100 / totalFileLength);

        if (percentComplete > 100)
            percentComplete = 100;
        showProgressBar();
        let bar = document.getElementById('bar');

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
    let xhr = new XMLHttpRequest();
    let fd = new FormData();
    let file = document.getElementById('files').files[filesUploaded];
    let routeName = document.getElementById('routeName').value;
    fd.append("multipartFile", file);
    fd.append("routeName", routeName);
    xhr.upload.addEventListener("progress", onUploadProgress, false);
    xhr.addEventListener("load", onUploadComplete, false);
    xhr.addEventListener("error", onUploadFailed, false);

    let hiddenPedestrian = document.getElementById("hiddenPedestrian");
    let postApi = '';
    if (document.contains(hiddenPedestrian)) {
        postApi = "/split-crossing";
    } else {
        postApi = "/video-split";
    }

    xhr.open("POST", postApi);
    xhr.send(fd);
}

function nullValidation() {
    let file = document.getElementById("files").files;
    let length = file.length;

    return length > 0;
}

//Validate each file type before uploading
function validateFileFormat() {
    let files = document.getElementById("files").files;
    let val = true;
    for (let i = 0; i < files.length; i++) {
        let fileInput = files[i];
        let fileType = fileInput.name;
        let allowedExtensions = /(\.mp4|\.mov)$/i;
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
    let bar = document.getElementById('bar');
    bar.style.width = 0;
    bar.innerHTML = " ";

}

//------------------------------------------------------------------------------------------------------- //
function readURL(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader();

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
    let my_url = "";
    fd.append("multipartFile", file);
    xhr.addEventListener("load", showTable, false);
    xhr.addEventListener("error", onUploadFailed, false);

    // Append a parameter to the end of the image filename, to differentiate between crossing and signboard
    let hiddenPedestrian = document.getElementById("hiddenPedestrianCheck");
    if (document.contains(hiddenPedestrian)) {
        my_url = "http://localhost:5000/check/" + file + "|CROSSWALK";
    } else {
        my_url = "http://localhost:5000/check/" + file;
    }

    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let resp_text = JSON.parse(this.responseText);
            console.log('resp_text', resp_text);
            document.getElementById('table').rows[0].cells[1].innerHTML = resp_text.lat;
            document.getElementById('table').rows[1].cells[1].innerHTML = resp_text.long;
            document.getElementById('table').rows[2].cells[1].innerHTML = resp_text.sign_name;
            document.getElementById('table').rows[3].cells[1].innerHTML = resp_text.accuracy;
            $('#selectedImageOut').attr('src', resp_text.file_path).width(600).height(338);
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
    hideTable();
    hideProgressBar();
    if (document.getElementById('files'))
        document.getElementById('files').addEventListener('change', onFileSelect, false);

    if (document.getElementById('splitButton'))
        document.getElementById('splitButton').addEventListener('click', startUpload, false);

    if (document.getElementById('resetButton'))
        document.getElementById('resetButton').addEventListener('click', resetAll, false);

    if (document.getElementById('load_img'))
        document.getElementById('load_img').addEventListener('click', getInfo, false);
};

