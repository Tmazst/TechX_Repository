



var sections = document.querySelectorAll(".profile-sections");
var currentSectionIndex = 0;
var firstSection = sections[0];
var noSections = sections.length;
var progressCont = document.querySelectorAll(".progress-cont");
var progressCount = document.querySelectorAll(".progress-no");
let indexList = [];



function changeProgressColor(){

    for (var sect=0;sect<noSections;sect++){
        // Create Divs
        var progressCountIncr = document.createElement("div");
        var progressCircle = document.createElement("div");
        var progressLineSep = document.createElement("div");

        if (indexList.includes(sect)) {
            // Skip creating the progress element since it exists
            continue;
        }

        // Do not start from zero
        progressCountIncr.innerText = (sect+1);
        //  console.log("Current Index Outside:" + currentSectionIndex);
        //  console.log("Current Sect: Outside" + sect);
        //  Make current progress count coral in color

        if(currentSectionIndex == sect){
            // Assign Classes to divs
            progressCountIncr.classList.add("progress-no-c");
            progressCircle.classList.add("progress-incr-c");
            progressLineSep.classList.add("progress-line-sep-c");

            // Append to parents div
            progressCircle.appendChild(progressCountIncr);
            progressCont[currentSectionIndex].appendChild(progressLineSep);
            progressCont[currentSectionIndex].appendChild(progressCircle);

        }else{

//            console.log("Current Index Else:" + currentSectionIndex);
//            if (!indexList.includes(currentSectionIndex)){

                //Assign Classes to divs
                progressCircle.classList.add("progress-incr");
                progressLineSep.classList.add("progress-line-sep");
                progressCountIncr.classList.add("progress-no");

                console.log("List Indexes: ",indexList);
                }

                // Append to parents div
                progressCircle.appendChild(progressCountIncr);
                progressCont[currentSectionIndex].appendChild(progressLineSep);
                progressCont[currentSectionIndex].appendChild(progressCircle);

                indexList.push(sect);

        }

    };





if (currentSectionIndex == 0){
    firstSection.style.display = "block";

    changeProgressColor()

    }else{
        firstSection.style.display = "none";
};


function showNextSection() {

    //Prevents Current Page From Reloading
    event.preventDefault();

    sections[currentSectionIndex].style.display = "none"; // Hide current section
    currentSectionIndex++; // Move to the next section

    if (currentSectionIndex < sections.length) {
        sections[currentSectionIndex].style.display = "block"; // Show next section
        changeProgressColor()
        };

    };

//
//function showPreviousSection() {
//
//    //Prevents Page From Reloading
//    event.preventDefault();
//
//    sections[currentSectionIndex].style.display = "none"; // Hide current section
//    currentSectionIndex--; // Move to the next section
//
//    if (currentSectionIndex >= 0) {
//        sections[currentSectionIndex].style.display = "block"; // Show next section
//        //changeProgressColor()
//        };
//
//    };

//function showPreviousSection() {
//
//    history.go(-1)
//
//
//
//    };



//If Other in web type is selected do the following...
document.querySelector("#otherType").addEventListener('change',function(e){

        if (this.selectedIndex == 5){
            var anInput = document.createElement('input');
            var otherLabel = document.createElement('label');
            var parent = this.parentNode;
            //Assign IDs
            anInput.id = 'other-opt-input';
            otherLabel.id = 'other-opt-label';
            // Label description
            otherLabel.innerHTML = '<span> Please Specify: </span> '
            //Add Class
            anInput.classList.add('form-control-other');
            parent.appendChild(otherLabel);
            this.parentNode.appendChild(anInput);

        }else{
            //If these Elements are defined/present, remove them
            if(document.querySelector("#other-opt-input") != "undefined"){
                document.querySelector("#other-opt-input").remove();
                document.querySelector("#other-opt-label").remove();
            }

        }

    }
    );


    //If Other in web type is selected do the following...
document.querySelector("#checkbox-opt").addEventListener('change',function(){

        if (this.checked){
            var anInput = document.createElement('input');
            var otherLabel = document.createElement('label');
            var parent = this.parentNode;
            //Assign IDs
            anInput.id = 'doc-upload-id';
            anInput.type = 'file';
            otherLabel.id = 'doc-upload-label';
            // Label description
            otherLabel.innerHTML = '<br><br><span> Please Upload Document below: </span> <br><br> '
            //Add Class
            //anInput.classList.add('form-control-other');
            parent.appendChild(otherLabel);
            this.parentNode.appendChild(anInput);

        }else{
            //If these Elements are defined/present, remove them
            if(document.querySelector("#doc-upload-id") != "undefined"){
                document.querySelector("#doc-upload-id").remove();
                document.querySelector("#doc-upload-label").remove();
            }

        }

    }
    );

