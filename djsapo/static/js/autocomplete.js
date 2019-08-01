// autoComplete.js on type event emitter
//document.querySelector("#autoComplete").addEventListener("autoComplete", function(event) {
  //console.log(event.detail);
//});
// The autoComplete.js Engine instance creator
const autoCompletejs = new autoComplete({
    data: {
        src: async () => {
            // Loading placeholder text
            document
                .querySelector("#autoComplete")
                .setAttribute("placeholder", "Loading...");
            // Fetch External Data Source
            const source = await fetch($studentApi);

            const data = await source.json();
            // Post loading placeholder text
            document
                .querySelector("#autoComplete")
                .setAttribute("placeholder", "Search Students");
            // Returns Fetched data
            return data;
        },
        key: ["lastname","email"],
        cache: true
    },
    sort: (a, b) => {
        if (a.match < b.match) return -1;
        if (a.match > b.match) return 1;
        return 0;
    },
    placeHolder: "Search Students",
    selector: "#autoComplete",
    threshold: 0,
    debounce: 0,
    searchEngine: "strict",
    //searchEngine: "loose",
    highlight: true,
    maxResults: 30,
    resultsList: {
        render: true,
        container: source => {
          source.setAttribute("id", "autoComplete_results_list");
        },
        destination: document.querySelector("#autoComplete"),
        position: "afterend",
        element: "ul"
    },
    resultItem: {
        content: (data, source) => {
          source.innerHTML = data.match + ", " + data.value.firstname + ": " + data.value.email;
        },
        element: "li"
    },
    noResults: () => {
        const result = document.createElement("li");
        result.setAttribute("class", "no_result");
        result.setAttribute("tabindex", "1");
        result.innerHTML = "No students found";
        document.querySelector("#autoComplete_results_list").appendChild(result);
    },
    onSelection: feedback => {
        const selection = feedback.selection.value.lastname + ", " + feedback.selection.value.firstname;
        // Render selected choice to selection div
        document.querySelector(".selection").innerHTML = selection;
        //document.querySelector("#autoComplete").value = feedback.selection.value.id;
        document.querySelector("#autoComplete").value = "";
        document.querySelector("#autoComplete").setAttribute('data-email', feedback.selection.value.email);
        // Change placeholder with the selected value
        //document.querySelector("#autoComplete").setAttribute("placeholder", selection);
    }
});
// Toggle event for search input
// showing & hidding results list onfocus / blur
["focus", "blur", "mousedown", "keydown"].forEach(function(eventType) {
  const input = document.querySelector("#autoComplete");
  const resultsList = document.querySelector("#autoComplete_results_list");

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
  document.querySelector("#autoComplete_results_list").addEventListener(eventType, function(event) {
    if (eventType === "focusin") {
      if (event.target && event.target.nodeName === "LI") {
        document.querySelector("#autoComplete").classList.remove("out");
        document.querySelector("#autoComplete").classList.add("in");
      }
    } else if (eventType === "focusout" || event.keyCode === 13) {
      document.querySelector("#autoComplete").classList.remove("in");
      document.querySelector("#autoComplete").classList.add("out");
    }
  });
});
