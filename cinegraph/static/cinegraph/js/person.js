// expand and collapse a person's biography
class readMore {
  constructor() {
    this.content = ".readmore__content";
    this.buttonToggle = ".readmore__toggle";
  }

  bootstrap() {
    this.setNodes();
    this.init();
    this.addEventListeners();
  }

  setNodes() {
    this.nodes = {
      contentToggle: document.querySelector(this.content),
    };

    this.buttonToggle = this.nodes.contentToggle.parentElement.querySelector(
      this.buttonToggle
    );
  }

  init() {
    const { contentToggle } = this.nodes;

    this.stateContent = contentToggle.innerHTML;

    contentToggle.innerHTML = `${this.stateContent.substring(0, 1000)}...`;
  }

  addEventListeners() {
    this.buttonToggle.addEventListener("click", this.onClick.bind(this));
  }

  onClick(event) {
    const targetEvent = event.currentTarget;
    const { contentToggle } = this.nodes;

    if (targetEvent.getAttribute("aria-checked") === "true") {
      targetEvent.setAttribute("aria-checked", "false");
      contentToggle.innerHTML = this.stateContent;
      this.buttonToggle.innerHTML = "Read less";
    } else {
      targetEvent.setAttribute("aria-checked", "true");
      contentToggle.innerHTML = `${this.stateContent.substring(0, 1000)}...`;
      this.buttonToggle.innerHTML = "Read more";
    }
  }
}
const initReadMore = new readMore();
initReadMore.bootstrap();

// select and view a person's credits for each department
const selectElement = document.querySelector("#departmentSelect");
const departmentContents = document.querySelectorAll(".department-content");
const defaultDepartment = selectElement.value;

// Show content for default department on page load
departmentContents.forEach((content) => {
  if (content.id === `department-${defaultDepartment}`) {
    content.style.display = "block";
  } else {
    content.style.display = "none";
  }
});

selectElement.addEventListener("change", (event) => {
  const selectedDepartment = event.target.value;

  departmentContents.forEach((content) => {
    if (content.id === `department-${selectedDepartment}`) {
      content.style.display = "block";
    } else {
      content.style.display = "none";
    }
  });
});
