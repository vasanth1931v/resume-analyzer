document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("analyzeForm");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let formData = new FormData(form);

        fetch("/analyze", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {

            // SHOW MATCH PERCENTAGE
            document.getElementById("matchPercentage").innerText =
                "Match Percentage: " + data.match_percentage + "%";

            let yourSkillsList = document.getElementById("yourSkills");
            let missingSkillsList = document.getElementById("missingSkills");
            let jobRolesList = document.getElementById("jobRoles");

            yourSkillsList.innerHTML = "";
            missingSkillsList.innerHTML = "";
            jobRolesList.innerHTML = "";

            data.resume_skills.forEach(skill => {
                let li = document.createElement("li");
                li.textContent = skill;
                yourSkillsList.appendChild(li);
            });

            data.missing_skills.forEach(skill => {
                let li = document.createElement("li");
                li.textContent = skill;
                missingSkillsList.appendChild(li);
            });

            data.suggested_roles.forEach(role => {
                let li = document.createElement("li");
                li.textContent = role;
                jobRolesList.appendChild(li);
            });

        })
        .catch(error => {
            console.error("Error:", error);
        });

    });

});
