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

    function sort_cases(cases, column) {
        cases.sort(function(a, b){return a[column] < b[column]});
        return cases;
    }

    function render_table(entries)
    {
        let tbody = document.querySelector("#case-list tbody");
        tbody.innerHTML = "";
        for (const entry of entries) {
            let tr = document.createElement("tr");
            tbody.append(tr);
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
            a1.href = "{% url 'admin:judgment_event_changelist' %}?q=" + entry.case_id;
            a1.textContent = entry.case_id;
            td.append(a1);
            {% else %}
            td.textContent = entry.case_id;
            {% endif %}
            tr.append(td);
            td = document.createElement("td");
            td.innerHTML = entry.case_name;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.court;
            tr.append(td);
            td = document.createElement("td");
            td.textContent = entry.judges;
            tr.append(td);
            td = document.createElement("td");
            td.innerHTML = entry.status_display;
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
        for (let entry of cases_array) {
            if (criterion == "all") {
                cases.push(entry);
            } else if (criterion == "reserved") {
                if (entry.status == "R") {
                    cases.push(entry);
                }
            } else if (criterion == "reserved_3") {
                if (entry.status == "R" && (entry.three_months ||
                    entry.six_months)) {
                    cases.push(entry);
                }
            } else if (criterion == "reserved_6") {
                if (entry.status == "R" && entry.six_months) {
                    cases.push(entry);
                }
            } else if (criterion == "handed") {
                if (entry.status == "H") {
                    cases.push(entry);
                }
            } else if (criterion == "handed_3") {
                if (entry.status == "H" && (entry.three_months ||
                    entry.six_months)) {
                    cases.push(entry);
                }
            } else if (criterion == "handed_6") {
                if (entry.status == "H" && entry.six_months) {
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
        let desc = cases.length + " case";
        if (cases.length != 1) desc += "s";
        document.getElementById("case-count").textContent = desc;
        $("#case-list").trigger("update");
    }

    document.getElementById("filter-cases").
        addEventListener("change", set_table);
    set_table();


}

init();

