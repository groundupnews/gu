"use strict";

const FIELDS = [
    "id_court", "id_event_date", "id_case_name", "id_judges",
    "id_document_url", "id_document", "id_notes",
]

function hideFields()
{
    for (let field of FIELDS) {
        document.getElementById(field).parentElement.
            style.display = "none";
    }
    document.getElementById('event-add-submit').
        style.display = "none";
}

function showFields()
{
    for (let field of FIELDS) {
        document.getElementById(field).parentElement.
            style.display = "block";
    }
    document.getElementById('event-add-submit').
        style.display = "block";
}


function init()
{
    document.getElementById("id_case_id").
        addEventListener("blur", function(e) {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch("{% url 'judgment:get_case' %}", {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',},
                mode: 'same-origin',
                body: JSON.stringify({
                    "case_id": e.target.value,
                })
            }).then(response => {
                if (response.status === 200) {
                    return response.json();
                } else {
                    throw 'Error getting case number: ' +  response.status;
                }
            }).then(data => {
                if (data.case_id != '') {
                    document.getElementById("id_case_id").value = data.case_id
                    for (let field of FIELDS) {
                        if (field.substr(3) in data) {
                            document.getElementById(field).value =
                                data[field.substr(3)];
                        }
                    }
                    document.getElementById('id_court').value =
                        data['court_pk'];
                    document.getElementById('id_event_date').value = "";
                }

            }).catch((error) => {
                console.error('Error:', error);
            });
        });
}

init();
