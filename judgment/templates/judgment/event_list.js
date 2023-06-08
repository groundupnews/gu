"use strict";

function init() {

    let cases_array = [
        {% for obj in object_list %}
        {
            case_id: "{{obj.case_id}}",
                case_name: "{{obj.case_name}}",
                court: "{{obj.court}}",
                judges: "{{obj.judges}}",
                status: "{{obj.status}}",
                status_display: "{{obj.status_display}}",
                date_reserved: "{{obj.date_reserved|date:'Y-m-d'}}",
                date_current: "{{obj.date_current|date:'Y-m-d'}}",
                three_months: {{obj.3m|lower}},
                six_months: {{obj.6m|lower}}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ];
    function render_table(entries)
    {
        let tbody = document.querySelector("#case-list tbody");
        tbody.innerHTML = "";
        for (const entry of entries) {
            let tr = document.createElement("tr");
            tbody.append(tr);
            console.log(entry.three_months, entry.six_months);
            if (entry.status != "R") {
                tr.classList.add("resolved");
            }
            if (entry.three_months) {
                tr.classList.add("late");
            }
            if (entry.six_months) {
                tr.classList.add("very-late");
            }
            let td;
            td = document.createElement("td");
            {% if request.user.is_staff %}
            let a1 = document.createElement("a");
            a1.href = "{% url 'admin:judgment_event_changelist' %}?q={{obj.case_id}}";
            a1.textContent = entry.case_id;
            td.append(a1);
            {% else %}
            td.textContent = entry.case_id;
            {% endif %}
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.case_name;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.court;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.judges;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.status_display;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.date_reserved;
            tr.append(td);
            td = document.createElement("td");
            if (entry.status == "R") {
                td.textContent = "Not yet";
            } else {
                td.textContent = entry.date_current;
            }
            tr.append(td);
        }
    }

    $(function() {
        $("#case-list").tablesorter();
    });
    function filter_cases(criterion) {
        let cases = [];
        console.log(criterion);
        for (let entry of cases_array) {
            console.log(entry, entry.status, entry.three_months,
                entry.six_months);
            if (criterion == "all") {
                cases.push(entry);
            } else if (criterion == "reserved") {
                if (entry.status == "R") {
                    cases.push(entry);
                }
            } else if (criterion == "handed") {
                if (entry.status == "H") {
                    cases.push(entry);
                }
            } else if (criterion == "three") {
                if (entry.three_months) {
                    cases.push(entry);
                }
            } else if (criterion == "six") {
                if (entry.six_months) {
                    cases.push(entry);
                }
            }
        }
        return cases;
    }

    function set_table() {
        const criterion = document.getElementById("filter-cases").value;
        let cases = filter_cases(criterion);
        render_table(cases);
    }

    document.getElementById("filter-cases").
        addEventListener("change", set_table);
    set_table();
}

init();

