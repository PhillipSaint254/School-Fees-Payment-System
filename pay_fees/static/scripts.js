function passwordViewRegister() {
    var password1 = document.getElementById("exampleInputPassword1");
    var password2 = document.getElementById("exampleInputPassword2");
    var checkbox = document.getElementById("exampleCheck1");

    if (checkbox.checked) {
        password1.type = "text";
        password2.type = "text";
    } else {
        password1.type = "password";
        password2.type = "password";
    }
}

// Function to fetch schools from the server
var facultyInput = document.getElementById("fucalty_input");
var courseInput = document.getElementById("course_input");
var password1Input = document.getElementById("exampleInputPassword1");
var password2Input = document.getElementById("exampleInputPassword2");
var selectedSchoolPK = -1;
var selectdFacultyPK = -1;

document.getElementById("student-selection").addEventListener("click", function() {
    var detailsDiv = document.getElementById("select-student-switch");
    var arrowIcon = document.querySelector("#student-selection .arrow i");

    if (detailsDiv.classList.contains("closed")) {
        detailsDiv.classList.toggle("opened");
        detailsDiv.classList.toggle("closed");

        arrowIcon.classList.remove("fa-angle-down");
        arrowIcon.classList.add("fa-angle-up");

        password1Input.disabled = true;
        password2Input.disabled = true;
    } else {
        detailsDiv.classList.toggle("opened");
        detailsDiv.classList.toggle("closed");

        arrowIcon.classList.remove("fa-angle-up");
        arrowIcon.classList.add("fa-angle-down");

        password1Input.disabled = false;
        password2Input.disabled = false;
    }

});

function fetchSchools() {
    return fetch('/get_all_schools/')
        .then(response => response.json())
        .then(data => {
            return data.schools; // Return the list of schools
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to filter schools based on user input
function filterSchools(input) {
    var schoolOptions = document.getElementById("school-options");
    schoolOptions.innerHTML = ""; // Clear previous options

    var schools = JSON.parse(document.getElementById("school_input").getAttribute('data-schools'));

    if (input.trim() === "") {
        schoolOptions.classList.add("select-hide");
        return;
    }

    var matchingSchools = schools.filter(function(school) {
        return school.toLowerCase().includes(input.toLowerCase());
    });

    if (matchingSchools.length > 0) {
        schoolOptions.classList.remove("select-hide");
        matchingSchools.forEach(function(school) {
            var option = document.createElement("div");
            option.textContent = school;
            option.addEventListener("click", function() {
                selectSchool(this.textContent);
                facultyInput.disabled = false;
            });
            schoolOptions.appendChild(option);
        });
    } else {
        schoolOptions.classList.add("select-hide");
    }
}

// Function to handle the selection of a school
function selectSchool(school) {
    var schoolInput = document.getElementById("school_input");
    schoolInput.value = school;
    selectedSchoolPK = school.split(":")[0];
    document.getElementById("school-options").classList.add("select-hide");
}

// Event listener to close the dropdown when clicked outside
document.addEventListener("click", function(e) {
    if (!e.target.matches('#school_input')) {
        document.getElementById("school-options").classList.add("select-hide");
        fetchFaculties()
            .then(faculties => {
                // Once schools are fetched, store them and perform other actions
                var facultyInput = document.getElementById("fucalty_input");
                facultyInput.setAttribute('data-faculty', JSON.stringify(faculties));
            });
    }
});

// Function to fetch faculties from the server based on selected school
function fetchFaculties() {
    return fetch('/get_faculties/?school=' + selectedSchoolPK)
        .then(response => response.json())
        .then(data => {
            return data.faculties; // Return the list of faculties
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to filter schools based on user input
function filterFaculties(input) {
    var facultyOptions = document.getElementById("faculty-options");
    facultyOptions.innerHTML = ""; // Clear previous options

    var faculties = JSON.parse(document.getElementById("fucalty_input").getAttribute('data-faculty'));

    if (input.trim() === "") {
        facultyOptions.classList.add("select-hide");
        return;
    }

    var matchingFaculties = faculties.filter(function(faculty) {
        return faculty.toLowerCase().includes(input.toLowerCase());
    });

    if (matchingFaculties.length > 0) {
        facultyOptions.classList.remove("select-hide");
        matchingFaculties.forEach(function(faculty) {
            var option = document.createElement("div");
            option.textContent = faculty;
            option.addEventListener("click", function() {
                selectFaculty(this.textContent);
                fetchCourses()
                    .then(courses => {
                        // Once schools are fetched, store them and perform other actions
                        var courseInput = document.getElementById("course_input");
                        courseInput.setAttribute('data-course', JSON.stringify(courses));
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            });
            facultyOptions.appendChild(option);
        });
    } else {
        facultyOptions.classList.add("select-hide");
    }
}

// Function to enable course input when a faculty is selected
function selectFaculty(faculty) {
    var facultyInput = document.getElementById("fucalty_input");
    facultyInput.value = faculty;
    selectedFacultyPK = faculty.split(":")[0];
    document.getElementById("faculty-options").classList.add("select-hide");
    courseInput.disabled = false;
    courseInput.value = "";
}

// Function to fetch courses from the server based on selected school
function fetchCourses() {
    return fetch('/get_courses/?school=' + selectedSchoolPK + '&faculty=' + selectedFacultyPK)
        .then(response => response.json())
        .then(data => {
            console.log("handling fetch course");
            console.log(data);
            return data.courses; // Return the list of faculties
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function filterCourses(input) {
    var courseOptions = document.getElementById("course-options");
    courseOptions.innerHTML = ""; // Clear previous options

    var courses = JSON.parse(document.getElementById("course_input").getAttribute('data-course'));

    if (input.trim() === "") {
        courseOptions.classList.add("select-hide");
        return;
    }

    var matchingCourses = courses.filter(function(course) {
        return course.toLowerCase().includes(input.toLowerCase());
    });

    if (matchingCourses.length > 0) {
        courseOptions.classList.remove("select-hide");
        matchingCourses.forEach(function(course) {
            var option = document.createElement("div");
            option.textContent = course;
            option.addEventListener("click", function() {
                selectCourse(this.textContent);
            });
            courseOptions.appendChild(option);
        });
    } else {
        courseOptions.classList.add("select-hide");
    }
}

// Function to enable course input when a course is selected
function selectCourse(course) {
    var courseInput = document.getElementById("course_input");
    courseInput.value = course;
    document.getElementById("course-options").classList.add("select-hide");
    password1Input.disabled = false;
    password2Input.disabled = false;
}