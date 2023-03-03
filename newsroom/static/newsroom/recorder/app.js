URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

function startRecording() {
	

    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;
	pauseButton.disabled = false


	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/
		audioContext = new AudioContext();

		/*  assign to gumStream for later use  */
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);

		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/

		rec = new Recorder(input,{numChannels:1});
        
		//start the recording process
		rec.record();
        //Show recording message and clear existing recordings
        rstatus.innerHTML="Recording in progress...";
        if(recordingsList.firstElementChild){
        recordingsList.removeChild(recordingsList.firstElementChild);
        }

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;
    	pauseButton.disabled = true;
	});
}

function pauseRecording(){
	
	if (rec.recording){
		//pause
		rec.stop();
		pauseButton.innerHTML="Resume";
	}else{
		//resume
		rec.record();
		pauseButton.innerHTML="Pause";

	}
}

function stopRecording() {
	
	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = false;
	pauseButton.disabled = true;

	//reset button just in case the recording is stopped while paused
	pauseButton.innerHTML="Pause";
	
	//tell the recorder to stop the recording
	rec.stop();
    rstatus.innerHTML="Recording stopped. Upload in progress";

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(createDownloadLink);

    
    
}

function createDownloadLink(blob) {
	
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
    var li2= document.createElement('li');

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;
    
	//add the new audio element to li
	li.appendChild(au);
    
	//Date needs to be stripped of non-numeric characters and only the date and time are used for the file name
    var cdate = new Date();
    var fdate=cdate.toISOString().replaceAll("-","");
    fdate=fdate.replaceAll("t","");
    fdate=fdate.replaceAll(":","");
    fdate=fdate.substring(0,8)+fdate.substring(9,15);

    //Create filename. 
    var fname=pk.innerHTML+"_"+fdate+".wav";
    //Create form to pass through filebrowser upload method
    var form_data = new FormData();
	//Convert blob audio to file format so it can be processed and uploaded as wav audio	
    var wavfile=new File([blob], fname)			
	form_data.append("file", wavfile);
	//Attach CSRF token for security purposes  			
	csrf_token = $('input[name="csrfmiddlewaretoken"]').val();		
	form_data.append("csrfmiddlewaretoken", csrf_token);

	//ajax call submits the form with csrf data and file to filebrowser upload method.		
   	$.ajax({
        url: '../../admin/filebrowser/upload_file/',
        type: 'POST',
        data: form_data,

        success: function (response) {
            if (response.success) {
               rstatus.innerHTML="Recording stopped. Upload Success"
            }else if(response.errors) {
               rstatus.innerHTML="Recording stopped. Upload Failed"
            }
        },
        cache: false,
        contentType: false,
        processData: false
    });

    
    id_audio_summary.value="uploads/"+fname;
    var link = document.createElement('a');
    //save to disk link
	link.href = url;
	link.download = "uploads/"+fname; //download forces the browser to donwload the file using the  filename
	link.innerHTML = "uploads/"+fname;
    li2.appendChild(link);
    //In order to maintain only a single recording within the list we must replace existing data with the new recording. 
    //replaceChild() requires an existing node hence we create a node from the list and if it doesn't exist we can just append the new data directly
    var oldnode=recordingsList.childNodes[0];
    if(oldnode){
        recordingsList.replaceChild(li, oldnode);
    }else{
        recordingsList.appendChild(li)
    }
    oldnode=recordingsList.childNodes[1];
    if(oldnode){
        recordingsList.replaceChild(li2, oldnode);
    }else{
        recordingsList.appendChild(li2)
    }
    showSave();
    
}
