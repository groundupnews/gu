"use strict;"


function makeSlug(text) {
    var min=100000000000000000000000000000000000;
    var max=999999999999999999999999999999999999;
    // Get the current date and time as a numeric only 14 digit string
    var currentDate = new Date();
    var date = currentDate.toISOString().slice(0, 19).replace(/[-T:]/g, "");
    //pick a random 36 digit number
    let slug=Math.floor(Math.random() * (max - min + 1) + min).toString();
    //add them to together
    slug=slug+date;
    return slug;
}
