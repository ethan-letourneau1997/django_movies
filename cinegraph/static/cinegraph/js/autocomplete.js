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
              "list-group-item list-group-item-dark "
            );
            if (movie.id && movie.id !== "") {
              var link;
              if (movie.media_type === "movie") {
                link = $("<a>")
                  .attr("href", "/movies/" + movie.id + "/")
                  .text(movie.title);
                var icon = $("<i>").addClass("fa-sharp fa-solid fa-video");
                var span = $("<span>").text("in movies");
              } else if (movie.media_type === "tv") {
                link = $("<a>")
                  .attr("href", "/shows/" + movie.id + "/")
                  .text(movie.title);
                var icon = $("<i>").addClass("fa-solid fa-tv");
                var span = $("<span>").text("in shows");
              } else if (movie.media_type === "person") {
                link = $("<a>")
                  .attr("href", "/people/" + movie.id + "/")
                  .text(movie.name);
                var icon = $("<i>").addClass("fa-solid fa-person");
                var span = $("<span>").text("in person");
              }
              var anchor = $("<a>")
                .attr("href", link.attr("href"))
                .append(icon)
                .append(" ")
                .append(link)
                .append(" ")
                .append(span);
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
