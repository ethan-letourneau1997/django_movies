//* show / hide search
const searchIcon = document.querySelector(".fa-search");
const searchContainer = document.querySelector(".search-container");

searchIcon.addEventListener("click", function () {
  searchContainer.classList.toggle("active");
  if (searchContainer.classList.contains("active")) {
    searchIcon.classList.remove("fa-search");
    searchIcon.classList.add("fa-times");
  } else {
    searchIcon.classList.add("fa-search");
    searchIcon.classList.remove("fa-times");
  }
});

document.addEventListener("click", function (event) {
  if (!searchContainer.contains(event.target) && event.target !== searchIcon) {
    searchContainer.classList.remove("active");
    searchIcon.classList.add("fa-search");
    searchIcon.classList.remove("fa-times");
  }
});

//* autocomplete logic

$(document).ready(function () {
  // listen for input changes on the search input field
  $("#search-input").on("input", function () {
    // get the current value of the search input field
    var query = $(this).val();
    if (query.length > 0) {
      // make an AJAX request to the autocomplete URL with the current query as a parameter
      $.ajax({
        url: "/autocomplete/",
        data: {
          query: query,
        },
        success: function (response) {
          // handle the JSON response from the autocomplete view
          var suggestions = response.suggestions;
          $("#autocomplete-list").empty();
          // display the autocomplete suggestions in a list
          suggestions.slice(0, 10).forEach(function (movie) {
            var li = $("<li>").addClass(
              "list-group-item list-group-item-dark mx-2"
            );
            if (movie.id && movie.id !== "") {
              var link;
              var date;
              if (movie.media_type === "movie") {
                date = $("<span>")
                  .addClass("")
                  .text(" (" + movie.release_date.slice(0, 4) + ")");
                link = $("<a>")
                  .attr("href", "/movies/" + movie.id + "/")
                  .text(movie.title)
                  .append(date);
                var icon = $("<i>").addClass("fa-sharp fa-solid fa-video mx-1");
                var type = $("<span>").addClass("fw-600").text("in movies");
              } else if (movie.media_type === "tv") {
                date = $("<span>")
                  .addClass("")
                  .text(" (" + movie.first_air_date.slice(0, 4) + ")");
                link = $("<a>")
                  .attr("href", "/tv/" + movie.id + "/")
                  .text(movie.title)
                  .append(date);
                var icon = $("<i>").addClass("fa-solid fa-tv mx-1");
                var type = $("<span>").addClass("fw-600").text("in shows");
              } else if (movie.media_type === "person") {
                link = $("<a>")
                  .attr("href", "/people/" + movie.id + "/")
                  .text(movie.name);
                var icon = $("<i>").addClass("fa-solid fa-person mx-1");
                var type = $("<span>").addClass("fw-600").text("in people");
                date = "";
              }
              var anchor = $("<a>")
                .attr("href", link.attr("href"))
                .append(icon)
                .append(" ")
                .append(link)
                .append(" ")
                .append(type);
              li.append(anchor);
            } else {
              li.text(movie.title);
            }
            $("#autocomplete-list").append(li);
          });
        },
      });
    } else {
      // clear the autocomplete list if the search input field is empty
      $("#autocomplete-list").empty();
    }
  });
});
