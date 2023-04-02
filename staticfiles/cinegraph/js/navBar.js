// Hide nav on scroll down, show on scroll up

var new_scroll_position = 0;
var last_scroll_position;
var header = document.getElementById("navbar");

window.addEventListener("scroll", function (e) {
  last_scroll_position = window.scrollY;

  // Scrolling down
  if (
    new_scroll_position < last_scroll_position &&
    last_scroll_position > 200
  ) {
    // header.removeClass('slideDown').addClass('slideUp');
    header.classList.remove("slideDown");
    header.classList.add("slideUp");

    // Set search container transition duration to match header
    searchContainer.style.transitionDuration = "0.3s";

    // Scrolling up
  } else if (new_scroll_position > last_scroll_position) {
    // header.removeClass('slideUp').addClass('slideDown');
    header.classList.remove("slideUp");
    header.classList.add("slideDown");

    // Set search container transition duration to match header
    searchContainer.style.transitionDuration = "0.3s";
  }

  new_scroll_position = last_scroll_position;
});

// Move search to top when nav hides on scroll

$(document).ready(function () {
  $(window).scroll(function () {
    if ($("#navbar").hasClass("slideDown")) {
      $(".search-container.active").css({
        transition: "top 0.5s ease",
        top: "65px",
      });
    } else {
      $(".search-container.active").css({
        transition: "top 0.5s ease",
        top: "0",
      });
    }
  });
});
