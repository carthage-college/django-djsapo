// autoComplete.js on type event emitter
document.querySelector("#id_course").addEventListener("autoComplete", function(event) {
  console.log(event.detail);
});
// The autoComplete.js Engine instance creator
const coursesAutoComplete = new autoComplete({
    data: {
        src: async () => {
            // Loading placeholder text
            document
                .querySelector("#id_course")
                .setAttribute("placeholder", "Loading...");
            // Fetch External Data Source
            const source = await fetch(
                "https://www.carthage.edu/academics/schedule/R/RA/2019/json/"
            );
            const data = await source.json();
            // Post loading placeholder text
            document
                .querySelector("#id_course")
                .setAttribute("placeholder", "Search Courses");
            // Returns Fetched data
            return data;
        },
        key: ["title","crs_sec"],
        cache: true
    },
    placeHolder: "Search Courses",
    selector: "#id_course",
    threshold: 0,
    debounce: 0,
    searchEngine: "strict",
    //searchEngine: "loose",
    highlight: true,
    maxResults: 20,
    resultsList: {
        render: true,
        container: source => {
          source.setAttribute("id", "courses_results_list");
        },
        destination: document.querySelector("#id_course"),
        position: "afterend",
        element: "ul"
    },
    resultItem: {
        content: (data, source) => {
          console.log(source);
          source.innerHTML = data.value.title + ": " + data.value.crs_no + " " + data.value.sec_no;
        },
        element: "li"
    },
    noResults: () => {
        const result = document.createElement("li");
        result.setAttribute("class", "no_result");
        result.setAttribute("tabindex", "1");
        result.innerHTML = "No courses found";
        document.querySelector("#courses_results_list").appendChild(result);
    },
    onSelection: feedback => {
        const selection = feedback.selection.value.crs_no + " " + feedback.selection.value.sec_no;
        document.querySelector("#id_course").value = selection;
    }
});
// Toggle event for search input
// showing & hidding results list onfocus / blur
["focus", "blur", "mousedown", "keydown"].forEach(function(eventType) {
  const input = document.querySelector("#id_course");
  const resultsList = document.querySelector("#courses_results_list");

  // Hide Results list when not used
  document.addEventListener(eventType, function(event) {
    const current = event.target;
    if (
      current === input ||
      current === resultsList ||
      input.contains(current) ||
      resultsList.contains(current)
    ) {
      resultsList.style.display = "block";
    } else {
      resultsList.style.display = "none";
    }
  });
});
// Toggle Input Classes on results list focus to keep style
["focusin", "focusout", "keydown"].forEach(function(eventType) {
  document.querySelector("#courses_results_list").addEventListener(eventType, function(event) {
    if (eventType === "focusin") {
      if (event.target && event.target.nodeName === "LI") {
        document.querySelector("#id_course").classList.remove("out");
        document.querySelector("#id_course").classList.add("in");
      }
    } else if (eventType === "focusout" || event.keyCode === 13) {
      document.querySelector("#id_course").classList.remove("in");
      document.querySelector("#id_course").classList.add("out");
    }
  });
});
